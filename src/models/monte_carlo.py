"""
Monte Carlo option pricing implementation.

This module implements Monte Carlo Simulation for pricing options, 
especially useful for exotic options that don't have closed-form solutions.

"""
import numpy as np
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from .option import Option

@dataclass
class MonteCarloResult:
    price: float
    standard_error: float
    confidence_interval_95: Tuple[float, float]
    num_simulations: int
    simulation_time: float

class MonteCarloEngine:
    def __init__(self, random_seed: Optional[int] = None):
        if random_seed is not None:
            np.random.seed(random_seed)
    def _generate_stock_path(
            self,
            initial_price: float,
            drift: float,
            volatility: float,
            time_to_expiration: float,
            num_steps: int
    ) -> np.ndarray:
        """
        Generate a single stock price path using Geometric Brownian Motion.
        mathematical model followed in black scholes world:
        dS = mu * S * dt + sigma * S * dW
        Where:
        mu =  drift rate
        sigma = volatility
        dW = random Brownian motion
        """
        # time step size
        dt = time_to_expiration / num_steps

        # pre-calculate constants for efficiency (now includes dt in drift term)
        drift_term = (drift - 0.5 * volatility**2) * dt
        diffusion_term = volatility * math.sqrt(dt)

        # generate random normal variables
        random_shocks = np.random.normal(0, 1, num_steps)

        # calculate log price changes
        log_returns = drift_term + diffusion_term * random_shocks

        # convert to price path
        log_prices = np.log(initial_price) + np.cumsum(log_returns)
        stock_path = np.exp(log_prices)

        return np.concatenate([[initial_price], stock_path])
    
    def _calculate_european_payoff(
            self,
            option: Option,
            final_stock_price: float
    ) -> float:
        if option.is_call:
            return max(final_stock_price - option.strike_price, 0)
        else:
            return max(option.strike_price - final_stock_price, 0)
        
    def _calculate_asian_payoff(
            self,
            option: Option,
            stock_path: np.ndarray
    ) -> float:
        # calculate average stock price
        average_price = np.mean(stock_path)

        if option.is_call:
            return max(average_price - option.strike_price, 0)
        else:
            return max(option.strike_price - average_price, 0)
        
    def _calculate_barrier_payoff(
            self,
            option: Option,
            stock_path: np.ndarray,
            barrier_level: float,
            barrier_type: str = "knock_out" 
    ) -> float:
        
        # check if barrier was ever hit during the path
        if option.is_call:
            barrier_hit = np.any(stock_path >= barrier_level)
        else:
            barrier_hit = np.any(stock_path <= barrier_level)

        # calculate european payoff first
        final_price = stock_path[-1]
        european_payoff = self._calculate_european_payoff(option, final_price)
        
        # apply barrier logic
        if barrier_type == "knock_out":
            # Option becomes worthless if barrier is hit
            return 0.0 if barrier_hit else european_payoff
        elif barrier_type == "knock_in":
            # Option only has value if barrier is hit
            return european_payoff if barrier_hit else 0.0
        else:
            raise ValueError(f"Unknown barrier type: { barrier_type}")
        
    def price_european_option(
            self,
            option: Option,
            num_simulations: int = 10000,
            num_steps: int = 252
    ) -> MonteCarloResult:
        import time
        start_time = time.time()

        if option.volatility is None:
            raise ValueError("Volatility is required for Monte Carlo pricing")
        
        # Use risk-free rate as drift for risk neutral pricing
        drift = option.risk_free_rate

        payoffs = []

        # run simulations
        for _ in range(num_simulations):
            # Generate stock price path
            stock_path = self._generate_stock_path(
                initial_price=option.current_stock_price,
                drift=drift,
                volatility=option.volatility,
                time_to_expiration=option.time_to_expiration,
                num_steps=num_steps
            )

            # calculate payoff for this path
            final_price = stock_path[-1]
            payoff = self._calculate_european_payoff(option, final_price)
            payoffs.append(payoff)
        
        # Convert to numpy array for calculations
        payoffs = np.array(payoffs)
        # discount back to present value
        discount_factor = math.exp(-option.risk_free_rate * option.time_to_expiration)
        discounted_payoffs = payoffs * discount_factor

        # Calculate statistics
        price = np.mean(discounted_payoffs)
        standard_error = np.std(discounted_payoffs) / math.sqrt(num_simulations)

        # 95% confidence interval
        confidence_margin = 1.96 * standard_error
        confidence_interval = (price - confidence_margin, price + confidence_margin)

        simulation_time = time.time() - start_time

        return MonteCarloResult(
            price=price,
            standard_error=standard_error,
            confidence_interval_95=confidence_interval,
            num_simulations=num_simulations,
            simulation_time=simulation_time
        )
    
    def price_asian_option(
            self,
            option: Option,
            num_simulations: int = 10000,
            num_steps: int = 252
    ) -> MonteCarloResult:
        
        import time
        start_time = time.time()

        if option.volatility is None:
            raise ValueError("Volatility is required for Monte carlo pricing")
        
        drift = option.risk_free_rate
        payoffs = []

        for _ in range(num_simulations):
            stock_path = self._generate_stock_path(
                initial_price=option.current_stock_price,
                drift=drift,
                volatility=option.volatility,
                time_to_expiration=option.time_to_expiration,
                num_steps=num_steps
            )

            payoff = self._calculate_asian_payoff(option, stock_path)
            payoffs.append(payoff)
        
        payoffs = np.array(payoffs)
        discount_factor = math.exp(-option.risk_free_rate * option.time_to_expiration)
        discounted_payoffs = payoffs * discount_factor

        # Calculate statistics
        price = np.mean(discounted_payoffs)
        standard_error = np.std(discounted_payoffs) / math.sqrt(num_simulations)
        confidence_margin = 1.96 * standard_error
        confidence_interval = (price - confidence_margin, price + confidence_margin)

        simulation_time = time.time() - start_time

        return MonteCarloResult(
            price=price,
            standard_error=standard_error,
            confidence_interval_95=confidence_interval,
            num_simulations=num_simulations,
            simulation_time=simulation_time
        )
    
    def price_barrier_option(
            self,
            option: Option,
            barrier_level: float,
            barrier_type: str = "knock_out",
            num_simulations: int = 10000,
            num_steps: int = 252
    ) -> MonteCarloResult:
        import time
        start_time = time.time()
        if option.volatility is None:
            raise ValueError("Volatility is required for Monte carlo pricing")
        
        drift = option.risk_free_rate
        payoffs = []

        for _ in range(num_simulations):
            stock_path = self._generate_stock_path(
                initial_price=option.current_stock_price,
                drift=drift,
                volatility=option.volatility,
                time_to_expiration=option.time_to_expiration,
                num_steps=num_steps               
            )

            payoff = self._calculate_barrier_payoff(
                option, stock_path, barrier_level, barrier_type
            )
            payoffs.append(payoff)

        payoffs = np.array(payoffs)
        discount_factor =  math.exp(-option.risk_free_rate * option.time_to_expiration)
        discounted_payoffs = payoffs * discount_factor

        price = np.mean(discounted_payoffs)
        standard_error = np.std(discounted_payoffs) / math.sqrt(num_simulations)
        confidence_margin = 1.96 * standard_error
        confidence_interval = (price - confidence_margin, price + confidence_margin)

        simulation_time = time.time() - start_time

        return MonteCarloResult(
            price=price,
            standard_error=standard_error,
            confidence_interval_95=confidence_interval,
            num_simulations=num_simulations,
            simulation_time=simulation_time
        )
    

    # Utility function for analysis
    def compare_methods(option: Option, num_simulations: int = 50000) -> dict:
        """
        Compare Blach-Scholes vs Monte Carlo for european options"""
        from .black_scholes import BlackScholesEngine

        # price with Black_Scholes (analytical)
        bs_price = BlackScholesEngine.price_option(option)

        # price monte carlo (numerical)
        mc_engine = MonteCarloEngine(random_seed=42)
        mc_result = mc_engine.price_european_option(option, num_simulations)

        return {
            'black_scholes_price': bs_price,
            'monte_carlo_price': mc_result.price,
            'difference': abs(bs_price-mc_result.price),
            'relative_error': abs(bs_price - mc_result.price) / bs_price * 100,
            'monte_carlo_std_error': mc_result.standard_error,
            'confidence_interval': mc_result.confidence_interval_95,
            'simulation_time': mc_result.simulation_time,
            'num_simulations': num_simulations
        }

