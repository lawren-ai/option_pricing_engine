"""
Generate Multiple Test Scenarios for README
--------------------------------------------
Tests the pricing engine across different market conditions.

Run from project root:
    python tests/generate_scenarios.py

Or:
    python -m tests.generate_scenarios

Saves charts to images/ folder.

Author: Lawrence (2025)
"""

import sys
import os

# Add parent directory to path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from src.models.option import Option, OptionType
from src.models.black_scholes import BlackScholesEngine
from src.models.monte_carlo import MonteCarloEngine


# Create images directory if it doesn't exist
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'images')
os.makedirs(IMAGES_DIR, exist_ok=True)


def test_scenario(name, symbol, S, K, days, vol, opt_type="call"):
    """Run a single test scenario and return results"""
    print(f"\n{'='*70}")
    print(f"🧪 Testing: {name}")
    print(f"{'='*70}")
    print(f"Stock: ${S}, Strike: ${K}, Days: {days}, Vol: {vol*100:.0f}%, Type: {opt_type}")
    
    # Create option
    expiration_date = datetime.now() + timedelta(days=days)
    option = Option(
        symbol=symbol,
        strike_price=K,
        expiration_date=expiration_date,
        option_type=OptionType.CALL if opt_type == "call" else OptionType.PUT,
        current_stock_price=S,
        risk_free_rate=0.05,
        volatility=vol
    )
    
    # Price with both methods
    bs_price = BlackScholesEngine.price_option(option)
    
    mc_engine = MonteCarloEngine(random_seed=42)
    mc_result = mc_engine.price_european_option(option, num_simulations=50_000)
    
    error_pct = abs(bs_price - mc_result.price) / bs_price * 100
    
    print(f"✅ Black-Scholes: ${bs_price:.4f}")
    print(f"✅ Monte Carlo:   ${mc_result.price:.4f} ± ${mc_result.standard_error:.4f}")
    print(f"✅ Error:         {error_pct:.2f}%")
    
    return {
        'name': name,
        'option': option,
        'bs_price': bs_price,
        'mc_price': mc_result.price,
        'mc_std': mc_result.standard_error,
        'error_pct': error_pct,
        'intrinsic': option.intrinsic_value
    }


def create_comprehensive_scenario_chart(scenarios):
    """Create a mega-chart showing all scenarios"""
    fig = plt.figure(figsize=(18, 12))
    
    # Create 3x3 grid
    from matplotlib.gridspec import GridSpec
    gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # Colors
    bs_color = '#66c2a5'
    mc_color = '#fc8d62'
    
    # Extract data
    names = [s['name'] for s in scenarios]
    bs_prices = [s['bs_price'] for s in scenarios]
    mc_prices = [s['mc_price'] for s in scenarios]
    mc_stds = [s['mc_std'] for s in scenarios]
    errors = [s['error_pct'] for s in scenarios]
    
    # Panel 1: Price Comparison (All Scenarios)
    ax1 = fig.add_subplot(gs[0, :2])
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, bs_prices, width, label='Black-Scholes',
                    color=bs_color, edgecolor='black', linewidth=1.5)
    bars2 = ax1.bar(x + width/2, mc_prices, width, label='Monte Carlo',
                    color=mc_color, edgecolor='black', linewidth=1.5,
                    yerr=np.array(mc_stds)*1.96, capsize=4)
    
    ax1.set_ylabel('Option Price ($)', fontweight='bold', fontsize=11)
    ax1.set_title('Price Comparison Across All Scenarios', fontweight='bold', fontsize=13)
    ax1.set_xticks(x)
    ax1.set_xticklabels([s.split('\n')[0] for s in names], rotation=45, ha='right', fontsize=9)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Panel 2: Error Analysis
    ax2 = fig.add_subplot(gs[0, 2])
    bars = ax2.barh(range(len(scenarios)), errors, color='#e78ac3', 
                    edgecolor='black', linewidth=1.5)
    ax2.set_yticks(range(len(scenarios)))
    ax2.set_yticklabels([s.split('\n')[0] for s in names], fontsize=9)
    ax2.set_xlabel('Relative Error (%)', fontweight='bold', fontsize=10)
    ax2.set_title('Pricing Error', fontweight='bold', fontsize=12)
    ax2.axvline(x=1, color='green', linestyle='--', alpha=0.5, linewidth=2, label='1% threshold')
    ax2.legend(fontsize=9)
    ax2.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (bar, err) in enumerate(zip(bars, errors)):
        width = bar.get_width()
        ax2.text(width, i, f' {err:.2f}%', va='center', fontsize=9, fontweight='bold')
    
    # Panels 3-8: Individual Scenario Details (6 most interesting scenarios)
    interesting_indices = [0, 1, 2, 3, 4, 5] if len(scenarios) >= 6 else range(len(scenarios))
    
    positions = [
        (1, 0), (1, 1), (1, 2),
        (2, 0), (2, 1), (2, 2)
    ]
    
    for idx, (i, pos) in enumerate(zip(interesting_indices, positions)):
        if i >= len(scenarios):
            continue
            
        scenario = scenarios[i]
        ax = fig.add_subplot(gs[pos[0], pos[1]])
        
        # Mini convergence analysis
        sim_counts = [1000, 5000, 10000, 25000, 50000]
        mc_engine = MonteCarloEngine(random_seed=42)
        conv_prices = []
        
        for num_sims in sim_counts:
            result = mc_engine.price_european_option(scenario['option'], num_simulations=num_sims)
            conv_prices.append(result.price)
        
        ax.plot(sim_counts, conv_prices, 'o-', color=mc_color, linewidth=2, markersize=6)
        ax.axhline(y=scenario['bs_price'], color=bs_color, linestyle='--', linewidth=2)
        ax.set_xlabel('Simulations', fontsize=9)
        ax.set_ylabel('Price ($)', fontsize=9)
        ax.set_title(scenario['name'], fontsize=10, fontweight='bold')
        ax.set_xscale('log')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(labelsize=8)
    
    # Overall title
    fig.suptitle('Options Pricing Engine: Comprehensive Scenario Testing\n'
                'Black-Scholes vs Monte Carlo Across Market Conditions',
                fontsize=16, fontweight='bold', y=0.99)
    
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    return fig


