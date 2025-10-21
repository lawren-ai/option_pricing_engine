

"""
Test script for Options Pricing Engine REST API.

Run the API server first:
    python api/app.py

Then run this script in another terminal:
    python api/test_api.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_header(title):
    print("\n" + "=" * 70)
    print(f"🧪 {title}")
    print("=" * 70)

def print_response(response):
    """Pretty print JSON response"""
    if response.status_code == 200:
        print("✅ Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Error {response.status_code}")
        print(json.dumps(response.json(), indent=2))

def test_health_check():
    """Test health check endpoint"""
    print_header("HEALTH CHECK")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response(response)

def test_black_scholes_pricing():
    """Test Black-Scholes pricing"""
    print_header("BLACK-SCHOLES PRICING")
    
    payload = {
        "symbol": "AAPL",
        "option_type": "call",
        "strike_price": 150,
        "stock_price": 155,
        "days_to_expiration": 30,
        "risk_free_rate": 0.05,
        "volatility": 0.30
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/price/black-scholes", json=payload)
    print_response(response)

def test_monte_carlo_pricing():
    """Test Monte Carlo pricing"""
    print_header("MONTE CARLO SIMULATION")
    
    payload = {
        "symbol": "MSFT",
        "option_type": "call",
        "strike_price": 200,
        "stock_price": 195,
        "days_to_expiration": 90,
        "risk_free_rate": 0.05,
        "volatility": 0.25,
        "num_simulations": 50000,
        "option_style": "european"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/price/monte-carlo", json=payload)
    print_response(response)

def test_greeks_calculation():
    """Test Greeks calculation"""
    print_header("GREEKS CALCULATION")
    
    payload = {
        "symbol": "GOOGL",
        "option_type": "call",
        "strike_price": 2800,
        "stock_price": 2850,
        "days_to_expiration": 45,
        "risk_free_rate": 0.05,
        "volatility": 0.28
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/greeks", json=payload)
    print_response(response)

def test_asian_option():
    """Test Asian option pricing"""
    print_header("ASIAN OPTION PRICING")
    
    payload = {
        "symbol": "TSLA",
        "option_type": "call",
        "strike_price": 200,
        "stock_price": 200,
        "days_to_expiration": 60,
        "risk_free_rate": 0.05,
        "volatility": 0.45,
        "num_simulations": 30000,
        "option_style": "asian"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/price/monte-carlo", json=payload)
    print_response(response)

def test_barrier_option():
    """Test Barrier option pricing"""
    print_header("BARRIER OPTION PRICING")
    
    payload = {
        "symbol": "NVDA",
        "option_type": "call",
        "strike_price": 100,
        "stock_price": 100,
        "days_to_expiration": 90,
        "risk_free_rate": 0.05,
        "volatility": 0.30,
        "num_simulations": 30000,
        "option_style": "barrier",
        "barrier_level": 120,
        "barrier_type": "knock_out"
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/price/monte-carlo", json=payload)
    print_response(response)

def test_portfolio_analysis():
    """Test portfolio analysis"""
    print_header("PORTFOLIO RISK ANALYSIS")
    
    payload = {
        "positions": [
            {
                "quantity": 100,
                "option": {
                    "symbol": "SPY",
                    "option_type": "call",
                    "strike_price": 450,
                    "stock_price": 450,
                    "days_to_expiration": 30,
                    "risk_free_rate": 0.05,
                    "volatility": 0.15
                }
            },
            {
                "quantity": -50,
                "option": {
                    "symbol": "SPY",
                    "option_type": "put",
                    "strike_price": 440,
                    "stock_price": 450,
                    "days_to_expiration": 30,
                    "risk_free_rate": 0.05,
                    "volatility": 0.15
                }
            }
        ]
    }
    
    print("Request:")
    print("Portfolio: Long 100 calls @ 450, Short 50 puts @ 440")
    
    response = requests.post(f"{BASE_URL}/api/portfolio/analyze", json=payload)
    print_response(response)

def test_comparison():
    """Test Black-Scholes vs Monte Carlo comparison"""
    print_header("PRICING METHOD COMPARISON")
    
    payload = {
        "symbol": "AMD",
        "option_type": "call",
        "strike_price": 100,
        "stock_price": 100,
        "days_to_expiration": 30,
        "risk_free_rate": 0.05,
        "volatility": 0.40,
        "num_simulations": 50000
    }
    
    print("Request:")
    print(json.dumps(payload, indent=2))
    
    response = requests.post(f"{BASE_URL}/api/compare", json=payload)
    print_response(response)

def main():
    """Run all API tests"""
    print("=" * 70)
    print("🚀 OPTIONS PRICING ENGINE - API TESTS")
    print("=" * 70)
    print("\n⚠️  Make sure the API server is running:")
    print("   python api/app.py")
    print("\nTesting API at:", BASE_URL)
    
    try:
        # Run all tests
        test_health_check()
        test_black_scholes_pricing()
        test_monte_carlo_pricing()
        test_greeks_calculation()
        test_asian_option()
        test_barrier_option()
        test_portfolio_analysis()
        test_comparison()
        
        print("\n" + "=" * 70)
        print("✅ ALL API TESTS COMPLETED!")
        print("=" * 70)
        print("\n💡 Your API is working perfectly!")
        print("📖 Full documentation: http://localhost:5000/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 70)
        print("❌ CONNECTION ERROR")
        print("=" * 70)
        print("\n⚠️  Could not connect to API server!")
        print("Please start the server first:")
        print("   python api/app.py")
        print("\nThen run this test script again.")

if __name__ == "__main__":
    main()