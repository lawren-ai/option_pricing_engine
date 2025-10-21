import math
import numpy as np
from scipy.stats import norm
from dataclasses import dataclass
from typing import Optional, Callable, Dict
from .option import Option

@dataclass
class GreeksResult:
    """Cotainer for all greek values
    """
    delta: float  # change per 1$ stock move
    gamma: float  #chnage in delta per 1$ stock move
    vega: float  #Change per 1% volatility increase
    theta: float  # value lost per day (usually negative)
    rho: float    # change per 1% interest rate increase

    def __str__(self) -> str:
        """Human-readable greeks summary"""
        return (
            f"Greeks:\n"
            f"  Delta: {self.delta:+.4f} (stock sensitivity)\n"
            f"  Gamma: {self.gamma:+.4f} (delta curvature)\n"
            f"  Vega:  {self.vega:+.4f} (volatility sensitivity)\n"
            f"  Theta: {self.theta:+.4f} (time decay per day)\n"
            f"  Rho:   {self.rho:+.4f} (rate sensitivity)\n"
        )
    
class GreeksCalculator:
    """Calculate greeks using analytical and numerical methoods"""
    @staticmethod
    def _calculate_d1_d2(
        stock_price: float,
        strike_price: float,
        risk_free_rate: float,
        volatility: float,
        time_to_expiration: float
    ) -> tuple:
        """Calculate d1 and d2 for Black-Scholes formula"""
        d1 = (math.log(stock_price / strike_price) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiration) / (volatility * math.sqrt(time_to_expiration))
        d2 = d1 - volatility * math.sqrt(time_to_expiration)
        return d1, d2
    
    @classmethod
    def calculate_analytical_greeks(
        cls,
        option: Option
    ) -> GreeksResult:
        """Claculate greeks using Black-Scholes formula"""
        if option.volatility is None:
                raise ValueError("Volatility is required for analytical greeks calculation")
        
        if option.time_to_expiration <= 0:
            #   Expired options have zero greeks except delta
            delta = 1.0 if (option.is_call and option.is_in_the_money) else 0.0
            delta = -1.0 if (option.is_put and option.is_in_the_money) else delta

            return GreeksResult(
                delta=delta,
                gamma=0.0,
                vega=0.0,
                theta=0.0,
                rho=0.0
            )
        
        #   extract parameters
        S = option.current_stock_price
        K = option.strike_price
        r = option.risk_free_rate
        sigma = option.volatility
        T = option.time_to_expiration
        d1, d2 = cls._calculate_d1_d2(S, K, r, sigma, T)

        # standard normal pdf and cdf
        pdf_d1 = norm.pdf(d1)
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)

        # delta: dv/ds
        # call: 0 to 1, put: -1 to 0
        if option.is_call:
            delta = cdf_d1
        else:
            delta = cdf_d1 - 1

        # gamma: d²v/ds² (same for calls and puts)
        gamma = pdf_d1 / (S * sigma * math.sqrt(T))

        # vega: dv/dσ
        vega = S * pdf_d1 * math.sqrt(T) / 100  # per 1% vol change

        # theta: dv/dt (per day)
        if option.is_call:
            term1 = -(S * pdf_d1 * sigma) / (2 * math.sqrt(T))
            term2 = -r * K * math.exp(-r * T) * cdf_d2
            theta = (term1 + term2) / 365
        else:
            term1 = -(S * pdf_d1 * sigma) / (2 * math.sqrt(T))
            term2 = r * K * math.exp(-r * T) * norm.cdf(-d2)
            theta = (term1 + term2) / 365


        # rho: dv/dr (per 1% rate change)
        if option.is_call:
            rho = K * T * math.exp(-r * T) * cdf_d2 / 100
        else:
            rho = -K * T * math.exp(-r * T) * norm.cdf(-d2) / 100

        return GreeksResult(
            delta=delta,
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho=rho
        )
    
    @staticmethod
    def calculate_numerical_greeks(
        pricer_func: Callable[[Option], float],
        option: Option,
        delta_bump: float = 0.01,
        vega_bump: float = 0.001,
        theta_days: float = 1.0,
        rho_bump: float = 0.0001
    ) -> GreeksResult:
        """Calculate greeks using finite difference method"""
        import copy
        from datetime import timedelta

        # base price
        base_price = pricer_func(option)

        # delta: (V(S + dS) - V(S - dS)) / (2 * dS)
        # central difference for better accuracy
        option_up = copy.deepcopy(option)
        option_up.current_stock_price += delta_bump
        option_down = copy.deepcopy(option)
        option_down.current_stock_price -= delta_bump


        price_up = pricer_func(option_up)
        price_down = pricer_func(option_down)
        delta = (price_up - price_down) / (2 * delta_bump)

        #gamma: (V(S + dS) - 2V(S) + V(S - dS)) / (dS²)
        gamma = (price_up - 2 * base_price + price_down) / (delta_bump ** 2)    
        # vega: (V(σ + dσ) - V(σ - dσ)) / (2 * dσ)
        # sensitivity to volatility changes
        if option.volatility is not None:
            option_vega_up = copy.deepcopy(option)
            option_vega_up.volatility += vega_bump
            option_vega_down = copy.deepcopy(option)
            option_vega_down.volatility -= vega_bump
            option_vega_down.volatility = max(0.001, option.volatility - vega_bump)

            price_vega_up = pricer_func(option_vega_up)
            price_vega_down = pricer_func(option_vega_down)
            vega = (price_vega_up - price_vega_down) / (2 * vega_bump)
        else:
            vega = 0.0
        
        # theta: (V(t) - V(t + dT)) / dT
        # forward difference since time only moves forward
        option_theta = copy.deepcopy(option)
        option_theta.expiration_date -= timedelta(days=theta_days)

        if option_theta.time_to_expiration > 0:
            price_theta = pricer_func(option_theta)
            theta = (price_theta - base_price) / theta_days

        else:
            theta = 0.0

        # rho: (V(r + dr) - V(r - dr)) / (2 * dr)
        option_rho_up = copy.deepcopy(option)
        option_rho_up.risk_free_rate += rho_bump
        option_rho_down = copy.deepcopy(option)
        option_rho_down.risk_free_rate = max(0.0, option.risk_free_rate - rho_bump )

        price_rho_up = pricer_func(option_rho_up)
        price_rho_down = pricer_func(option_rho_down)
        rho = (price_rho_up - price_rho_down) / (2 * rho_bump) / 100

        return GreeksResult(
            delta=delta,
            gamma=gamma,
            vega=vega,
            theta=theta,
            rho=rho
        ) 
    