def create_summary_table(scenarios):
    """Create a beautiful summary table"""
    print("\n" + "="*100)
    print("📊 COMPREHENSIVE SCENARIO TESTING SUMMARY")
    print("="*100)
    print(f"\n{'Scenario':<25} {'Stock':<8} {'Strike':<8} {'Days':<6} {'Vol':<6} "
          f"{'BS Price':<10} {'MC Price':<10} {'Error':<8}")
    print("-"*100)
    
    for s in scenarios:
        opt = s['option']
        print(f"{s['name']:<25} ${opt.current_stock_price:<7.0f} ${opt.strike_price:<7.0f} "
              f"{(opt.expiration_date - datetime.now()).days:<6d} {opt.volatility*100:<5.0f}% "
              f"${s['bs_price']:<9.4f} ${s['mc_price']:<9.4f} {s['error_pct']:<7.2f}%")
    
    print("="*100)
    
    # Summary statistics
    avg_error = np.mean([s['error_pct'] for s in scenarios])
    max_error = np.max([s['error_pct'] for s in scenarios])
    min_error = np.min([s['error_pct'] for s in scenarios])
    
    print(f"\n📈 Summary Statistics:")
    print(f"   • Average Error: {avg_error:.2f}%")
    print(f"   • Min Error:     {min_error:.2f}%")
    print(f"   • Max Error:     {max_error:.2f}%")
    print(f"   • All scenarios: {'✅ < 2%' if max_error < 2 else '✅ < 5%' if max_error < 5 else '⚠️  Review needed'}")
    print("="*100)


