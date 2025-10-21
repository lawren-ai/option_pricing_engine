# greeks_demo.py


import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.option import Option, OptionType
from models.black_scholes import BlackScholesEngine
from models.greeks import GreeksCalculator, interpret_greeks

def demo_your_msft_greeks():
    """Calculate Greeks for your MSFT call option"""
    print("=" * 70)
    print("🎯 YOUR MICROSOFT CALL OPTION GREEKS")
    print("=" * 70)
    
    msft_call = Option(
        symbol="MSFT",
        strike_price=200.0,
        expiration_date=datetime.now() + timedelta(days=90),
        option_type=OptionType.CALL,
        current_stock_price=195.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    # Price the option
    price = BlackScholesEngine.price_option(msft_call)
    
    # Calculate Greeks
    greeks = GreeksCalculator.calculate_analytical_greeks(msft_call)
    
    print(f"Option: {msft_call}")
    print(f"Price: ${price:.2f}")
    print(f"\n{greeks}")
    print(f"\n{interpret_greeks(greeks, msft_call)}")
    
    return greeks

def demo_greeks_by_moneyness():
    """Show how Greeks change with moneyness (stock price vs strike)"""
    print("\n" + "=" * 70)
    print("📊 GREEKS BY MONEYNESS")
    print("=" * 70)
    
    print("\nHow Greeks change as stock price moves:")
    print("(Strike = $100, 30 days to expiration, 25% vol)")
    print()
    print(f"{'Stock':>7} {'Price':>7} {'Delta':>7} {'Gamma':>7} {'Vega':>7} {'Theta':>7}")
    print("-" * 60)
    
    stock_prices = [80, 90, 95, 100, 105, 110, 120]
    
    for stock_price in stock_prices:
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
        greeks = GreeksCalculator.calculate_analytical_greeks(option)
        
        print(f"${stock_price:>6.0f} ${price:>6.2f} {greeks.delta:>7.3f} "
              f"{greeks.gamma:>7.4f} {greeks.vega:>7.2f} {greeks.theta:>7.2f}")
    
    print("\n💡 Key Observations:")
    print("   • Delta increases as option goes in-the-money")
    print("   • Gamma peaks at-the-money (most sensitive point)")
    print("   • Vega highest at-the-money")
    print("   • Theta (time decay) also highest at-the-money")

def demo_greeks_vs_time():
    """Show how Greeks evolve as expiration approaches"""
    print("\n" + "=" * 70)
    print("⏰ GREEKS VS TIME TO EXPIRATION")
    print("=" * 70)
    
    print("\nHow Greeks change as expiration approaches:")
    print("(At-the-money: Stock=$100, Strike=$100, 25% vol)")
    print()
    print(f"{'Days':>5} {'Price':>7} {'Delta':>7} {'Gamma':>8} {'Vega':>7} {'Theta':>7}")
    print("-" * 60)
    
    days_list = [90, 60, 30, 14, 7, 3, 1]
    
    for days in days_list:
        option = Option(
            symbol="TIME",
            strike_price=100.0,
            expiration_date=datetime.now() + timedelta(days=days),
            option_type=OptionType.CALL,
            current_stock_price=100.0,
            risk_free_rate=0.05,
            volatility=0.25
        )
        
        price = BlackScholesEngine.price_option(option)
        greeks = GreeksCalculator.calculate_analytical_greeks(option)
        
        print(f"{days:>5d} ${price:>6.2f} {greeks.delta:>7.3f} "
              f"{greeks.gamma:>8.5f} {greeks.vega:>7.2f} {greeks.theta:>7.2f}")
    
    print("\n💡 Key Observations:")
    print("   • Option value decreases (theta decay)")
    print("   • Gamma explodes as expiration nears (high delta risk)")
    print("   • Vega decreases (less time for volatility to matter)")
    print("   • Theta accelerates (faster time decay)")

def demo_greeks_vs_volatility():
    """Show how Greeks change with different volatilities"""
    print("\n" + "=" * 70)
    print("📈 GREEKS VS VOLATILITY")
    print("=" * 70)
    
    print("\nHow Greeks change with implied volatility:")
    print("(At-the-money: Stock=$100, Strike=$100, 30 days)")
    print()
    print(f"{'Vol':>6} {'Price':>7} {'Delta':>7} {'Gamma':>7} {'Vega':>7} {'Theta':>7}")
    print("-" * 60)
    
    volatilities = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60]
    
    for vol in volatilities:
        option = Option(
            symbol="VOL",
            strike_price=100.0,
            expiration_date=datetime.now() + timedelta(days=30),
            option_type=OptionType.CALL,
            current_stock_price=100.0,
            risk_free_rate=0.05,
            volatility=vol
        )
        
        price = BlackScholesEngine.price_option(option)
        greeks = GreeksCalculator.calculate_analytical_greeks(option)
        
        print(f"{vol:>5.0%} ${price:>6.2f} {greeks.delta:>7.3f} "
              f"{greeks.gamma:>7.4f} {greeks.vega:>7.2f} {greeks.theta:>7.2f}")
    
    print("\n💡 Key Observations:")
    print("   • Higher vol = higher option prices (more uncertainty)")
    print("   • Delta approaches 0.5 at-the-money (regardless of vol)")
    print("   • Vega increases with volatility")
    print("   • Theta (time decay) increases with volatility")

