
import math
from typing import Tuple
from scipy.stats import norm
from .option import Option

class BlackScholesEngine:
    @staticmethod
    def _calculate_d1_d2(
        stock_price: float,
        strike_price: float, 
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float
    ) -> Tuple[float, float]:
        """
        Calculate d1 and d2
        d1 = [ln(S/K) + (r + σ²/2) * T] / (σ * √T)
        d2 = d1 - σ * √T
        """
        # validate inputs
        if time_to_expiration <= 0:
            raise ValueError(f"Time to expiration must be positive, got {time_to_expiration}")
            
        if volatility <= 0:
            raise ValueError(f"Volatility must be positive, got {volatility}")
            
        if stock_price <= 0:
            raise ValueError(f"Stock price must be positive, got {stock_price}")
            
        if strike_price <= 0:
            raise ValueError(f"Strike price must be positive, got {strike_price}")
        
        # Calculate d1
        d1 = (
            math.log(stock_price / strike_price) + 
            (risk_free_rate + 0.5 * volatility**2) * time_to_expiration
        ) / (volatility * math.sqrt(time_to_expiration))
        
        # Calculate d2
        d2 = d1 - volatility * math.sqrt(time_to_expiration)
        
        return d1, d2
    
    @classmethod
    def calculate_call_price(
        cls,
        stock_price: float,
        strike_price: float,
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float
    ) -> float:
        """
        Calculate call option price using Black-Scholes formula.
        
        Formula: C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)
        """
        # Get the d1 and d2 values
        d1, d2 = cls._calculate_d1_d2(
            stock_price, strike_price, time_to_expiration, 
            risk_free_rate, volatility
        )
        
        # N(d1) and N(d2) are probabilities from the normal distribution
        n_d1 = norm.cdf(d1)  # Cumulative distribution function
        n_d2 = norm.cdf(d2)
        
        # Apply the Black-Scholes call formula
        call_price = (
            stock_price * n_d1 -  
            strike_price * math.exp(-risk_free_rate * time_to_expiration) * n_d2
            )
        
        # Options can never have negative value
        return max(call_price, 0.0)
    
    @classmethod 
    def calculate_put_price(
        cls,
        stock_price: float,
        strike_price: float, 
        time_to_expiration: float,
        risk_free_rate: float,
        volatility: float
    ) -> float:
        """
        Calculate put option price using Black-Scholes formula.
        
        Formula: P = K × e^(-rT) × N(-d₂) - S₀ × N(-d₁)
        """
        # Same d1, d2 calculation as for calls
        d1, d2 = cls._calculate_d1_d2(
            stock_price, strike_price, time_to_expiration,
            risk_free_rate, volatility
        )
        
        # For puts, use the negative values: N(-d1) and N(-d2)
        n_minus_d1 = norm.cdf(-d1)
        n_minus_d2 = norm.cdf(-d2)
        
        # Apply the Black-Scholes put formula
        put_price = (
            strike_price * math.exp(-risk_free_rate * time_to_expiration) * n_minus_d2 -
            stock_price * n_minus_d1
        )
        
        # Options can never have negative value
        return max(put_price, 0.0)
    
    @classmethod
    def price_option(cls, option: Option) -> float:
        # check for volatility
        if option.volatility is None:
            raise ValueError(
                f"Volatility is required for Black-Scholes pricing. "
                f"Option: {option}"
            )
        
        # Route to appropriate pricing method based on option type
        if option.is_call:
            return cls.calculate_call_price(
                stock_price=option.current_stock_price,
                strike_price=option.strike_price,
                time_to_expiration=option.time_to_expiration,
                risk_free_rate=option.risk_free_rate,
                volatility=option.volatility
            )
        else:  
            return cls.calculate_put_price(
                stock_price=option.current_stock_price,
                strike_price=option.strike_price, 
                time_to_expiration=option.time_to_expiration,
                risk_free_rate=option.risk_free_rate,
                volatility=option.volatility
            )
    
    @classmethod
    def calculate_implied_volatility(
        cls,
        option: Option,
        market_price: float,
        tolerance: float = 0.0001,
        max_iterations: int = 100
    ) -> float:
        """
        Calculate implied volatility using Newton-Raphson method.
        
        Implied volatility is the volatility that makes the Black-Scholes
        price equal to the observed market price. It's what the market
        "thinks" the volatility should be.
        
        This is advanced functionality - we'll implement this later!
        
        Args:
            option: Option to calculate implied volatility for
            market_price: Observed market price of the option
            tolerance: Convergence tolerance for the algorithm
            max_iterations: Maximum iterations before giving up
            
        Returns:
            Implied volatility as a decimal (0.25 = 25%)
            
        Note: This is a placeholder for now - we'll implement this
        when we cover advanced features!
        """
        # TODO: Implement Newton-Raphson method for implied volatility
        # This is complex and we'll cover it in advanced topics
        raise NotImplementedError(
            "Implied volatility calculation will be implemented "
            "in the advanced features module"
        )