def interpret_greeks(greeks: GreeksResult, option: Option) -> str:
    """Generate human-readable interpretation of greeks"""
    S = option.current_stock_price
    
    interpretation = []
    interpretation.append("=" * 60)
    interpretation.append("GREEKS INTERPRETATION")
    interpretation.append("=" * 60)
    
    # Delta interpretation
    interpretation.append(f"\n DELTA: {greeks.delta:+.4f}")
    if option.is_call:
        interpretation.append(f"   • If stock moves $1 up: option gains ${greeks.delta:.2f}")
        interpretation.append(f"   • If stock moves $1 down: option loses ${abs(greeks.delta):.2f}")
        interpretation.append(f"   • Acts like owning {greeks.delta:.2f} shares of stock")
    else:
        interpretation.append(f"   • If stock moves $1 up: option loses ${abs(greeks.delta):.2f}")
        interpretation.append(f"   • If stock moves $1 down: option gains ${greeks.delta:.2f}")
        interpretation.append(f"   • Acts like shorting {abs(greeks.delta):.2f} shares of stock")
    
    # Gamma interpretation
    interpretation.append(f"\n GAMMA: {greeks.gamma:+.6f}")
    interpretation.append(f"   • Delta changes by {greeks.gamma:.4f} for each $1 stock move")
    if greeks.gamma > 0.01:
        interpretation.append(f"   • HIGH gamma: Delta is very sensitive to stock price")
        interpretation.append(f"   • Need frequent rehedging")
    else:
        interpretation.append(f"   • LOW gamma: Delta is relatively stable")
    
    # Vega interpretation
    interpretation.append(f"\n VEGA: {greeks.vega:+.4f}")
    interpretation.append(f"   • If volatility increases 1%: option gains ${greeks.vega:.2f}")
    interpretation.append(f"   • If volatility decreases 1%: option loses ${abs(greeks.vega):.2f}")
    if greeks.vega > 5:
        interpretation.append(f"   • HIGH vega: Very sensitive to volatility changes")
        interpretation.append(f"   • Consider volatility hedging")
    
    # Theta interpretation
    interpretation.append(f"\n THETA: {greeks.theta:+.4f}")
    interpretation.append(f"   • Option loses ${abs(greeks.theta):.2f} per day from time decay")
    interpretation.append(f"   • Over one week: loses ${abs(greeks.theta) * 7:.2f}")
    interpretation.append(f"   • Over one month: loses ${abs(greeks.theta) * 30:.2f}")
    if greeks.theta < -0.10:
        interpretation.append(f"   • HIGH theta decay: Significant daily value loss")
        interpretation.append(f"   • Time is working against this position")
    
    # Rho interpretation
    interpretation.append(f"\n RHO: {greeks.rho:+.4f}")
    interpretation.append(f"   • If interest rates increase 1%: option {'gains' if greeks.rho > 0 else 'loses'} ${abs(greeks.rho):.2f}")
    if abs(greeks.rho) < 1:
        interpretation.append(f"   • LOW rho: Not very sensitive to rate changes")
    
    return "\n".join(interpretation)
        