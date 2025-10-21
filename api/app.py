
"""
Options Pricing Engine REST API

A production-ready Flask API for option pricing and risk analytics.
Exposes Black-Scholes, Monte Carlo, and Greeks calculation via HTTP endpoints.

Usage:
    python api/app.py
    
    Then visit: http://localhost:5000/docs
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from datetime import datetime, timedelta
import sys
import os

# Add project root directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

try:
    from src.models.option import Option, OptionType
    from src.models.black_scholes import BlackScholesEngine
    from src.models.monte_carlo import MonteCarloEngine
    from src.models.greeks import GreeksCalculator
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running the app from the project root directory")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web clients

# Configuration
app.config['JSON_SORT_KEYS'] = False

# Swagger UI configuration
SWAGGER_URL = '/docs'  # URL for exposing Swagger UI
API_URL = '/static/swagger.json'  # Our API url (can be a local file)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Options Pricing Engine API",
        'deepLinking': True,
        'displayOperationId': True
    }
)

# Register blueprint at URL
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Route for serving swagger specification
@app.route("/static/swagger.json")
def serve_swagger_spec():
    return send_from_directory(os.path.dirname(__file__), 'swagger.json')

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

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = ['flask', 'flask-cors', 'flask-swagger-ui', 'numpy', 'scipy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

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
    print("🚀 Options Pricing Engine API")
    print("=" * 50)
    
    # Check dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   • {package}")
        print("\nPlease install missing packages using:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)
    
    print("✅ All dependencies installed")
    print("\nAvailable Endpoints:")
    print("  • GET /api/health - Check API health")
    print("  • POST /api/price/black-scholes - Price options using Black-Scholes")
    print("  • POST /api/price/monte-carlo - Price options using Monte Carlo")
    print("  • POST /api/greeks - Calculate option Greeks")
    print("  • POST /api/portfolio/analyze - Analyze option portfolio")
    print("  • GET /docs - Interactive API documentation")
    
    print("\n📖 Swagger UI: http://localhost:5000/docs")
    print("🔍 API Documentation: http://localhost:5000/static/swagger.json")
    print("\nStarting server...")
    
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
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