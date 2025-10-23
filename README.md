# Options Pricing Engine 🚀

> A production-grade quantitative finance system with REST API for options pricing, risk management, and real-time market analysis.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Live Data](https://img.shields.io/badge/market%20data-live-green)](https://github.com/lawren-ai/option_pricing_engine)

## 🎯 Project Overview

This project implements a production-ready options pricing and risk management system with a REST API. It combines mathematical pricing models with real-time market data integration, making it suitable for both learning and real-world trading applications.

**Key Features:**
- Black-Scholes analytical pricing
- Monte Carlo simulation for exotic options
- Complete Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- Real-time market data integration via Yahoo Finance
- REST API with comprehensive documentation
- Portfolio analysis and risk management

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main demo
python main.py

# Try live market data
python demos/live_market_demo.py

# Start the REST API
python api/app.py
```

**See it in action:** Visit `http://localhost:5000/docs` for interactive API documentation.

---

## ✨ Features

### Pricing Models
- Black-Scholes analytical pricing (microsecond-level speed)
- Monte Carlo simulation for complex derivatives
- Support for European, Asian, and Barrier options
- Handles edge cases (zero rates, extreme volatility)

### Risk Analytics
- Complete Greeks calculation (Δ, Γ, Θ, ν, ρ)
- Portfolio-level risk aggregation
- Volatility smile/skew analysis
- Real-time risk monitoring

### Market Integration
- Live stock price feeds via Yahoo Finance
- Options chain data with bid/ask spreads
- Historical and implied volatility calculations
- Real-time market validation

### REST API
- Comprehensive API documentation
- JSON request/response format
- Rate limiting and error handling
- CORS support for web clients

### Production Features
- Robust error handling
- Performance optimization
- Comprehensive validation
- Unit test coverage

---

## 🏗️ Architecture

```
option_pricing_engine/
├── api/                 # REST API implementation
│   ├── app.py          # Flask application
│   └── test_api.py     # API test suite
├── src/
│   ├── models/         # Core pricing models
│   │   ├── black_scholes.py
│   │   ├── monte_carlo.py
│   │   ├── greeks.py
│   │   └── option.py
│   └── data/          # Market data integration
│       └── market_data.py
├── demos/             # Demonstration scripts
│   ├── live_market_demo.py
│   ├── monte_carlo_demo.py
│   └── greeks_demo.py
├── images/           # Visualizations
├── tests/            # Unit tests
└── requirements.txt  # Dependencies
```

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/lawren-ai/option_pricing_engine.git
cd option_pricing_engine

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

---

## 💻 Usage

### Starting the API Server

```bash
python api/app.py
```

The server will start at `http://localhost:5000`. Visit `http://localhost:5000/docs` for interactive API documentation.

### Example API Request

```bash
curl -X POST "http://localhost:5000/api/greeks" \
     -H "Content-Type: application/json" \
     -d '{
       "symbol": "MSFT",
       "strike_price": 200,
       "days_to_expiration": 90,
       "option_type": "call",
       "stock_price": 195,
       "volatility": 0.25,
       "risk_free_rate": 0.05
     }'
```

### Python Usage

```python
from datetime import datetime, timedelta
from src.models.option import Option, OptionType
from src.models.black_scholes import BlackScholesEngine
from src.models.greeks import GreeksCalculator

# Create an option
option = Option(
    symbol="AAPL",
    strike_price=150.0,
    expiration_date=datetime.now() + timedelta(days=30),
    option_type=OptionType.CALL,
    current_stock_price=155.0,
    risk_free_rate=0.05,
    volatility=0.30
)

# Price it
price = BlackScholesEngine.price_option(option)
print(f"Option Price: ${price:.2f}")

# Calculate Greeks
greeks = GreeksCalculator.calculate_analytical_greeks(option)
print(f"Delta: {greeks.delta:.4f}")
```

### Running Demonstrations

```bash
# Live market data integration demo
python demos/live_market_demo.py

# Monte Carlo pricing demo
python demos/monte_carlo_demo.py

# Greeks analysis demo
python demos/greeks_demo.py

# Create visualizations
python create_visualizations.py
```

---

## 📊 Key Features & Results

### 1. Black-Scholes Analytical Pricing

Implements the famous formula that won the Nobel Prize in Economics (1997):

```
C = S₀ × N(d₁) - K × e^(-rT) × N(d₂)
```

**Performance:** Microsecond-level pricing (0.52ms per 1000 options)

**Example Output:**
```
MSFT $200 Call (90 days, 25% vol)
Black-Scholes Price: $8.49
Time to price: 0.0005 seconds
```

### 2. Monte Carlo Simulation

Simulates thousands of possible price paths to price exotic options:

**Validation Results:**
- Black-Scholes: $8.49
- Monte Carlo (100k sims): $8.43 ± $0.05
- **Relative Error: 0.69%** ✅

**Convergence Analysis:**
| Simulations | Price | Error | Std Error | Time |
|------------|-------|-------|-----------|------|
| 1,000 | $8.47 | 1.07% | $0.11 | 0.11s |
| 10,000 | $8.52 | 0.82% | $0.04 | 0.84s |
| 100,000 | $8.48 | 0.53% | $0.01 | 9.76s |

### 3. Exotic Options Pricing

Prices path-dependent options with no closed-form solutions:

**Asian Options** (payoff based on average price):
```
European Call: $3.59
Asian Call:    $2.08  (42% cheaper due to averaging effect)
```

**Barrier Options** (knock-in/knock-out):
```
European Call:        $5.49
Knock-out ($120):     $2.64  (52% discount - can become worthless)
Knock-in ($120):      $2.87  (only active if barrier hit)
```

### 4. Greeks Risk Analysis

Calculates all five main risk sensitivities:

```
MSFT $200 Call Greeks:
  Delta:  +0.4830  (acts like 48 shares per contract)
  Gamma:  +0.0165  (delta changes by 0.0165 per $1 move)
  Vega:   +0.3858  (gains $0.39 per 1% volatility increase)
  Theta:  -0.0654  (loses $0.07 per day from time decay)
  Rho:    +0.2111  (gains $0.21 per 1% rate increase)
```

**Portfolio Risk Management:**
```
Portfolio: Long 100 calls, Short 50 puts
Net Delta: +64.17  (equivalent to 64 shares)
Daily Theta: -$3.87 (time decay per day)
Hedge: Sell 64 shares for delta-neutral position
```

---

## 🌐 Live Market Data Integration

The engine integrates with Yahoo Finance to fetch real-time market data:

### Real-Time Data Sources
- **Stock Prices**: Live quotes for any ticker
- **Historical Volatility**: 30-day rolling calculations  
- **Options Chains**: Complete bid/ask spreads and open interest
- **Implied Volatility**: Market expectations from option prices
- **Risk-Free Rate**: Current 3-month Treasury yields

### Market Data Demo Results

```
Multi-Stock Volatility Analysis:
  Symbol        Price      30d Vol     Classification
  --------------------------------------------------------
  TSLA      $433.58      47.96%      High (Growth stock)
  AAPL      $260.08      25.57%      Medium (Tech)
  MSFT      $523.62      14.95%      Low (Mature tech)
  SPY       $669.43      10.57%      Low (Stable index)
```

**Volatility Smile Detection:**
- Successfully identifies market phenomena
- OTM puts show elevated IV (downside protection premium)
- ATM options have moderate IV (~28%)
- Deep OTM options show elevated IV (tail risk premium)

### Usage Example

```python
from src.data.market_data import MarketDataFetcher

fetcher = MarketDataFetcher()

# Get live stock price
price = fetcher.get_stock_price("AAPL")  # Returns: $260.08

# Calculate historical volatility
vol = fetcher.get_historical_volatility("AAPL", days=30)  # Returns: 25.57%

# Create option with live market data
option_data = fetcher.create_option_from_market_data(
    symbol="AAPL",
    strike_price=260,
    days_to_expiration=30,
    option_type="call"
)
# Automatically fetches: stock price, implied volatility, risk-free rate
```

### Model Validation

Tested against real SPY options market:
- ✅ Volatility calculations match market consensus
- ✅ Successfully detects volatility smile phenomenon  
- ✅ Handles real-world edge cases (illiquid options, wide spreads)
- ✅ Risk-free rate from actual 3-month Treasury yields

Run the live data demo:
```bash
python demos/live_market_demo.py
```

---

## 📊 Visual Results

### Greeks Evolution Over Time
![Greeks Evolution](images/greeks_evolution.png)
*How risk sensitivities change as expiration approaches. Note the gamma explosion in the bottom-left panel.*

### Monte Carlo Convergence Analysis
![Monte Carlo Convergence](images/monte_carlo_convergence.png)
*Monte Carlo pricing converges to Black-Scholes with error < 1% at 50k simulations.*

### Option Price Surface
![Price Surface](images/price_surface.png)
*3D visualization of call option price across stock prices and time to expiration.*

### Portfolio Risk Dashboard
![Portfolio Dashboard](images/portfolio_dashboard.png)
*Real-time risk management for a multi-leg options portfolio.*

---

## 🌐 API Endpoints

### Options Pricing

#### `POST /api/price/black-scholes`
Price European options using Black-Scholes formula.
```json
{
    "symbol": "AAPL",
    "strike_price": 150.0,
    "days_to_expiration": 30,
    "option_type": "call",
    "stock_price": 155.0,
    "volatility": 0.25,
    "risk_free_rate": 0.05
}
```

#### `POST /api/price/monte-carlo`
Price options using Monte Carlo simulation.
```json
{
    "symbol": "AAPL",
    "strike_price": 150.0,
    "days_to_expiration": 30,
    "option_type": "call",
    "option_style": "asian",
    "stock_price": 155.0,
    "volatility": 0.25,
    "risk_free_rate": 0.05,
    "num_simulations": 10000
}
```

#### `POST /api/price/live`
Price option using LIVE market data from Yahoo Finance.
```json
{
    "symbol": "AAPL",
    "strike_price": 150,
    "days_to_expiration": 30,
    "option_type": "call",
    "use_implied_vol": true
}
```

### Risk Analytics

#### `POST /api/greeks`
Calculate option Greeks (Delta, Gamma, Theta, Vega, Rho).

#### `POST /api/portfolio/analyze`
Analyze multi-leg option strategies.
```json
{
    "positions": [
        {
            "quantity": 100,
            "option": {
                "symbol": "SPY",
                "strike_price": 450,
                "days_to_expiration": 30,
                "option_type": "call"
            }
        }
    ]
}
```

#### `POST /api/market/compare`
Compare model prices against actual market prices.
```json
{
    "symbol": "SPY"
}
```

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_black_scholes.py

# Run with coverage report
python -m pytest --cov=src tests/

# Test the API
python api/test_api.py
```

### Model Validation
- Put-call parity checks (validates mathematical consistency)
- Monte Carlo convergence analysis
- Market price comparison against Yahoo Finance data
- Greeks numerical verification

---

## 🧮 Mathematical Foundation

### Black-Scholes Model

The engine implements the complete Black-Scholes framework:

```python
d₁ = [ln(S/K) + (r + σ²/2)T] / (σ√T)
d₂ = d₁ - σ√T

Call Price = S·N(d₁) - K·e^(-rT)·N(d₂)
Put Price  = K·e^(-rT)·N(-d₂) - S·N(-d₁)
```

**Key Assumptions:**
- European exercise (only at expiration)
- Constant volatility and interest rates
- Log-normal stock price distribution
- No dividends, transaction costs, or taxes

### Geometric Brownian Motion

Monte Carlo paths follow the stochastic differential equation:

```
dS = μS dt + σS dW

Discretized: S(t+Δt) = S(t) · exp[(μ - σ²/2)Δt + σ√Δt · Z]
```

Where Z ~ N(0,1) is a standard normal random variable.

### Greeks Formulas

```
Delta (Δ)  = ∂V/∂S  = N(d₁)                    [for calls]
Gamma (Γ)  = ∂²V/∂S² = φ(d₁)/(S·σ·√T)          [same for calls/puts]
Vega (ν)   = ∂V/∂σ  = S·φ(d₁)·√T               [same for calls/puts]
Theta (Θ)  = ∂V/∂t  = -[S·φ(d₁)·σ]/[2√T] - ... [option-type dependent]
Rho (ρ)    = ∂V/∂r  = K·T·e^(-rT)·N(d₂)        [for calls]
```

---

## 🐛 Technical Challenges & Solutions

### Challenge 1: Monte Carlo Price Explosion

**Problem:** Initial Monte Carlo implementation produced prices of $21,000+ for options that should be $8.

**Root Cause:** Missing time scaling in the drift term of Geometric Brownian Motion.

**Solution:** 
```python
# Wrong: drift_term = (r - 0.5 * sigma**2)
# Correct: drift_term = (r - 0.5 * sigma**2) * dt
```

**Learning:** Stochastic process bugs compound over time - a 0.1% error per step becomes 100%+ over 1000 steps!

### Challenge 2: Expiration Day Edge Cases

**Problem:** Options with < 1 day remaining caused division by zero errors.

**Solution:** Implemented minimum time threshold and special handling:
```python
if time_to_expiration < 1/365:
    return max(intrinsic_value, 0)  # Pure intrinsic value
```

### Challenge 3: Numerical Greeks Accuracy

**Problem:** Finite difference Greeks were noisy for short-dated options.

**Solution:** Used central differences and adaptive bump sizes:
```python
delta = (price(S + h) - price(S - h)) / (2h)  # More accurate than forward difference
```

---

## 📈 Performance Benchmarks

Tested on: MacBook Pro M1, Python 3.9

| Method | Options Priced | Time | Ops/Second |
|--------|---------------|------|------------|
| Black-Scholes | 1,000 | 0.52s | 1,923/s |
| Monte Carlo (10k sims) | 1 | 0.96s | 1.04/s |
| Greeks (analytical) | 1,000 | 0.58s | 1,724/s |
| Market Data Fetch | 1 ticker | 0.3s | 3.3/s |

**Key Insight:** Black-Scholes is ~1,800x faster than Monte Carlo, but Monte Carlo handles ANY option type.

---

## 🎓 What I Learned

### Quantitative Finance
- How derivatives are actually priced in markets
- Why implied volatility matters more than historical volatility
- How market makers hedge billions in risk using Greeks
- The trade-offs between analytical vs numerical methods
- Real-world market microstructure (bid-ask spreads, volatility smile)

### Software Engineering
- Debugging stochastic processes requires understanding the math deeply
- Production code needs extensive edge case handling
- Mathematical validation (put-call parity) is essential
- Performance matters: microseconds vs milliseconds in trading
- API design and RESTful principles

### Problem Solving
- Started with working standalone code, integrated into classes
- Used debug scripts to isolate bugs systematically
- Validated outputs against known analytical solutions
- Built confidence through comprehensive testing
- Integrated external APIs for real-world validation

---

## 🚀 Future Enhancements

**Completed:**
- [x] Black-Scholes analytical pricing
- [x] Monte Carlo simulation
- [x] Greeks calculation
- [x] REST API implementation
- [x] Live market data integration (Yahoo Finance) ✅
- [x] Volatility smile analysis ✅
- [x] Professional visualizations ✅

**Planned Features:**
- [ ] Implied volatility calculation (Newton-Raphson method)
- [ ] American options (Longstaff-Schwartz algorithm)
- [ ] Multi-asset options (basket options, spreads)
- [ ] Interactive web dashboard
- [ ] Historical data backtesting
- [ ] Volatility surface 3D visualization

**Nice-to-Have:**
- [ ] GPU acceleration for Monte Carlo (CuPy)
- [ ] Distributed simulation (Ray/Dask)
- [ ] Machine learning for implied vol prediction
- [ ] Integration with additional data providers

---

## 📚 References & Resources

**Academic Papers:**
- Black, F., & Scholes, M. (1973). "The Pricing of Options and Corporate Liabilities"
- Merton, R. C. (1973). "Theory of Rational Option Pricing"

**Books:**
- Hull, J. C. (2018). "Options, Futures, and Other Derivatives" (10th ed.)
- Shreve, S. E. (2004). "Stochastic Calculus for Finance II"

**Online Resources:**
- [QuantLib Documentation](https://www.quantlib.org/)
- [Derivatives Markets on Coursera](https://www.coursera.org/learn/financial-engineering-1)

---

## 🤝 Contributing

Contributions are welcome! Areas where help is needed:

1. **Additional option types** (American, Lookback, Asian variants)
2. **Performance optimization** (Cython, numba JIT compilation)
3. **Test coverage** (currently at ~60%, target 90%+)
4. **Documentation** (jupyter notebooks with examples)

---

## 📜 License

MIT License - feel free to use this for learning or commercial projects.

---

## 👨‍💻 Author

**Ayotunde Akinboade**
- Aspiring Quantitative Developer
- Interested in fintech and algorithmic trading
- Currently learning quantitative finance and building towards roles at firms like Goldman Sachs, Citadel, or fintech platforms like Cowrywise

**Connect:**
- GitHub: [@lawren-ai](https://github.com/lawren-ai)
- LinkedIn: [Ayotunde Akinboade](https://www.linkedin.com/in/ayotunde-akinboade)
- Email: akinboadelawrenceayo@gmail.com

Feel free to reach out for questions, feedback, or collaboration opportunities!

---

## 🙏 Acknowledgments

Built as a learning project to understand how financial markets work and how quantitative finance teams at investment banks price and manage risk for complex derivatives.

Special thanks to the open-source quantitative finance community and resources like QuantLib, Quantitative Finance on StackExchange, and MIT OpenCourseWare for making this knowledge accessible.

---

**⭐ If you found this project helpful, please consider starring it on GitHub!**