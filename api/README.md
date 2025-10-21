# Options Pricing Engine API

A production-grade REST API for options pricing and risk analytics. This API provides endpoints for Black-Scholes pricing, Monte Carlo simulation, Greeks calculation, and portfolio analysis.

## 🚀 Features

- Black-Scholes option pricing
- Monte Carlo simulation for exotic options
- Greeks calculation (Delta, Gamma, Vega, Theta, Rho)
- Portfolio analysis and risk metrics
- Method comparison tools
- Interactive Swagger documentation

## 📋 API Endpoints

### Pricing Endpoints

#### `POST /api/price/black-scholes`
Price European options using the Black-Scholes formula.
```json
{
    "symbol": "MSFT",
    "strike_price": 200,
    "days_to_expiration": 90,
    "stock_price": 195,
    "risk_free_rate": 0.05,
    "volatility": 0.25,
    "option_type": "call"
}
```

#### `POST /api/price/monte-carlo`
Price options using Monte Carlo simulation. Supports European, Asian, and Barrier options.
```json
{
    "symbol": "AAPL",
    "strike_price": 150,
    "days_to_expiration": 60,
    "stock_price": 145,
    "risk_free_rate": 0.05,
    "volatility": 0.30,
    "option_type": "put",
    "option_style": "european",
    "num_simulations": 10000
}
```

### Risk Analysis Endpoints

#### `POST /api/greeks`
Calculate option Greeks using analytical formulas.
```json
{
    "symbol": "TSLA",
    "strike_price": 800,
    "days_to_expiration": 30,
    "stock_price": 780,
    "risk_free_rate": 0.05,
    "volatility": 0.40,
    "option_type": "call"
}
```

#### `POST /api/portfolio/analyze`
Analyze multi-leg options portfolio.
```json
{
    "positions": [
        {
            "quantity": 1,
            "option": {
                "symbol": "AAPL",
                "strike_price": 150,
                "days_to_expiration": 60,
                "stock_price": 145,
                "volatility": 0.30,
                "option_type": "call"
            }
        }
    ]
}
```

### Utility Endpoints

#### `GET /api/health`
Check API health status.

#### `POST /api/compare`
Compare Black-Scholes vs Monte Carlo pricing.

## 🛠️ Setup & Installation

1. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install flask flask-cors flask-swagger-ui numpy scipy
```

3. Run the server:
```bash
python api/app.py
```

4. Access the API documentation:
- Swagger UI: http://localhost:5000/docs
- API Specification: http://localhost:5000/static/swagger.json

## 📚 API Documentation

Full API documentation is available through the Swagger UI interface at `/docs` when the server is running. This includes:
- Detailed request/response schemas
- Example payloads
- Error responses
- Interactive testing interface

## 🧪 Example Usage

Using Python requests:
```python
import requests
import json

# Define the option parameters
data = {
    "symbol": "MSFT",
    "strike_price": 200,
    "days_to_expiration": 90,
    "stock_price": 195,
    "risk_free_rate": 0.05,
    "volatility": 0.25,
    "option_type": "call"
}

# Calculate option price and Greeks
response = requests.post(
    "http://localhost:5000/api/greeks",
    json=data
)

# Print the results
print(json.dumps(response.json(), indent=2))
```

Using PowerShell:
```powershell
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    symbol = "MSFT"
    strike_price = 200
    days_to_expiration = 90
    stock_price = 195
    risk_free_rate = 0.05
    volatility = 0.25
    option_type = "call"
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/api/greeks -Method Post -Headers $headers -Body $body
```

## ⚡ Performance

- Black-Scholes pricing: <1ms per calculation
- Greeks calculation: <1ms for all Greeks
- Monte Carlo simulation: ~100-500ms for 10,000 simulations
- Portfolio analysis: Scales linearly with number of positions

## 🔒 Error Handling

The API includes comprehensive error handling for:
- Invalid parameters
- Missing required fields
- Out-of-range values
- Server errors

All errors return a JSON response with:
- HTTP status code
- Error message
- Additional context when available

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.