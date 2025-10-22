# api/app.py

"""
Options Pricing Engine REST API

A production-ready Flask API for option pricing and risk analytics.
Exposes Black-Scholes, Monte Carlo, and Greeks calculation via HTTP endpoints.

Usage:
    python api/app.py
    
    Then visit: http://localhost:5000/docs
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.option import Option, OptionType
from models.black_scholes import BlackScholesEngine
from models.monte_carlo import MonteCarloEngine
from models.greeks import GreeksCalculator

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web clients

# Configuration
app.config['JSON_SORT_KEYS'] = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_option_from_request(data):
    """
    Parse option parameters from JSON request.
    Handles date parsing and validation.
    """
    try:
        # Parse expiration date
        if 'days_to_expiration' in data:
            expiration_date = datetime.now() + timedelta(days=int(data['days_to_expiration']))
        elif 'expiration_date' in data:
            expiration_date = datetime.fromisoformat(data['expiration_date'])
        else:
            raise ValueError("Must provide either 'days_to_expiration' or 'expiration_date'")
        
        # Parse option type
        option_type_str = data.get('option_type', 'call').lower()
        option_type = OptionType.CALL if option_type_str == 'call' else OptionType.PUT
        
        # Create option object
        option = Option(
            symbol=data.get('symbol', 'DEMO'),
            strike_price=float(data['strike_price']),
            expiration_date=expiration_date,
            option_type=option_type,
            current_stock_price=float(data['stock_price']),
            risk_free_rate=float(data.get('risk_free_rate', 0.05)),
            volatility=float(data.get('volatility'))
        )
        
        return option, None
    
    except KeyError as e:
        return None, f"Missing required parameter: {str(e)}"
    except ValueError as e:
        return None, f"Invalid parameter value: {str(e)}"
    except Exception as e:
        return None, f"Error parsing request: {str(e)}"

def option_to_dict(option, price=None, greeks=None):
    """Convert option object to JSON-serializable dictionary"""
    result = {
        'symbol': option.symbol,
        'option_type': option.option_type.value,
        'strike_price': option.strike_price,
        'stock_price': option.current_stock_price,
        'expiration_date': option.expiration_date.isoformat(),
        'days_to_expiration': (option.expiration_date - datetime.now()).days,
        'time_to_expiration': option.time_to_expiration,
        'risk_free_rate': option.risk_free_rate,
        'volatility': option.volatility,
        'is_in_the_money': option.is_in_the_money,
        'intrinsic_value': option.intrinsic_value
    }
    
    if price is not None:
        result['price'] = round(price, 4)
        result['time_value'] = round(price - option.intrinsic_value, 4)
    
    if greeks is not None:
        result['greeks'] = {
            'delta': round(greeks.delta, 6),
            'gamma': round(greeks.gamma, 6),
            'vega': round(greeks.vega, 6),
            'theta': round(greeks.theta, 6),
            'rho': round(greeks.rho, 6)
        }
    
    return result

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/')
def home():
    """API home page with documentation"""
    return jsonify({
        'name': 'Options Pricing Engine API',
        'version': '1.0.0',
        'description': 'Production-grade options pricing and risk analytics',
        'documentation': '/docs',
        'endpoints': {
            'pricing': {
                'black_scholes': 'POST /api/price/black-scholes',
                'monte_carlo': 'POST /api/price/monte-carlo',
                'exotic': 'POST /api/price/exotic'
            },
            'greeks': 'POST /api/greeks',
            'portfolio': 'POST /api/portfolio/analyze',
            'health': 'GET /api/health'
        }
    })

@app.route('/api/price/live', methods=['POST'])
def price_with_live_data():
    """
    Price option using live market data.
    Automatically fetches current stock price, volatility, and risk-free rate.
    """
    try:
        from data.market_data import MarketDataFetcher
        
        data = request.get_json()
        
        symbol = data.get('symbol')
        strike_price = float(data.get('strike_price'))
        days_to_expiration = int(data.get('days_to_expiration'))
        option_type = data.get('option_type', 'call')
        use_implied_vol = data.get('use_implied_vol', True)
        
        # Fetch live market data
        fetcher = MarketDataFetcher()
        option_data = fetcher.create_option_from_market_data(
            symbol=symbol,
            strike_price=strike_price,
            days_to_expiration=days_to_expiration,
            option_type=option_type,
            use_implied_vol=use_implied_vol
        )
        
        if not option_data:
            return jsonify({
                'success': False,
                'error': f'Could not fetch market data for {symbol}'
            }), 400
        
        # Create option and price it
        option, error = parse_option_from_request(option_data)
        if error:
            return jsonify({'error': error}), 400
        
        price = BlackScholesEngine.price_option(option)
        greeks = GreeksCalculator.calculate_analytical_greeks(option)
        
        return jsonify({
            'method': 'black_scholes_with_live_data',
            'success': True,
            'option': option_to_dict(option, price=price, greeks=greeks),
            'market_data': {
                'data_source': 'yahoo_finance',
                'volatility_type': 'implied' if use_implied_vol else 'historical',
                'timestamp': option_data['timestamp']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/market/compare', methods=['POST'])
def compare_with_market():
    """
    Compare your model price against actual market prices.
    Returns model price, market price, and the difference.
    """
    try:
        from data.market_data import MarketDataFetcher
        
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        # Get market comparison
        fetcher = MarketDataFetcher()
        comparison = fetcher.compare_model_vs_market(symbol)
        
        if comparison is None or comparison.empty:
            return jsonify({
                'success': False,
                'error': f'No options data available for {symbol}'
            }), 404
        
        # Convert to JSON-friendly format
        results = comparison.to_dict('records')
        
        # Calculate summary stats
        summary = {
            'symbol': symbol,
            'options_analyzed': len(comparison),
            'mean_absolute_error': float(comparison['Difference'].abs().mean()),
            'mean_percent_error': float(comparison['Pct_Error'].abs().mean()),
            'median_percent_error': float(comparison['Pct_Error'].abs().median()),
            'validation': 'PASS' if comparison['Pct_Error'].abs().mean() < 10 else 'REVIEW'
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'top_10_atm_options': results[:10],
            'full_results_count': len(results)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Update the docs endpoint to include new endpoints
@app.route('/docs')
def docs():
    """API documentation"""
    return jsonify({
        'title': 'Options Pricing Engine API Documentation',
        'base_url': 'http://localhost:5000',
        
        'endpoints': [
            {
                'endpoint': 'POST /api/price/black-scholes',
                'description': 'Price European option using Black-Scholes formula',
                'request_body': {
                    'symbol': 'string (optional, default: DEMO)',
                    'option_type': 'string (call or put)',
                    'strike_price': 'number',
                    'stock_price': 'number',
                    'days_to_expiration': 'integer',
                    'risk_free_rate': 'number (optional, default: 0.05)',
                    'volatility': 'number (e.g., 0.25 for 25%)'
                },
                'example': {
                    'symbol': 'AAPL',
                    'option_type': 'call',
                    'strike_price': 150,
                    'stock_price': 155,
                    'days_to_expiration': 30,
                    'volatility': 0.30
                }
            },
            {
                'endpoint': 'POST /api/price/live',
                'description': 'Price option using LIVE market data from Yahoo Finance',
                'request_body': {
                    'symbol': 'string (required)',
                    'strike_price': 'number',
                    'days_to_expiration': 'integer',
                    'option_type': 'string (call or put)',
                    'use_implied_vol': 'boolean (optional, default: true)'
                },
                'example': {
                    'symbol': 'AAPL',
                    'strike_price': 150,
                    'days_to_expiration': 30,
                    'option_type': 'call',
                    'use_implied_vol': True
                },
                'note': 'Automatically fetches stock price, volatility, and risk-free rate'
            },
            {
                'endpoint': 'POST /api/market/compare',
                'description': 'Compare model prices vs actual market prices',
                'request_body': {
                    'symbol': 'string (required)'
                },
                'example': {
                    'symbol': 'SPY'
                },
                'returns': 'Comparison of model vs market for entire options chain'
            },
            {
                'endpoint': 'POST /api/price/monte-carlo',
                'description': 'Price option using Monte Carlo simulation',
                'additional_params': {
                    'num_simulations': 'integer (default: 10000)',
                    'option_style': 'string (european, asian, barrier)'
                }
            },
            {
                'endpoint': 'POST /api/greeks',
                'description': 'Calculate option Greeks (Delta, Gamma, Vega, Theta, Rho)',
                'returns': 'Option price and all Greeks'
            },
            {
                'endpoint': 'POST /api/portfolio/analyze',
                'description': 'Analyze multi-leg options portfolio',
                'request_body': {
                    'positions': [
                        {
                            'quantity': 'number (positive for long, negative for short)',
                            'option': 'option parameters as above'
                        }
                    ]
                }
            }
        ]
    })

# Update home endpoint to include new features
@app.route('/')
def home():
    """API home page with documentation"""
    return jsonify({
        'name': 'Options Pricing Engine API',
        'version': '1.0.0',
        'description': 'Production-grade options pricing and risk analytics with LIVE market data',
        'documentation': '/docs',
        'endpoints': {
            'pricing': {
                'black_scholes': 'POST /api/price/black-scholes',
                'monte_carlo': 'POST /api/price/monte-carlo',
                'live_market_data': 'POST /api/price/live',  # NEW
                'exotic': 'POST /api/price/exotic'
            },
            'market_data': {
                'compare_vs_market': 'POST /api/market/compare'  # NEW
            },
            'greeks': 'POST /api/greeks',
            'portfolio': 'POST /api/portfolio/analyze',
            'health': 'GET /api/health'
        },
        'features': [
            'Real-time market data from Yahoo Finance',
            'Black-Scholes analytical pricing',
            'Monte Carlo simulation',
            'Exotic options (Asian, Barrier)',
            'Greeks calculation',
            'Portfolio risk management',
            'Model vs market validation'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'black_scholes': 'operational',
            'monte_carlo': 'operational',
            'greeks': 'operational'
        }
    })

@app.route('/api/price/black-scholes', methods=['POST'])
def price_black_scholes():
    """
    Price European option using Black-Scholes formula.
    Fast analytical pricing (microseconds).
    """
    try:
        data = request.get_json()
        
        # Parse option from request
        option, error = parse_option_from_request(data)
        if error:
            return jsonify({'error': error}), 400
        
        # Price the option
        price = BlackScholesEngine.price_option(option)
        
        # Return result
        return jsonify({
            'method': 'black_scholes',
            'success': True,
            'option': option_to_dict(option, price=price),
            'computation_time_ms': '<1'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/price/monte-carlo', methods=['POST'])
def price_monte_carlo():
    """
    Price option using Monte Carlo simulation.
    Slower but handles exotic options.
    """
    try:
        data = request.get_json()
        
        # Parse option
        option, error = parse_option_from_request(data)
        if error:
            return jsonify({'error': error}), 400
        
        # Parse Monte Carlo parameters
        num_simulations = int(data.get('num_simulations', 10000))
        option_style = data.get('option_style', 'european').lower()
        
        # Initialize Monte Carlo engine
        mc_engine = MonteCarloEngine()
        
        # Price based on option style
        if option_style == 'european':
            result = mc_engine.price_european_option(option, num_simulations=num_simulations)
        elif option_style == 'asian':
            result = mc_engine.price_asian_option(option, num_simulations=num_simulations)
        elif option_style == 'barrier':
            barrier_level = float(data.get('barrier_level'))
            barrier_type = data.get('barrier_type', 'knock_out')
            result = mc_engine.price_barrier_option(
                option, barrier_level, barrier_type, num_simulations=num_simulations
            )
        else:
            return jsonify({'error': f'Unknown option style: {option_style}'}), 400
        
        # Return result
        return jsonify({
            'method': 'monte_carlo',
            'option_style': option_style,
            'success': True,
            'option': option_to_dict(option, price=result.price),
            'monte_carlo': {
                'num_simulations': result.num_simulations,
                'standard_error': round(result.standard_error, 6),
                'confidence_interval_95': [
                    round(result.confidence_interval_95[0], 4),
                    round(result.confidence_interval_95[1], 4)
                ],
                'computation_time_ms': round(result.simulation_time * 1000, 2)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/greeks', methods=['POST'])
def calculate_greeks():
    """
    Calculate option Greeks using analytical Black-Scholes formulas.
    Returns price and all risk sensitivities.
    """
    try:
        data = request.get_json()
        
        # Parse option
        option, error = parse_option_from_request(data)
        if error:
            return jsonify({'error': error}), 400
        
        # Calculate price and Greeks
        price = BlackScholesEngine.price_option(option)
        greeks = GreeksCalculator.calculate_analytical_greeks(option)
        
        # Return result
        return jsonify({
            'success': True,
            'option': option_to_dict(option, price=price, greeks=greeks),
            'interpretation': {
                'delta_meaning': f"If stock moves $1, option changes by ${greeks.delta:.2f}",
                'gamma_meaning': f"Delta changes by {greeks.gamma:.4f} per $1 stock move",
                'vega_meaning': f"If volatility increases 1%, option gains ${greeks.vega:.2f}",
                'theta_meaning': f"Option loses ${abs(greeks.theta):.2f} per day",
                'rho_meaning': f"If rates increase 1%, option changes by ${greeks.rho:.2f}"
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio/analyze', methods=['POST'])
def analyze_portfolio():
    """
    Analyze multi-leg options portfolio.
    Calculates aggregate Greeks and risk metrics.
    """
    try:
        data = request.get_json()
        positions = data.get('positions', [])
        
        if not positions:
            return jsonify({'error': 'No positions provided'}), 400
        
        # Calculate Greeks for each position
        portfolio_results = []
        total_delta = 0
        total_gamma = 0
        total_vega = 0
        total_theta = 0
        total_rho = 0
        total_value = 0
        
        for position in positions:
            quantity = float(position.get('quantity', 1))
            option_data = position.get('option', {})
            
            # Parse option
            option, error = parse_option_from_request(option_data)
            if error:
                return jsonify({'error': f'Invalid option in position: {error}'}), 400
            
            # Calculate price and Greeks
            price = BlackScholesEngine.price_option(option)
            greeks = GreeksCalculator.calculate_analytical_greeks(option)
            
            # Aggregate
            total_delta += quantity * greeks.delta
            total_gamma += quantity * greeks.gamma
            total_vega += quantity * greeks.vega
            total_theta += quantity * greeks.theta
            total_rho += quantity * greeks.rho
            total_value += quantity * price
            
            portfolio_results.append({
                'quantity': quantity,
                'option': option_to_dict(option, price=price, greeks=greeks)
            })
        
        # Calculate hedge
        hedge_shares = -total_delta
        
        return jsonify({
            'success': True,
            'positions': portfolio_results,
            'portfolio_summary': {
                'total_value': round(total_value, 2),
                'net_delta': round(total_delta, 4),
                'net_gamma': round(total_gamma, 6),
                'net_vega': round(total_vega, 4),
                'net_theta': round(total_theta, 4),
                'net_rho': round(total_rho, 4)
            },
            'risk_analysis': {
                'delta_equivalent_shares': round(total_delta, 2),
                'daily_theta_decay': round(abs(total_theta), 2),
                'monthly_theta_decay': round(abs(total_theta) * 30, 2),
                'vol_sensitivity_1pct': round(total_vega, 2)
            },
            'hedging': {
                'delta_hedge': {
                    'action': 'sell' if hedge_shares > 0 else 'buy',
                    'shares': abs(round(hedge_shares, 0)),
                    'description': f"{'Sell' if hedge_shares > 0 else 'Buy'} {abs(int(hedge_shares))} shares to neutralize delta"
                }
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def compare_methods():
    """
    Compare Black-Scholes vs Monte Carlo for the same option.
    Useful for validation and understanding trade-offs.
    """
    try:
        data = request.get_json()
        
        # Parse option
        option, error = parse_option_from_request(data)
        if error:
            return jsonify({'error': error}), 400
        
        # Black-Scholes
        bs_price = BlackScholesEngine.price_option(option)
        
        # Monte Carlo
        num_sims = int(data.get('num_simulations', 50000))
        mc_engine = MonteCarloEngine(random_seed=42)
        mc_result = mc_engine.price_european_option(option, num_simulations=num_sims)
        
        # Compare
        difference = abs(bs_price - mc_result.price)
        relative_error = (difference / bs_price) * 100
        
        return jsonify({
            'success': True,
            'option': option_to_dict(option),
            'black_scholes': {
                'price': round(bs_price, 4),
                'method': 'analytical',
                'computation_time': '<1ms'
            },
            'monte_carlo': {
                'price': round(mc_result.price, 4),
                'method': 'numerical',
                'num_simulations': mc_result.num_simulations,
                'standard_error': round(mc_result.standard_error, 6),
                'confidence_interval': [
                    round(mc_result.confidence_interval_95[0], 4),
                    round(mc_result.confidence_interval_95[1], 4)
                ],
                'computation_time_ms': round(mc_result.simulation_time * 1000, 2)
            },
            'comparison': {
                'absolute_difference': round(difference, 4),
                'relative_error_pct': round(relative_error, 2),
                'validation': 'PASS' if relative_error < 1.0 else 'CHECK',
                'speed_ratio': f"Monte Carlo is ~{int(mc_result.simulation_time * 1000)}x slower"
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'documentation': '/docs'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 OPTIONS PRICING ENGINE REST API")
    print("=" * 70)
    print("\n📡 Starting server...")
    print("📍 Base URL: http://localhost:5000")
    print("📖 Documentation: http://localhost:5000/docs")
    print("\n🔥 Available endpoints:")
    print("   • POST /api/price/black-scholes  - Fast analytical pricing")
    print("   • POST /api/price/monte-carlo    - Numerical simulation")
    print("   • POST /api/greeks               - Risk sensitivities")
    print("   • POST /api/portfolio/analyze    - Portfolio analytics")
    print("   • POST /api/compare              - Method comparison")
    print("\n💡 Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)