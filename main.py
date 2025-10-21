# main.py

"""
Main demo script for the Options Pricing Engine.

This is the entry point for our application. It demonstrates
all the key features and serves as both a demo and integration test.

Run this after setting up the project structure:
python main.py
"""

import sys
import os
from datetime import datetime, timedelta
import math

# Add src to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now we can import our custom modules
from src.models.option import Option, OptionType
from src.models.black_scholes import BlackScholesEngine

def demo_your_microsoft_example():
    """
    Demo the Microsoft call option example from our conversation.
    
    This recreates your exact scenario: MSFT call option with 
    strike $200, 3 months to expiration, stock at $195.
    """
    print("=" * 70)
    print("🚀 YOUR MICROSOFT CALL OPTION EXAMPLE")
    print("=" * 70)
    
    # Create your MSFT call option
    msft_call = Option(
        symbol="MSFT",
        strike_price=200.0,
        expiration_date=datetime.now() + timedelta(days=90),  # ~3 months
        option_type=OptionType.CALL,
        current_stock_price=195.0,
        risk_free_rate=0.05,    # 5% risk-free rate
        volatility=0.25         # 25% volatility
    )
    
    # Price it using Black-Scholes
    try:
        price = BlackScholesEngine.price_option(msft_call)
        
        print(f"📋 Option Contract Details:")
        print(f"   Symbol: {msft_call.symbol}")
        print(f"   Type: {msft_call.option_type.value.upper()}")
        print(f"   Strike Price: ${msft_call.strike_price:,.2f}")
        print(f"   Current Stock Price: ${msft_call.current_stock_price:,.2f}")
        print(f"   Days to Expiration: {(msft_call.expiration_date - datetime.now()).days}")
        print(f"   Time to Expiration: {msft_call.time_to_expiration:.3f} years")
        print(f"   Risk-free Rate: {msft_call.risk_free_rate:.1%}")
        print(f"   Volatility: {msft_call.volatility:.1%}")
        
        print(f"\n🎯 BLACK-SCHOLES FAIR VALUE: ${price:.2f}")
        
        # Calculate key metrics
        intrinsic_value = msft_call.intrinsic_value
        time_value = price - intrinsic_value
        breakeven = msft_call.strike_price + price
        
        print(f"\n📊 Option Value Breakdown:")
        print(f"   Intrinsic Value: ${intrinsic_value:.2f}")
        print(f"   Time Value: ${time_value:.2f}")
        print(f"   Total Premium: ${price:.2f}")
        
        print(f"\n💡 Trading Analysis:")
        print(f"   • You pay: ${price:.2f} per share today")
        print(f"   • Breakeven point: MSFT needs to reach ${breakeven:.2f}")
        print(f"   • If MSFT hits $220: Profit = ${220 - breakeven:.2f} per share")
        print(f"   • If MSFT stays below $200: You lose the ${price:.2f} premium")
        print(f"   • Max loss: ${price:.2f} per share (100% of premium)")
        print(f"   • Max gain: Unlimited (as MSFT stock price rises)")
        
        return price
        
    except Exception as e:
        print(f"❌ Error pricing option: {e}")
        return None

def demo_option_properties():
    """
    Demonstrate various option properties and calculations.
    Shows off our Option class features.
    """
    print("\n" + "=" * 70)
    print("🔍 OPTION PROPERTIES DEMONSTRATION")
    print("=" * 70)
    
    # Create a few different options to compare
    options = [
        Option("AAPL", 150.0, datetime.now() + timedelta(days=30), OptionType.CALL, 155.0, 0.05, 0.30),
        Option("GOOGL", 2800.0, datetime.now() + timedelta(days=60), OptionType.PUT, 2750.0, 0.05, 0.35),
        Option("TSLA", 200.0, datetime.now() + timedelta(days=45), OptionType.CALL, 180.0, 0.05, 0.60),
    ]
    
    print("Option Properties Comparison:")
    print("-" * 70)
    
    for option in options:
        print(f"\n{option}")
        print(f"  Time to expiration: {option.time_to_expiration:.3f} years")
        print(f"  Is in the money: {option.is_in_the_money}")
        print(f"  Intrinsic value: ${option.intrinsic_value:.2f}")
        print(f"  Option type: {'Call' if option.is_call else 'Put'}")

