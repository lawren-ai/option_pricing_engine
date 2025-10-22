# src/data/market_data.py

"""
Live Market Data Integration

Fetches real-time stock prices, options chains, and implied volatility
from Yahoo Finance and other sources.

Usage:
    from src.data.market_data import MarketDataFetcher
    
    fetcher = MarketDataFetcher()
    price = fetcher.get_stock_price("AAPL")
    volatility = fetcher.get_historical_volatility("AAPL", days=30)
"""

import yfinance as yf
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import warnings
warnings.filterwarnings('ignore')

class MarketDataFetcher:
    """
    Fetches real market data for option pricing.
    
    This class integrates with Yahoo Finance to get:
    - Real-time stock prices
    - Historical price data
    - Implied volatility
    - Options chains
    - Risk-free rates (using Treasury yields)
    """
    
    def __init__(self):
        """Initialize the market data fetcher"""
        self.cache = {}  # Simple caching to avoid repeated API calls
    
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """
        Get current stock price.
        
        Args:
            symbol: Stock ticker (e.g., "AAPL", "MSFT")
            
        Returns:
            Current stock price or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if data.empty:
                print(f"⚠️  No data found for {symbol}")
                return None
            
            current_price = data['Close'].iloc[-1]
            print(f"📈 {symbol}: ${current_price:.2f}")
            return float(current_price)
            
        except Exception as e:
            print(f"❌ Error fetching price for {symbol}: {e}")
            return None
    
    def get_historical_volatility(
        self, 
        symbol: str, 
        days: int = 30
    ) -> Optional[float]:
        """
        Calculate historical volatility from past price movements.
        
        Historical volatility = annualized standard deviation of log returns.
        This is what traders use when implied volatility isn't available.
        
        Args:
            symbol: Stock ticker
            days: Lookback period for volatility calculation
            
        Returns:
            Annualized volatility (e.g., 0.25 = 25% vol)
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days*2)  # Get extra data
            hist = ticker.history(start=start_date, end=end_date)
            
            if len(hist) < days:
                print(f"⚠️  Insufficient data for {symbol}")
                return None
            
            # Calculate log returns
            log_returns = np.log(hist['Close'] / hist['Close'].shift(1))
            
            # Calculate volatility
            daily_vol = log_returns.std()
            annual_vol = daily_vol * np.sqrt(252)  # 252 trading days/year
            
            print(f"📊 {symbol} Historical Volatility ({days}d): {annual_vol:.2%}")
            return float(annual_vol)
            
        except Exception as e:
            print(f"❌ Error calculating volatility for {symbol}: {e}")
            return None
    
    def get_options_chain(
        self, 
        symbol: str, 
        expiration_date: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get options chain data from Yahoo Finance.
        
        Returns real market prices for call and put options.
        Perfect for comparing your pricing model against market!
        
        Args:
            symbol: Stock ticker
            expiration_date: Optional specific expiration date (YYYY-MM-DD)
            
        Returns:
            Dictionary with calls and puts DataFrames
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            expirations = ticker.options
            if not expirations:
                print(f"⚠️  No options data for {symbol}")
                return None
            
            # Use specified or nearest expiration
            if expiration_date and expiration_date in expirations:
                exp_date = expiration_date
            else:
                exp_date = expirations[0]  # Nearest expiration
            
            # Get options chain
            opt_chain = ticker.option_chain(exp_date)
            
            print(f"📋 Options Chain for {symbol} (expires {exp_date}):")
            print(f"   • {len(opt_chain.calls)} calls available")
            print(f"   • {len(opt_chain.puts)} puts available")
            
            return {
                'expiration': exp_date,
                'calls': opt_chain.calls,
                'puts': opt_chain.puts,
                'available_expirations': expirations
            }
            
        except Exception as e:
            print(f"❌ Error fetching options chain for {symbol}: {e}")
            return None
    
    def get_risk_free_rate(self) -> float:
        """
        Get current risk-free rate from 3-month Treasury yield.
        
        In production, this would fetch from Fed API or Bloomberg.
        For now, we'll use a reasonable estimate.
        
        Returns:
            Risk-free rate as decimal (e.g., 0.05 = 5%)
        """
        try:
            # Fetch 3-month Treasury yield (^IRX)
            treasury = yf.Ticker("^IRX")
            data = treasury.history(period="1d")
            
            if not data.empty:
                rate = data['Close'].iloc[-1] / 100  # Convert to decimal
                print(f"💰 Risk-free rate (3M Treasury): {rate:.2%}")
                return float(rate)
            else:
                # Fallback to reasonable estimate
                print("⚠️  Using default risk-free rate: 5.00%")
                return 0.05
                
        except Exception as e:
            print(f"⚠️  Using default risk-free rate: 5.00%")
            return 0.05
    
    def get_implied_volatility_from_chain(
        self, 
        symbol: str, 
        option_type: str = "call",
        strike_price: Optional[float] = None
    ) -> Optional[float]:
        """
        Extract implied volatility from options chain.
        
        This gets the market's expectation of future volatility,
        which is what's priced into actual options.
        
        Args:
            symbol: Stock ticker
            option_type: "call" or "put"
            strike_price: Specific strike, or ATM if None
            
        Returns:
            Implied volatility from options market
        """
        try:
            chain = self.get_options_chain(symbol)
            if not chain:
                return None
            
            # Get current stock price
            current_price = self.get_stock_price(symbol)
            if not current_price:
                return None
            
            # Select calls or puts
            options = chain['calls'] if option_type.lower() == 'call' else chain['puts']
            
            # Find ATM or specific strike
            if strike_price:
                option = options[options['strike'] == strike_price]
            else:
                # Find closest to ATM
                options['distance'] = abs(options['strike'] - current_price)
                option = options.nsmallest(1, 'distance')
            
            if option.empty:
                print(f"⚠️  No option found at strike {strike_price}")
                return None
            
            # Get implied volatility
            iv = option['impliedVolatility'].iloc[0]
            
            if iv > 0:
                print(f"📊 Implied Volatility ({option_type} @ ${option['strike'].iloc[0]}): {iv:.2%}")
                return float(iv)
            else:
                print(f"⚠️  No implied volatility available")
                return None
                
        except Exception as e:
            print(f"❌ Error getting implied volatility: {e}")
            return None
    
    def create_option_from_market_data(
        self,
        symbol: str,
        strike_price: float,
        days_to_expiration: int,
        option_type: str = "call",
        use_implied_vol: bool = True
    ) -> Optional[Dict]:
        """
        Create option parameters using real market data.
        
        This is the magic function that combines everything!
        Perfect for creating realistic test cases.
        
        Args:
            symbol: Stock ticker
            strike_price: Strike price
            days_to_expiration: Days until expiration
            option_type: "call" or "put"
            use_implied_vol: Use market IV if True, else historical
            
        Returns:
            Dictionary with all option parameters
        """
        try:
            print(f"\n🔍 Fetching market data for {symbol}...")
            
            # Get stock price
            stock_price = self.get_stock_price(symbol)
            if not stock_price:
                return None
            
            # Get volatility
            if use_implied_vol:
                volatility = self.get_implied_volatility_from_chain(
                    symbol, option_type, strike_price
                )
                if volatility is None:
                    print("📊 Falling back to historical volatility...")
                    volatility = self.get_historical_volatility(symbol, days=30)
            else:
                volatility = self.get_historical_volatility(symbol, days=30)
            
            if volatility is None:
                print("⚠️  Using default volatility: 25%")
                volatility = 0.25
            
            # Get risk-free rate
            risk_free_rate = self.get_risk_free_rate()
            
            # Create expiration date
            expiration_date = datetime.now() + timedelta(days=days_to_expiration)
            
            print(f"\n✅ Market data fetched successfully!")
            
            return {
                'symbol': symbol,
                'strike_price': strike_price,
                'stock_price': stock_price,
                'expiration_date': expiration_date,
                'days_to_expiration': days_to_expiration,
                'option_type': option_type,
                'volatility': volatility,
                'risk_free_rate': risk_free_rate,
                'data_source': 'yahoo_finance',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error creating option from market data: {e}")
            return None
    
    def compare_model_vs_market(
        self,
        symbol: str,
        expiration_index: int = 0
    ) -> Optional[pd.DataFrame]:
        """
        Compare your pricing model against real market prices.
        
        This is GOLD for validating your model!
        Shows where your prices match the market and where they differ.
        
        Args:
            symbol: Stock ticker
            expiration_index: Which expiration to use (0 = nearest)
            
        Returns:
            DataFrame comparing model prices vs market prices
        """
        try:
            from ..models.option import Option, OptionType
            from ..models.black_scholes import BlackScholesEngine
            
            print(f"\n🔬 Comparing model vs market for {symbol}...")
            
            # Get options chain
            chain = self.get_options_chain(symbol)
            if not chain:
                return None
            
            # Get current price and volatility
            stock_price = self.get_stock_price(symbol)
            volatility = self.get_historical_volatility(symbol, days=30)
            risk_free_rate = self.get_risk_free_rate()
            
            if not all([stock_price, volatility]):
                return None
            
            # Calculate days to expiration
            exp_date = datetime.strptime(chain['expiration'], '%Y-%m-%d')
            days_to_exp = (exp_date - datetime.now()).days
            
            # Get calls data
            calls = chain['calls'].copy()
            
            # Price each option with our model
            model_prices = []
            for _, row in calls.iterrows():
                try:
                    option = Option(
                        symbol=symbol,
                        strike_price=row['strike'],
                        expiration_date=exp_date,
                        option_type=OptionType.CALL,
                        current_stock_price=stock_price,
                        risk_free_rate=risk_free_rate,
                        volatility=volatility
                    )
                    
                    model_price = BlackScholesEngine.price_option(option)
                    model_prices.append(model_price)
                except:
                    model_prices.append(np.nan)
            
            # Create comparison DataFrame
            comparison = pd.DataFrame({
                'Strike': calls['strike'],
                'Market_Bid': calls['bid'],
                'Market_Ask': calls['ask'],
                'Market_Last': calls['lastPrice'],
                'Market_Mid': (calls['bid'] + calls['ask']) / 2,
                'Model_Price': model_prices,
                'Difference': [m - market if not np.isnan(m) else np.nan 
                              for m, market in zip(model_prices, (calls['bid'] + calls['ask']) / 2)],
                'Volume': calls['volume'],
                'Open_Interest': calls['openInterest']
            })
            
            # Calculate error metrics
            comparison['Pct_Error'] = (
                (comparison['Model_Price'] - comparison['Market_Mid']) / 
                comparison['Market_Mid'] * 100
            )
            
            # Filter out illiquid options
            comparison = comparison[comparison['Volume'] > 0]
            
            print(f"\n📊 Comparison Results:")
            print(f"   • Options analyzed: {len(comparison)}")
            print(f"   • Mean absolute error: ${comparison['Difference'].abs().mean():.2f}")
            print(f"   • Mean % error: {comparison['Pct_Error'].abs().mean():.2f}%")
            
            return comparison
            
        except Exception as e:
            print(f"❌ Error comparing model vs market: {e}")
            import traceback
            traceback.print_exc()
            return None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def fetch_live_option_data(symbol: str, strike: float, days: int):
    """
    Quick helper to fetch live data for an option.
    
    Usage:
        data = fetch_live_option_data("AAPL", 150, 30)
        print(data)
    """
    fetcher = MarketDataFetcher()
    return fetcher.create_option_from_market_data(
        symbol, strike, days, "call", use_implied_vol=True
    )

def get_popular_tickers() -> List[str]:
    """
    Returns list of liquid stocks good for testing.
    These have active options markets with tight spreads.
    """
    return [
        # Tech giants
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        # Finance
        "JPM", "BAC", "GS", "WFC",
        # ETFs (very liquid)
        "SPY", "QQQ", "IWM",
        # Others
        "DIS", "NFLX", "AMD", "INTC"
    ]


# ============================================================================
# DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("📊 LIVE MARKET DATA INTEGRATION DEMO")
    print("=" * 70)
    
    fetcher = MarketDataFetcher()
    
    # Example 1: Get current stock price
    print("\n1️⃣ Fetching Stock Price:")
    price = fetcher.get_stock_price("AAPL")
    
    # Example 2: Calculate historical volatility
    print("\n2️⃣ Calculating Historical Volatility:")
    vol = fetcher.get_historical_volatility("AAPL", days=30)
    
    # Example 3: Get options chain
    print("\n3️⃣ Fetching Options Chain:")
    chain = fetcher.get_options_chain("AAPL")
    
    if chain:
        print(f"\n   Sample call options:")
        print(chain['calls'][['strike', 'lastPrice', 'bid', 'ask', 'volume', 'impliedVolatility']].head())
    
    # Example 4: Create option with real market data
    print("\n4️⃣ Creating Option with Live Data:")
    option_data = fetcher.create_option_from_market_data(
        symbol="AAPL",
        strike_price=150,
        days_to_expiration=30,
        option_type="call",
        use_implied_vol=True
    )
    
    if option_data:
        print("\n   Option Parameters:")
        for key, value in option_data.items():
            if key != 'expiration_date':
                print(f"   • {key}: {value}")
    
    # Example 5: Compare model vs market
    print("\n5️⃣ Comparing Model vs Market Prices:")
    comparison = fetcher.compare_model_vs_market("AAPL")
    
    if comparison is not None and not comparison.empty:
        print("\n   Top 5 ATM options:")
        print(comparison.head().to_string(index=False))
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE!")
    print("=" * 70)