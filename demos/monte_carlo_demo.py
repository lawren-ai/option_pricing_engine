import sys
import os
from datetime import datetime, timedelta
import time
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.option import Option, OptionType
from src.models.black_scholes import BlackScholesEngine
from src.models.monte_carlo import MonteCarloEngine

def demo_monte_carlo_vs_black_scholes():
    print("=" * 80)
    print(" MONTE CARLO vs BLACK-SCHOLES COMPARISON")
    print("=" * 80)

    msft_call = Option(
        symbol='MSFT',
        strike_price=200.0,
        expiration_date=datetime.now() + timedelta(days=90),
        option_type=OptionType.CALL,
        current_stock_price=195.0,
        risk_free_rate=0.05,
        volatility=0.25
    )

    print(f"Pricing: {msft_call}")
    print(f"Current stock: ${msft_call.current_stock_price}")
    print(f"Volatility: {msft_call.volatility:.1%}")
    print(f"TIme to expiration: {msft_call.time_to_expiration:.3f} years")
    
    comparison = MonteCarloEngine.compare_methods(msft_call, num_simulations=100000)

    print("RESULTS: ")
    print(f"Black-Scholes (analytical): {comparison['black_scholes_price']:.4f}")
    print(f"Monte Caro (simulation): ${comparison['monte_carlo_price']:.4f}")
    print(f"Absolute difference: ${comparison['difference']:.4f}")
    print(f"Relative error: ${comparison['relative_error']:.2f}%")
    print(f"Monte Carlo std error: ${comparison['monte_carlo_std_error']:.4f}")
    print(f"95% Confidence interval: ${comparison['confidence_interval'][0]:.4f} - ${comparison['confidence_interval'][1]:.4f}")
    print(f"Simulation time: ${comparison['simulation_time']:.2f} seconds")

    print("Analysis: ")
    if comparison['relative_error'] < 1.0:
        print("Excellent Monte Carlo matches Black-Scholes within 1%")
        print("This validates Monte Carlo implementation")
    elif comparison['relative_error'] < 2.0:
        print("Good! Monte Carlo matches Black-Scholes within 2%")
        print(" Small difference due to Monte Carlo Sampling error")
    else:
        print(" Large differnce - check implementation or increase simulations")

    return comparison

def demo_convergence_analysis():
    """
    Show how Monte Carlo accuracy improves with more simulations."""

    print(" MONTE CARLO CONVERGENCE ANALYSIS")
    
    test_option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )

    bs_price = BlackScholesEngine.price_option(test_option)
    print(f" Black Scholes benchmark: ${bs_price:.4f}")

    # test different number of simulations
    mc_engine = MonteCarloEngine(random_seed=42)
    simulation_counts = [1000, 5000, 10000, 25000, 50000, 100000]
    
    print(" Convergence Results: ")
    print(f"{'Simulations':<12} {'MC Price':<10} {'Error':<8} {'Rel Error':<10} {'Std Error':<10} {'Time':<8}")

    for num_sims in simulation_counts:
        result = mc_engine.price_european_option(test_option, num_sims)
        error = abs(result.price - bs_price)
        rel_error = (error / bs_price) * 100

        print(f"{num_sims:<12} ${result.price:<9.4f} ${error:<7.4f} {rel_error:<9.2f}% ${result.standard_error:<.4f} {result.simulation_time:<7.2f}s")
        
    print("Key Insights: ")
    print(f" More Simulations = more accurate results")
    print(f" Standard error decreases as square root of n(simulations)")
    print(f" Diminishing returns: 100k sims are not 10x better than 10k")
    print(f" Balance accuracy vs speed for production systems")


def demo_asian_options():
    print("ASIAN OPTIONS PRICING (Path-Dependent)")

    base_option = Option(
        symbol='ASIAN_TEST',
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.30
        )

    mc_engine = MonteCarloEngine(random_seed=42)

    european_result = mc_engine.price_european_option(base_option, num_simulations=50000)

    asian_result = mc_engine.price_asian_option(base_option, num_simulations=50000)

    print("Option Details: ")
    print(f" Stock: {base_option.symbol}")
    print(f" Strike: ${base_option.strike_price}")
    print(f" Current Price: ${base_option.current_stock_price}")
    print(f" Volatility: {base_option.volatility:.1%}")
    print(f" Time: {base_option.time_to_expiration:.3f} years")

    print("PRICING RESULTS: ")
    print(f"European Call (final price): ${european_result.price:.4f} ± ${european_result.standard_error:.4f}")
    print(f"Asian Call (average price): ${asian_result.price:.4f} ± ${asian_result.standard_error:.4f}")

    difference = european_result.price - asian_result.price
    discount_percent = (difference / european_result.price) * 100
    
    print(f" Asian vs European difference: ${difference:.4f}")
    print(f" Asian discount: {discount_percent:.1f}%")

    print(f" Why Asian Options Are Cheaper: ")
    print(f" Payoff based on AVERAGE price never option life")
    print(f" Average is less volatile than final price")
    print(f" Lower volatility = lower option value")
    print(f" Popular for hedging average exposure (oil prices , FX rates)")

    return european_result, asian_result