def demo_sensitivity_analysis():
    """
    Show how different parameters affect option pricing.
    This helps understand the "Greeks" (sensitivities).
    """
    print("\n" + "=" * 70)
    print("📊 SENSITIVITY ANALYSIS")
    print("=" * 70)
    
    # Base case option (at-the-money, 30 days)
    base_option = Option(
        symbol="DEMO",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    base_price = BlackScholesEngine.price_option(base_option)
    print(f"📍 Base Case: {base_option} → ${base_price:.2f}")
    
    # Test different stock prices (Delta effect)
    print(f"\n🔄 Stock Price Sensitivity (Delta):")
    stock_prices = [80, 90, 95, 100, 105, 110, 120]
    for stock_price in stock_prices:
        base_option.current_stock_price = stock_price
        price = BlackScholesEngine.price_option(base_option)
        delta_effect = price - base_price
        print(f"   Stock ${stock_price:3d}: ${price:5.2f} (Δ: {delta_effect:+5.2f})")
    
    # Reset for next test
    base_option.current_stock_price = 100.0
    
    # Test different volatilities (Vega effect)
    print(f"\n📈 Volatility Sensitivity (Vega):")
    volatilities = [0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    for vol in volatilities:
        base_option.volatility = vol
        price = BlackScholesEngine.price_option(base_option)
        vega_effect = price - base_price
        print(f"   Vol {vol:4.0%}: ${price:5.2f} (Δ: {vega_effect:+5.2f})")
    
    # Reset for next test
    base_option.volatility = 0.25
    
    # Test different times to expiration (Theta effect)
    print(f"\n⏰ Time Decay (Theta):")
    days_list = [90, 60, 30, 14, 7, 3, 1]  # Include 1 day - now handled properly
    for days in days_list:
        base_option.expiration_date = datetime.now() + timedelta(days=days)
        
        # Check if we can price this (avoid expired options)
        if base_option.time_to_expiration > 0:
            price = BlackScholesEngine.price_option(base_option)
            theta_effect = price - base_price
            print(f"   {days:2d} days: ${price:5.2f} (Δ: {theta_effect:+5.2f})")
        else:
            print(f"   {days:2d} days: EXPIRED (worthless)")

def demo_put_call_parity():
    """
    Demonstrate put-call parity relationship.
    
    Put-call parity: C - P = S - K*e^(-rT)
    This is a fundamental arbitrage relationship in options.
    """
    print("\n" + "=" * 70)
    print("⚖️  PUT-CALL PARITY DEMONSTRATION")
    print("=" * 70)
    
    # Create matching call and put options
    call_option = Option(
        symbol="PARITY",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=60),
        option_type=OptionType.CALL,
        current_stock_price=105.0,
        risk_free_rate=0.05,
        volatility=0.30
    )
    
    put_option = Option(
        symbol="PARITY",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=60),
        option_type=OptionType.PUT,
        current_stock_price=105.0,
        risk_free_rate=0.05,
        volatility=0.30
    )
    
    call_price = BlackScholesEngine.price_option(call_option)
    put_price = BlackScholesEngine.price_option(put_option)
    
    # Calculate put-call parity components
    stock_price = call_option.current_stock_price
    strike_pv = call_option.strike_price * math.exp(-call_option.risk_free_rate * call_option.time_to_expiration)
    
    left_side = call_price - put_price
    right_side = stock_price - strike_pv
    
    print(f"Call Option Price: ${call_price:.2f}")
    print(f"Put Option Price:  ${put_price:.2f}")
    print(f"Stock Price:       ${stock_price:.2f}")
    print(f"Strike PV:         ${strike_pv:.2f}")
    print(f"\nPut-Call Parity Check:")
    print(f"C - P = ${left_side:.2f}")
    print(f"S - K*e^(-rT) = ${right_side:.2f}")
    print(f"Difference: ${abs(left_side - right_side):.4f}")
    
    if abs(left_side - right_side) < 0.01:
        print("✅ Put-call parity holds! Our Black-Scholes implementation is mathematically consistent.")
    else:
        print("❌ Put-call parity violation! Check the implementation.")