def demo_call_vs_put_greeks():
    """Compare Greeks between calls and puts"""
    print("\n" + "=" * 70)
    print("☎️  CALL vs PUT GREEKS")
    print("=" * 70)
    
    call_option = Option(
        symbol="COMPARE",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    put_option = Option(
        symbol="COMPARE",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.PUT,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    call_price = BlackScholesEngine.price_option(call_option)
    put_price = BlackScholesEngine.price_option(put_option)
    
    call_greeks = GreeksCalculator.calculate_analytical_greeks(call_option)
    put_greeks = GreeksCalculator.calculate_analytical_greeks(put_option)
    
    print("\nAt-the-Money Comparison (Stock=$100, Strike=$100):")
    print()
    print(f"{'':20} {'CALL':>12} {'PUT':>12} {'Difference':>12}")
    print("-" * 58)
    print(f"{'Price:':20} ${call_price:>11.2f} ${put_price:>11.2f} ${call_price-put_price:>11.2f}")
    print(f"{'Delta:':20} {call_greeks.delta:>12.4f} {put_greeks.delta:>12.4f} {call_greeks.delta-put_greeks.delta:>12.4f}")
    print(f"{'Gamma:':20} {call_greeks.gamma:>12.6f} {put_greeks.gamma:>12.6f} {call_greeks.gamma-put_greeks.gamma:>12.6f}")
    print(f"{'Vega:':20} {call_greeks.vega:>12.4f} {put_greeks.vega:>12.4f} {call_greeks.vega-put_greeks.vega:>12.4f}")
    print(f"{'Theta:':20} {call_greeks.theta:>12.4f} {put_greeks.theta:>12.4f} {call_greeks.theta-put_greeks.theta:>12.4f}")
    print(f"{'Rho:':20} {call_greeks.rho:>12.4f} {put_greeks.rho:>12.4f} {call_greeks.rho-put_greeks.rho:>12.4f}")
    
    print("\n💡 Key Relationships:")
    print("   • Delta(Call) - Delta(Put) ≈ 1.0 (put-call parity)")
    print("   • Gamma is IDENTICAL for calls and puts")
    print("   • Vega is IDENTICAL for calls and puts")
    print("   • Theta similar magnitude but different signs")
    print("   • Rho has opposite signs (calls +ve, puts -ve)")

def demo_portfolio_greeks():
    """Show how Greeks aggregate in a portfolio"""
    print("\n" + "=" * 70)
    print("📊 PORTFOLIO GREEKS (Risk Management)")
    print("=" * 70)
    
    # Create a portfolio with multiple options
    # Long 100 calls, short 50 puts (bullish strategy)
    
    call_option = Option(
        symbol="PORTFOLIO",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    put_option = Option(
        symbol="PORTFOLIO",
        strike_price=95.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.PUT,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    call_greeks = GreeksCalculator.calculate_analytical_greeks(call_option)
    put_greeks = GreeksCalculator.calculate_analytical_greeks(put_option)
    
    # Portfolio: Long 100 calls, Short 50 puts
    long_calls = 100
    short_puts = -50
    
    portfolio_delta = long_calls * call_greeks.delta + short_puts * put_greeks.delta
    portfolio_gamma = long_calls * call_greeks.gamma + short_puts * put_greeks.gamma
    portfolio_vega = long_calls * call_greeks.vega + short_puts * put_greeks.vega
    portfolio_theta = long_calls * call_greeks.theta + short_puts * put_greeks.theta
    
    print("\nPortfolio Composition:")
    print(f"  • Long {long_calls} calls @ $100 strike")
    print(f"  • Short {abs(short_puts)} puts @ $95 strike")
    
    print("\nPortfolio Greeks:")
    print(f"  Delta: {portfolio_delta:+.2f}")
    print(f"  Gamma: {portfolio_gamma:+.4f}")
    print(f"  Vega:  {portfolio_vega:+.2f}")
    print(f"  Theta: {portfolio_theta:+.2f}")
    
    print("\n💡 Risk Analysis:")
    print(f"  • Net Delta = {portfolio_delta:.0f} → Acts like {portfolio_delta:.0f} shares")
    print(f"  • If stock moves $1: Portfolio {'gains' if portfolio_delta > 0 else 'loses'} ${abs(portfolio_delta):.2f}")
    print(f"  • Daily time decay: ${abs(portfolio_theta):.2f} per day")
    print(f"  • Volatility risk: ${portfolio_vega:.2f} per 1% vol change")
    
    # Calculate hedge
    hedge_shares = -portfolio_delta
    print(f"\n🛡️ Delta Hedge:")
    print(f"  • To neutralize delta: {'Buy' if hedge_shares > 0 else 'Sell'} {abs(hedge_shares):.0f} shares")
    print(f"  • This makes portfolio delta-neutral (hedged against small moves)")

def main():
    """Run all Greeks demonstrations"""
    print("🎓 OPTIONS GREEKS - COMPREHENSIVE ANALYSIS")
    print("Understanding Risk Sensitivities in Options Trading")
    print()
    
    try:
        # Your MSFT example
        demo_your_msft_greeks()
        
        # Comprehensive Greeks analysis
        demo_greeks_by_moneyness()
        demo_greeks_vs_time()
        demo_greeks_vs_volatility()
        demo_call_vs_put_greeks()
        demo_portfolio_greeks()
        
        print("\n" + "=" * 70)
        print("🎉 GREEKS ANALYSIS COMPLETE!")
        print("=" * 70)
        print("✅ Calculated all five main Greeks")
        print("✅ Analyzed Greeks across different scenarios")
        print("✅ Compared calls vs puts")
        print("✅ Demonstrated portfolio risk management")
        
        print("\n🎓 Key Takeaways:")
        print("   • Delta: Directional exposure (like owning stock)")
        print("   • Gamma: Curvature risk (delta changes)")
        print("   • Vega: Volatility risk (IV changes)")
        print("   • Theta: Time decay (value lost daily)")
        print("   • Rho: Interest rate risk (usually small)")
        
        print("\n💼 Real-World Applications:")
        print("   • Market makers use Greeks for hedging")
        print("   • Risk managers monitor portfolio Greeks")
        print("   • Traders use Greeks to select strategies")
        print("   • Regulators require Greek reporting for risk")
        
        print("\n🚀 You now understand:")
        print("   • How to calculate Greeks analytically")
        print("   • How Greeks change with market conditions")
        print("   • How to interpret Greeks for trading")
        print("   • How to aggregate Greeks for portfolios")
        print("   • How to use Greeks for risk management")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()