def demo_barrier_options():
    """
    Demonstrate barrier options - avtivated/deactivated by price levels
    """
    print("BARRIER OPTIONS PRICING (Path-Dependent)")

    base_option = Option(
        symbol = "BARRIER_TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=90),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )

    mc_engine = MonteCarloEngine(random_seed=42)

    # Price regular European option
    european_result = mc_engine.price_european_option(base_option, num_simulations=30000)

    # price barrier options with different barrier levels
    barrier_levels = [90, 95, 105, 110, 120]

    print(f"Base Option: {base_option}")
    print(f"Current Stock Price: ${base_option.current_stock_price}")
    print(f"European Call Price: ${european_result.price:.4f}")

    print(f" KNOCK-OUT CALL OPTIONS (become worthless if barrier hit):")
    print(f"{'Barrirer':<8} {'Price':<10} {'vs European':<12} {'Discount':<10}")

    for barrier in barrier_levels:
        if barrier > base_option.current_stock_price:
            barrier_result = mc_engine.price_barrier_option(
                base_option, barrier, "knock_out", num_simulations=30000
            )

            discount = european_result.price - barrier_result.price
            discount_pct = (discount / european_result.price) * 100

            print(f"{barrier:<7} ${barrier_result.price:<9.4f} ${discount:<11.4f} {discount_pct:<9.1f}%")
        
    print(f"KNOCK-IN CALL OPTIONS (only active if barrier hit)")
    print(f"{'Barrier':<8} {'Price':<10} {'vs European':<12} {'Differnce':<10}")

    for barrier in barrier_levels:
        if barrier > base_option.current_stock_price:
            barrier_result = mc_engine.price_barrier_option(
                base_option, barrier, "knock_in", num_simulations=30000
            )

            difference = barrier_result.price - european_result.price

            print(f"${barrier:<7} ${barrier_result.price:<9.4f} ${difference:<11.4f} {'N/A':<10}")

        
    print(f" Barrier Options Insights: ")
    print(f" Knock-out: CHEAPER than European (can become worthless)")
    print(f" Higher barriers = cheaper knock-outs (more likely to be hit)")
    print(f"Knock-in: Usually cheaper (only active if condition met)")
    print(f" Popular in structured products and FX markets")
    print(f" Knock-out + Knock-in approx. equals European (decomposition)")


def demo_performance_comparison():
    print("PERFORMANCE COMPARISON")

    test_option = Option(
        symbol = "PERF_TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )

    # black-scholes timing
    start_time = time.time()

    for _ in range(1000):
        bs_price =  BlackScholesEngine.price_option(test_option)
    bs_time = time.time() - start_time

    # Monte carlo timing
    mc_engine = MonteCarloEngine()
    start_time = time.time()
    mc_result = mc_engine.price_european_option(test_option, num_simulations=10000)
    mc_time = time.time() - start_time

    print(f"Pricing Performance (1000 options):")
    print(f"Black Scholes: {bs_time:.4f} seconds ({bs_time*1000:.2f} microsecond per option")
    print(f"Monte Carlo: {mc_time:.4f} seconds ({mc_time*1000:.2f} millisecond per option)")
    print(f"Speed ratio: Monte Carlo is {mc_time/bs_time:0f}x slower")

    print(f" Performance Trade-offs:")
    print(f" Black Scholes: Microsecond pricing, limited to European options")
    print(f" Monte Carlo: Millisecond pricing, handles ANY option type")
    print(f" Real-time trading: Black-Scholes preferred")
    print(" Risk management: Monte Carlo for complex portfolios")

def main():
    print("MONTE CARLO OPTIONS PRICING ENGINE")
    print("Advanced Quantitative Finance Techniques")

    try:
        # core comparison
        comparison = demo_monte_carlo_vs_black_scholes()

        # show convergence behaviour
        demo_convergence_analysis()

        # price exotic options
        demo_asian_options()
        demo_barrier_options()

        # performance analysis
        demo_performance_comparison()

        print("MONTE CARLO DEMONSTRATION COMPLETE!")
        print(" Successfully implemented Monte Carlo option pricing")
        print(" Validated against Black-Scholes for European options")
        print(" Priced exotic options ( Asian, Barrier) with no closed-form solution")
        print(" Demonstrated convergence and performance characteristics")

    except ImportError as e:
        print(f"Missing dependence: {e}")
        print(" Install: pip install numpy scipy")
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