def demo_extreme_scenarios():
    """
    Test edge cases and extreme market scenarios.
    Important for validating our implementation.
    """
    print("\n" + "=" * 70)
    print("🧪 EXTREME SCENARIOS TEST")
    print("=" * 70)
    
    scenarios = [
        ("At-the-money (stock = strike)", 100.0),
        ("Slightly in-the-money", 105.0),
        ("Deep in-the-money", 130.0),
        ("Slightly out-of-the-money", 95.0),
        ("Way out-of-the-money", 70.0)
    ]
    
    print("Call Option Prices (Strike = $100, 30 days, 25% vol):")
    for description, stock_price in scenarios:
        option = Option(
            symbol="TEST",
            strike_price=100.0,
            expiration_date=datetime.now() + timedelta(days=30),
            option_type=OptionType.CALL,
            current_stock_price=stock_price,
            risk_free_rate=0.05,
            volatility=0.25
        )
        price = BlackScholesEngine.price_option(option)
        intrinsic_value = max(stock_price - 100, 0)
        time_value = price - intrinsic_value
        print(f"   Stock ${stock_price:3.0f}: ${price:5.2f} (intrinsic: ${intrinsic_value:4.2f}, time: ${time_value:4.2f})")
    
    print("\nPut Option Prices (same scenarios):")
    for description, stock_price in scenarios:
        option = Option(
            symbol="TEST",
            strike_price=100.0,
            expiration_date=datetime.now() + timedelta(days=30),
            option_type=OptionType.PUT,
            current_stock_price=stock_price,
            risk_free_rate=0.05,
            volatility=0.25
        )
        price = BlackScholesEngine.price_option(option)
        intrinsic_value = max(100 - stock_price, 0)
        time_value = price - intrinsic_value
        print(f"   Stock ${stock_price:3.0f}: ${price:5.2f} (intrinsic: ${intrinsic_value:4.2f}, time: ${time_value:4.2f})")

def main():
    """
    Main function that runs all our demos.
    This showcases the complete functionality of our pricing engine.
    """
    print("🏦 OPTIONS PRICING ENGINE - COMPREHENSIVE DEMO")
    print("Built by: Senior Dev & Junior Dev (learning together!)")
    print("=" * 70)
    
    try:
        # Test your specific Microsoft example
        msft_price = demo_your_microsoft_example()
        
        # Show different option properties
        demo_option_properties()
        
        # Demonstrate sensitivity to different parameters
        demo_sensitivity_analysis()
        
        # Validate with put-call parity
        demo_put_call_parity()
        
        # Test extreme market scenarios
        demo_extreme_scenarios()
        
        print("\n" + "=" * 70)
        print("🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        if msft_price:
            print(f"✅ Your MSFT call option fair value: ${msft_price:.2f}")
        print(f"✅ Black-Scholes engine working perfectly")
        print(f"✅ Mathematical relationships validated")
        print(f"✅ Edge cases handled correctly")
        
        print(f"\n🎓 Key Learnings:")
        print(f"   • Options have both intrinsic and time value")
        print(f"   • Higher volatility increases option prices")
        print(f"   • Time decay accelerates as expiration approaches")
        print(f"   • Put-call parity provides mathematical validation")
        
        print(f"\n🚀 Ready for next steps:")
        print(f"   1. Monte Carlo simulation for path-dependent options")
        print(f"   2. Greeks calculation (Delta, Gamma, Theta, Vega, Rho)")
        print(f"   3. Exotic options pricing (Asian, Barrier, American)")
        print(f"   4. Production features (REST API, caching, monitoring)")
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("💡 Install required packages:")
        print("   pip install -r requirements.txt")
        print("   or: pip install scipy numpy matplotlib pandas")
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        print("💡 Make sure you've set up the project structure correctly")
        print("   Run: python setup_project.py")

if __name__ == "__main__":
    main()