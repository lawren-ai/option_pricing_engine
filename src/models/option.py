from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

@dataclass
class Option:
    # Contract specifications 
    symbol: str
    strike_price: float
    expiration_date: datetime
    option_type: OptionType
    
    # Market data (these change constantly in real trading)
    current_stock_price: float
    risk_free_rate: float
    volatility: Optional[float] = None
    
    def __post_init__(self):
        if self.strike_price <= 0:
            raise ValueError(f"Strike price must be positive, got {self.strike_price}")
        
        if self.current_stock_price <= 0:
            raise ValueError(f"Current stock price must be positive, got {self.current_stock_price}")
            
        if self.risk_free_rate < 0:
            raise ValueError(f"Risk-free rate cannot be negative, got {self.risk_free_rate}")
            
        if self.expiration_date <= datetime.now():
            raise ValueError("Option must have future expiration date")
            
        if self.volatility is not None and self.volatility <= 0:
            raise ValueError(f"Volatility must be positive, got {self.volatility}")
    
    @property
    def time_to_expiration(self) -> float:
        # Use total_seconds() for more precise calculation than just days
        time_delta = self.expiration_date - datetime.now()
        total_seconds = time_delta.total_seconds()
        
        # Convert seconds to years
        seconds_per_year = 365.25 * 24 * 3600  # Account for leap years
        years_remaining = total_seconds / seconds_per_year
        
        # Handle edge cases:
        # - If expired, return 0
        # - If very close to expiration, return minimum 1 day to avoid division by zero
        if years_remaining <= 0:
            return 0.0
        elif years_remaining < (1.0 / 365.25):  # Less than 1 day
            return 1.0 / 365.25  # Return exactly 1 day
            
        return years_remaining
    
    @property
    def is_call(self) -> bool:
        """Check if this is a call option"""
        return self.option_type == OptionType.CALL
    
    @property
    def is_put(self) -> bool:
        """Check if this is a put option"""
        return self.option_type == OptionType.PUT
        
    @property
    def is_in_the_money(self) -> bool:
        """
        Check if option is currently profitable to exercise.
        
        For calls: stock price > strike price
        For puts: stock price < strike price
        """
        if self.is_call:
            return self.current_stock_price > self.strike_price
        else:
            return self.current_stock_price < self.strike_price
    
    @property
    def intrinsic_value(self) -> float:
        """
        Calculate the intrinsic value of the option.
        
        This is what the option would be worth if exercised immediately.
        Options never trade below their intrinsic value.
        
        Returns:
            Intrinsic value in dollars
        """
        if self.is_call:
            return max(self.current_stock_price - self.strike_price, 0)
        else:
            return max(self.strike_price - self.current_stock_price, 0)
    
    def __str__(self) -> str:
        """
        Human-readable string representation.
        
        Useful for:
        - Logging and debugging
        - Display in user interfaces
        - Error messages
        """
        return (
            f"{self.symbol} ${self.strike_price} {self.option_type.value.upper()} "
            f"exp: {self.expiration_date.strftime('%Y-%m-%d')}"
        )
    
    def __repr__(self) -> str:
        """
        Developer-friendly representation that could recreate the object.
        
        Useful when debugging in Python REPL or debugger.
        """
        return (
            f"Option(symbol='{self.symbol}', "
            f"strike_price={self.strike_price}, "
            f"option_type={self.option_type}, "
            f"current_stock_price={self.current_stock_price}, "
            f"expiration_date=datetime({self.expiration_date.year}, "
            f"{self.expiration_date.month}, {self.expiration_date.day}))"
        )