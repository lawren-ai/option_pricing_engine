"""
Options Pricing Engine - Minimal Version
-----------------------------------------
Compares Black-Scholes vs Monte Carlo pricing

Files required:
- src/models/option.py
- src/models/black_scholes.py
- src/models/monte_carlo.py
- main.py

Author: Lawrence (2025)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from src.models.option import Option, OptionType
from src.models.black_scholes import BlackScholesEngine
from src.models.monte_carlo import MonteCarloEngine


def create_comparison_visualization(option, bs_price, mc_result):
    """
    Create a clean 4-panel comparison visualization
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Colors
    bs_color = '#66c2a5'
    mc_color = '#fc8d62'
    
    # Panel 1: Price Comparison
    methods = ['Black-Scholes\n(Analytical)', 'Monte Carlo\n(Numerical)']
    prices = [bs_price, mc_result.price]
    bars = ax1.bar(methods, prices, color=[bs_color, mc_color], 
                   edgecolor='black', linewidth=2, width=0.6)
    ax1.set_ylabel('Option Price ($)', fontweight='bold', fontsize=11)
    ax1.set_title('Price Comparison', fontweight='bold', fontsize=13)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for bar, price in zip(bars, prices):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${price:.4f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    # Panel 2: Convergence Analysis
    print("\n📊 Running convergence analysis...")
    sim_counts = [1000, 5000, 10000, 25000, 50000, 100000]
    mc_prices = []
    std_errors = []
    
    mc_engine = MonteCarloEngine(random_seed=42)
    for num_sims in sim_counts:
        result = mc_engine.price_european_option(option, num_simulations=num_sims)
        mc_prices.append(result.price)
        std_errors.append(result.standard_error)
    
    # Plot convergence
    ax2.plot(sim_counts, mc_prices, 'o-', color=mc_color, linewidth=2.5, 
            markersize=8, label='Monte Carlo', markeredgecolor='black')
    ax2.axhline(y=bs_price, color=bs_color, linestyle='--', linewidth=3,
               label=f'Black-Scholes: ${bs_price:.4f}')
    
    # Add confidence bands
    mc_prices_arr = np.array(mc_prices)
    std_errors_arr = np.array(std_errors)
    ax2.fill_between(sim_counts, 
                     mc_prices_arr - 1.96*std_errors_arr,
                     mc_prices_arr + 1.96*std_errors_arr,
                     alpha=0.3, color=mc_color, label='95% Confidence')
    
    ax2.set_xlabel('Number of Simulations', fontweight='bold', fontsize=11)
    ax2.set_ylabel('Option Price ($)', fontweight='bold', fontsize=11)
    ax2.set_title('Monte Carlo Convergence to Black-Scholes', 
                  fontweight='bold', fontsize=13)
    ax2.set_xscale('log')
    ax2.legend(loc='best', fontsize=10, framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Panel 3: Error Analysis
    errors_abs = [abs(p - bs_price) for p in mc_prices]
    errors_pct = [(abs(p - bs_price) / bs_price) * 100 for p in mc_prices]
    
    ax3_twin = ax3.twinx()
    
    line1 = ax3.plot(sim_counts, errors_abs, 'o-', color='#e78ac3', 
                     linewidth=2.5, markersize=8, label='Absolute Error ($)',
                     markeredgecolor='black')
    line2 = ax3_twin.plot(sim_counts, errors_pct, 's-', color='#a6d854', 
                          linewidth=2.5, markersize=8, label='Relative Error (%)',
                          markeredgecolor='black')
    
    ax3.set_xlabel('Number of Simulations', fontweight='bold', fontsize=11)
    ax3.set_ylabel('Absolute Error ($)', fontweight='bold', fontsize=11, color='#e78ac3')
    ax3_twin.set_ylabel('Relative Error (%)', fontweight='bold', fontsize=11, color='#a6d854')
    ax3.set_title('Pricing Error vs Simulations', fontweight='bold', fontsize=13)
    ax3.set_xscale('log')
    ax3.tick_params(axis='y', labelcolor='#e78ac3')
    ax3_twin.tick_params(axis='y', labelcolor='#a6d854')
    ax3.grid(True, alpha=0.3, linestyle='--')
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='upper right', fontsize=10, framealpha=0.9)
    
    # Panel 4: Confidence Interval Comparison
    ci_lower, ci_upper = mc_result.confidence_interval_95
    
    # Black-Scholes point estimate
    ax4.barh(['Black-Scholes'], [bs_price], height=0.4, color=bs_color, 
             alpha=0.8, edgecolor='black', linewidth=2, label='BS Price')
    
    # Monte Carlo with error bars
    ax4.barh(['Monte Carlo'], [mc_result.price], height=0.4, color=mc_color, 
             alpha=0.8, edgecolor='black', linewidth=2, label='MC Price')
    ax4.errorbar([mc_result.price], ['Monte Carlo'], 
                xerr=[[mc_result.price - ci_lower], [ci_upper - mc_result.price]],
                fmt='none', color='red', linewidth=3, capsize=8, 
                label='95% CI', zorder=10, capthick=2)
    
    ax4.set_xlabel('Option Price ($)', fontweight='bold', fontsize=11)
    ax4.set_title('Monte Carlo Uncertainty vs Black-Scholes', 
                  fontweight='bold', fontsize=13)
    ax4.legend(loc='lower right', fontsize=10, framealpha=0.9)
    ax4.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Overall title
    fig.suptitle(f'{option.symbol} {option.option_type.value.upper()} Option: '
                f'Analytical vs Numerical Pricing Comparison\n'
                f'Stock: ${option.current_stock_price:.2f} | Strike: ${option.strike_price:.2f} | '
                f'Vol: {option.volatility*100:.1f}% | {(option.expiration_date - datetime.now()).days} days',
                fontsize=14, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    return fig


def print_convergence_table(option, sim_counts=[1000, 5000, 10000, 50000, 100000]):
    """Print detailed convergence analysis table"""
    print("\n" + "=" * 95)
    print("📊 MONTE CARLO CONVERGENCE ANALYSIS")
    print("=" * 95)
    
    bs_price = BlackScholesEngine.price_option(option)
    mc_engine = MonteCarloEngine(random_seed=42)
    
    print(f"\n{'Simulations':<13} {'MC Price':<12} {'BS Price':<12} {'Error ($)':<12} "
          f"{'Error (%)':<10} {'Std Error':<12} {'Time (s)':<10}")
    print("-" * 95)
    
    for num_sims in sim_counts:
        result = mc_engine.price_european_option(option, num_simulations=num_sims)
        error = abs(result.price - bs_price)
        rel_error = (error / bs_price) * 100
        
        print(f"{num_sims:<13,} ${result.price:<11.4f} ${bs_price:<11.4f} "
              f"${error:<11.4f} {rel_error:<9.2f}% ${result.standard_error:<11.6f} "
              f"{result.simulation_time:<10.3f}")
    
    print("=" * 95)


def main():
    print("\n" + "=" * 70)
    print("🏦 OPTIONS PRICING ENGINE")
    print("Black-Scholes vs Monte Carlo Comparison")
    print("=" * 70)

    try:
        # ---- User Inputs ----
        print("\n📝 Enter option parameters (press Enter for defaults):\n")
        
        symbol = input("Stock symbol [AAPL]: ").upper().strip() or "AAPL"
        S = float(input("Current stock price [$150]: ") or 150)
        K = float(input("Strike price [$155]: ") or 155)
        days_to_exp = int(input("Days to expiration [30]: ") or 30)
        r = float(input("Risk-free rate [0.05 = 5%]: ") or 0.05)
        sigma = float(input("Volatility [0.25 = 25%]: ") or 0.25)
        opt_type = input("Option type (call/put) [call]: ").lower().strip() or "call"

        # ---- Build Option ----
        expiration_date = datetime.now() + timedelta(days=days_to_exp)
        option = Option(
            symbol=symbol,
            strike_price=K,
            expiration_date=expiration_date,
            option_type=OptionType.CALL if opt_type == "call" else OptionType.PUT,
            current_stock_price=S,
            risk_free_rate=r,
            volatility=sigma
        )

        # ---- Price with Both Methods ----
        print("\n" + "=" * 70)
        print("⏳ Calculating prices...")
        print("=" * 70)
        
        print("\n1️⃣ Black-Scholes (analytical)...")
        bs_price = BlackScholesEngine.price_option(option)
        print(f"   ✅ Completed in <1 microsecond")
        
        print("\n2️⃣ Monte Carlo (100,000 simulations)...")
        mc_engine = MonteCarloEngine()
        mc_result = mc_engine.price_european_option(option, num_simulations=100_000)
        print(f"   ✅ Completed in {mc_result.simulation_time:.3f} seconds")

        # ---- Display Results ----
        print("\n" + "=" * 70)
        print(f"📊 PRICING RESULTS - {symbol} {opt_type.upper()}")
        print("=" * 70)
        
        print("\n📋 Option Details:")
        print(f"   Stock Price:       ${S:.2f}")
        print(f"   Strike Price:      ${K:.2f}")
        print(f"   Days to Expiry:    {days_to_exp}")
        print(f"   Volatility:        {sigma*100:.1f}%")
        print(f"   Risk-free Rate:    {r*100:.1f}%")
        print(f"   Intrinsic Value:   ${option.intrinsic_value:.2f}")
        
        print("\n💰 Pricing Results:")
        print(f"   Black-Scholes:     ${bs_price:.4f}")
        print(f"   Monte Carlo:       ${mc_result.price:.4f}")
        print(f"   Standard Error:    ±${mc_result.standard_error:.6f}")
        print(f"   95% Confidence:    [${mc_result.confidence_interval_95[0]:.4f}, "
              f"${mc_result.confidence_interval_95[1]:.4f}]")
        
        print("\n📉 Error Analysis:")
        error_abs = abs(bs_price - mc_result.price)
        error_pct = (error_abs / bs_price) * 100
        print(f"   Absolute Error:    ${error_abs:.4f}")
        print(f"   Relative Error:    {error_pct:.3f}%")
        
        print("\n⚡ Performance:")
        print(f"   BS Time:           ~0.001 ms (instant)")
        print(f"   MC Time:           {mc_result.simulation_time*1000:.1f} ms")
        print(f"   Speed Ratio:       MC is ~{mc_result.simulation_time*1_000_000:.0f}x slower")
        
        print("=" * 70)

        # ---- Convergence Analysis ----
        print_convergence_table(option)

        # ---- Create Visualizations ----
        print("\n📈 Generating comparison visualizations...")
        fig = create_comparison_visualization(option, bs_price, mc_result)
        
        # Save figure
        filename = f'{symbol}_BS_vs_MC_comparison.png'
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved: {filename}")
        
        plt.show()

        # ---- Key Insights ----
        print("\n" + "=" * 70)
        print("💡 KEY INSIGHTS")
        print("=" * 70)
        
        if error_pct < 0.5:
            verdict = "✅ Excellent! MC matches BS within 0.5%"
        elif error_pct < 1.0:
            verdict = "✅ Very Good! MC matches BS within 1%"
        elif error_pct < 2.0:
            verdict = "✅ Good! MC matches BS within 2%"
        elif error_pct < 5.0:
            verdict = "⚠️  Acceptable. MC within 5% of BS"
        else:
            verdict = "❌ Large discrepancy. Try more simulations"
        
        print(f"\n{verdict}")
        print(f"\n🎯 Method Comparison:")
        print(f"   Black-Scholes:")
        print(f"      • Speed: Instant (~1 microsecond)")
        print(f"      • Accuracy: Exact (analytical solution)")
        print(f"      • Limitations: European options only")
        print(f"   ")
        print(f"   Monte Carlo:")
        print(f"      • Speed: {mc_result.simulation_time:.3f} seconds for 100k paths")
        print(f"      • Accuracy: Converges to BS with more simulations")
        print(f"      • Advantages: Can price ANY option type")
        
        print(f"\n📚 When to Use:")
        print(f"   • Use Black-Scholes: European options, need speed, real-time pricing")
        print(f"   • Use Monte Carlo: Exotic options, path-dependent, no closed-form solution")
        
        print("=" * 70)
        print("\n✅ Analysis complete!\n")

    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n⚠️ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()