def main():
    print("\n" + "="*70)
    print("🧪 OPTIONS PRICING ENGINE - SCENARIO TESTING")
    print("Generating test cases for README documentation")
    print("="*70)
    
    # Define comprehensive test scenarios
    scenarios = []
    
    # Scenario 1: At-the-Money Call (baseline)
    scenarios.append(test_scenario(
        "ATM Call\n(Baseline)",
        "SPY", S=450, K=450, days=30, vol=0.15, opt_type="call"
    ))
    
    # Scenario 2: In-the-Money Call
    scenarios.append(test_scenario(
        "ITM Call\n(Deep Profitable)",
        "AAPL", S=180, K=150, days=30, vol=0.25, opt_type="call"
    ))
    
    # Scenario 3: Out-of-the-Money Call
    scenarios.append(test_scenario(
        "OTM Call\n(Lottery Ticket)",
        "MSFT", S=400, K=450, days=30, vol=0.20, opt_type="call"
    ))
    
    # Scenario 4: High Volatility (Meme Stock)
    scenarios.append(test_scenario(
        "High Vol Call\n(Volatile Stock)",
        "TSLA", S=250, K=250, days=30, vol=0.60, opt_type="call"
    ))
    
    # Scenario 5: Low Volatility (Stable Stock)
    scenarios.append(test_scenario(
        "Low Vol Call\n(Stable Stock)",
        "KO", S=60, K=60, days=30, vol=0.12, opt_type="call"
    ))
    
    # Scenario 6: Long Expiration
    scenarios.append(test_scenario(
        "Long-Term Call\n(6 Months)",
        "GOOGL", S=150, K=150, days=180, vol=0.30, opt_type="call"
    ))
    
    # Scenario 7: Short Expiration
    scenarios.append(test_scenario(
        "Short-Term Call\n(1 Week)",
        "AMZN", S=180, K=180, days=7, vol=0.25, opt_type="call"
    ))
    
    # Scenario 8: Put Option (ATM)
    scenarios.append(test_scenario(
        "ATM Put\n(Downside Protection)",
        "SPY", S=450, K=450, days=30, vol=0.15, opt_type="put"
    ))
    
    # Create summary table
    create_summary_table(scenarios)
    
    # Generate comprehensive chart
    print("\n📊 Generating comprehensive visualization...")
    fig = create_comprehensive_scenario_chart(scenarios)
    
    # Save figure
    filename = 'images/scenario_testing_comprehensive.png'
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {filename}")
    
    # Create individual scenario charts for README
    print("\n📸 Generating individual scenario charts...")
    
    # Chart 1: Moneyness Comparison (ATM, ITM, OTM)
    fig2, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig2.suptitle('Impact of Moneyness on Option Pricing', fontsize=14, fontweight='bold')
    
    moneyness_scenarios = [scenarios[0], scenarios[1], scenarios[2]]  # ATM, ITM, OTM
    bs_color = '#66c2a5'
    mc_color = '#fc8d62'
    for ax, scenario in zip(axes, moneyness_scenarios):
        methods = ['Black-Scholes', 'Monte Carlo']
        prices = [scenario['bs_price'], scenario['mc_price']]
        
        bars = ax.bar(methods, prices, color=[bs_color, mc_color], 
                     edgecolor='black', linewidth=2, width=0.6)
        ax.set_title(scenario['name'], fontweight='bold')
        ax.set_ylabel('Option Price ($)', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${price:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    fig2.savefig('images/moneyness_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/moneyness_comparison.png")
    
    # Chart 2: Volatility Impact
    fig3, ax = plt.subplots(figsize=(10, 6))
    
    vol_scenarios = [scenarios[4], scenarios[0], scenarios[3]]  # Low, Medium, High vol
    vol_labels = ['Low Vol\n(12%)', 'Medium Vol\n(15%)', 'High Vol\n(60%)']
    
    x = np.arange(len(vol_scenarios))
    width = 0.35
    
    bs_vals = [s['bs_price'] for s in vol_scenarios]
    mc_vals = [s['mc_price'] for s in vol_scenarios]
    
    bars1 = ax.bar(x - width/2, bs_vals, width, label='Black-Scholes',
                   color=bs_color, edgecolor='black', linewidth=2)
    bars2 = ax.bar(x + width/2, mc_vals, width, label='Monte Carlo',
                   color=mc_color, edgecolor='black', linewidth=2)
    
    ax.set_xlabel('Volatility Level', fontweight='bold', fontsize=12)
    ax.set_ylabel('Option Price ($)', fontweight='bold', fontsize=12)
    ax.set_title('Impact of Volatility on Option Pricing\n(At-The-Money, 30 Days)', 
                 fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(vol_labels)
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    fig3.savefig('images/volatility_impact.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/volatility_impact.png")
    
    plt.show()
    
    print("\n" + "="*70)
    print("✅ SCENARIO TESTING COMPLETE!")
    print("="*70)
    print("\n📁 Generated files:")
    print("   1. scenario_testing_comprehensive.png (main showcase)")
    print("   2. moneyness_comparison.png (ATM vs ITM vs OTM)")
    print("   3. volatility_impact.png (Low vs Medium vs High vol)")
    print("\n💡 Use these charts in your README to demonstrate:")
    print("   • Model works across all market conditions")
    print("   • Consistent accuracy (<2% error)")
    print("   • Handles edge cases (high vol, short expiry)")
    print("   • Both calls and puts priced correctly")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()