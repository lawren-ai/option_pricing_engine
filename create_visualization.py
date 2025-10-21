# create_visualizations.py

"""
Generate professional visualizations for README and presentations.

Creates 4 key charts:
1. Greeks evolution over time
2. Monte Carlo convergence analysis
3. Option price surface (moneyness vs time)
4. Portfolio risk dashboard
"""

import sys
import os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.option import Option, OptionType
from models.black_scholes import BlackScholesEngine
from models.monte_carlo import MonteCarloEngine
from models.greeks import GreeksCalculator

# Set professional style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['legend.fontsize'] = 9

def create_greeks_evolution_chart():
    """
    Chart 1: How Greeks change as expiration approaches.
    This is the most important chart for understanding option behavior.
    """
    print("📊 Creating Greeks Evolution Chart...")
    
    days_range = list(range(90, 0, -1))  # 90 days down to 1 day
    
    deltas = []
    gammas = []
    vegas = []
    thetas = []
    prices = []
    
    for days in days_range:
        option = Option(
            symbol="DEMO",
            strike_price=100.0,
            expiration_date=datetime.now() + timedelta(days=days),
            option_type=OptionType.CALL,
            current_stock_price=100.0,
            risk_free_rate=0.05,
            volatility=0.25
        )
        
        price = BlackScholesEngine.price_option(option)
        greeks = GreeksCalculator.calculate_analytical_greeks(option)
        
        prices.append(price)
        deltas.append(greeks.delta)
        gammas.append(greeks.gamma * 100)  # Scale for visibility
        vegas.append(greeks.vega)
        thetas.append(abs(greeks.theta))  # Absolute value for clarity
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Greeks Evolution: At-The-Money Call Option (Strike=$100, Stock=$100, Vol=25%)', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # Option Price
    ax1.plot(days_range, prices, 'b-', linewidth=2.5, label='Option Price')
    ax1.fill_between(days_range, prices, alpha=0.3)
    ax1.set_xlabel('Days to Expiration')
    ax1.set_ylabel('Option Price ($)')
    ax1.set_title('Option Value Decay', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axvline(x=30, color='r', linestyle='--', alpha=0.5, label='30 Days')
    ax1.legend()
    
    # Delta
    ax2.plot(days_range, deltas, 'g-', linewidth=2.5, label='Delta')
    ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Delta = 0.5')
    ax2.set_xlabel('Days to Expiration')
    ax2.set_ylabel('Delta')
    ax2.set_title('Delta Evolution (Stock Sensitivity)', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    ax2.set_ylim([0.48, 0.58])
    
    # Gamma (scaled x100 for visibility)
    ax3.plot(days_range, gammas, 'orange', linewidth=2.5, label='Gamma × 100')
    ax3.fill_between(days_range, gammas, alpha=0.3, color='orange')
    ax3.set_xlabel('Days to Expiration')
    ax3.set_ylabel('Gamma × 100')
    ax3.set_title('Gamma Explosion Near Expiration (⚠️ Rehedging Risk)', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # Theta (absolute value)
    ax4.plot(days_range, thetas, 'r-', linewidth=2.5, label='|Theta|')
    ax4.fill_between(days_range, thetas, alpha=0.3, color='red')
    ax4.set_xlabel('Days to Expiration')
    ax4.set_ylabel('Daily Time Decay ($)')
    ax4.set_title('Time Decay Acceleration (Value Lost Per Day)', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('images/greeks_evolution.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/greeks_evolution.png")
    plt.close()

def create_monte_carlo_convergence_chart():
    """
    Chart 2: Monte Carlo convergence analysis.
    Shows how accuracy improves with more simulations.
    """
    print("📊 Creating Monte Carlo Convergence Chart...")
    
    option = Option(
        symbol="CONVERGENCE",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    # Black-Scholes benchmark
    bs_price = BlackScholesEngine.price_option(option)
    
    # Test different simulation counts
    sim_counts = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    mc_prices = []
    std_errors = []
    times = []
    
    mc_engine = MonteCarloEngine(random_seed=42)
    
    for num_sims in sim_counts:
        result = mc_engine.price_european_option(option, num_simulations=num_sims)
        mc_prices.append(result.price)
        std_errors.append(result.standard_error)
        times.append(result.simulation_time)
    
    # Create figure
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Monte Carlo Convergence Analysis', fontsize=16, fontweight='bold')
    
    # Price convergence
    ax1.plot(sim_counts, mc_prices, 'bo-', linewidth=2, markersize=8, label='Monte Carlo')
    ax1.axhline(y=bs_price, color='r', linestyle='--', linewidth=2, label=f'Black-Scholes: ${bs_price:.4f}')
    ax1.fill_between(sim_counts, 
                      [p - 1.96*se for p, se in zip(mc_prices, std_errors)],
                      [p + 1.96*se for p, se in zip(mc_prices, std_errors)],
                      alpha=0.3, label='95% Confidence Interval')
    ax1.set_xlabel('Number of Simulations')
    ax1.set_ylabel('Option Price ($)')
    ax1.set_title('Price Convergence to Black-Scholes', fontweight='bold')
    ax1.set_xscale('log')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Error vs simulations
    errors = [abs(mc - bs_price) / bs_price * 100 for mc in mc_prices]
    ax2.plot(sim_counts, errors, 'ro-', linewidth=2, markersize=8)
    ax2.axhline(y=1.0, color='g', linestyle='--', alpha=0.5, label='1% Error')
    ax2.set_xlabel('Number of Simulations')
    ax2.set_ylabel('Relative Error (%)')
    ax2.set_title('Error Decreases with √n', fontweight='bold')
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # Time vs accuracy trade-off
    ax3.scatter(times, errors, s=200, c=sim_counts, cmap='viridis', alpha=0.7, edgecolors='black')
    for i, txt in enumerate(sim_counts):
        ax3.annotate(f'{txt:,}', (times[i], errors[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=8)
    ax3.set_xlabel('Computation Time (seconds)')
    ax3.set_ylabel('Relative Error (%)')
    ax3.set_title('Speed vs Accuracy Trade-off', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    cbar = plt.colorbar(ax3.collections[0], ax=ax3, label='Simulations')
    
    plt.tight_layout()
    plt.savefig('images/monte_carlo_convergence.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/monte_carlo_convergence.png")
    plt.close()

def create_price_surface_chart():
    """
    Chart 3: 3D surface showing option price vs stock price and time.
    Classic visualization used in trading floors.
    """
    print("📊 Creating Option Price Surface Chart...")
    
    from mpl_toolkits.mplot3d import Axes3D
    
    # Create grid
    stock_prices = np.linspace(80, 120, 30)
    days_to_exp = np.linspace(1, 90, 30)
    
    X, Y = np.meshgrid(stock_prices, days_to_exp)
    Z = np.zeros_like(X)
    
    # Calculate prices for each point
    for i in range(len(days_to_exp)):
        for j in range(len(stock_prices)):
            option = Option(
                symbol="SURFACE",
                strike_price=100.0,
                expiration_date=datetime.now() + timedelta(days=int(days_to_exp[i])),
                option_type=OptionType.CALL,
                current_stock_price=stock_prices[j],
                risk_free_rate=0.05,
                volatility=0.25
            )
            Z[i, j] = BlackScholesEngine.price_option(option)
    
    # Create 3D plot
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.9, edgecolor='none')
    
    ax.set_xlabel('Stock Price ($)', fontsize=12, labelpad=10)
    ax.set_ylabel('Days to Expiration', fontsize=12, labelpad=10)
    ax.set_zlabel('Option Price ($)', fontsize=12, labelpad=10)
    ax.set_title('Call Option Price Surface\n(Strike=$100, Vol=25%)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Add colorbar
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Option Price ($)')
    
    # Set viewing angle
    ax.view_init(elev=25, azim=45)
    
    plt.tight_layout()
    plt.savefig('images/price_surface.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/price_surface.png")
    plt.close()

def create_portfolio_dashboard():
    """
    Chart 4: Portfolio risk dashboard showing multiple metrics.
    Shows practical application for risk management.
    """
    print("📊 Creating Portfolio Risk Dashboard...")
    
    # Define portfolio
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
    
    # Calculate Greeks
    call_greeks = GreeksCalculator.calculate_analytical_greeks(call_option)
    put_greeks = GreeksCalculator.calculate_analytical_greeks(put_option)
    
    # Portfolio positions
    long_calls = 100
    short_puts = -50
    
    # Portfolio Greeks
    portfolio_delta = long_calls * call_greeks.delta + short_puts * put_greeks.delta
    portfolio_gamma = long_calls * call_greeks.gamma + short_puts * put_greeks.gamma
    portfolio_vega = long_calls * call_greeks.vega + short_puts * put_greeks.vega
    portfolio_theta = long_calls * call_greeks.theta + short_puts * put_greeks.theta
    
    # Create dashboard
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # Title
    fig.suptitle('Portfolio Risk Dashboard\nLong 100 Calls ($100) | Short 50 Puts ($95)', 
                 fontsize=16, fontweight='bold')
    
    # Greeks gauge charts
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.barh(['Delta'], [portfolio_delta], color='green' if portfolio_delta > 0 else 'red')
    ax1.set_xlim([-100, 100])
    ax1.set_title('Net Delta', fontweight='bold')
    ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax1.text(portfolio_delta, 0, f'{portfolio_delta:.1f}', 
             ha='left' if portfolio_delta > 0 else 'right', va='center', fontweight='bold')
    
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.barh(['Gamma'], [portfolio_gamma], color='orange')
    ax2.set_xlim([0, 10])
    ax2.set_title('Net Gamma', fontweight='bold')
    ax2.text(portfolio_gamma, 0, f'{portfolio_gamma:.2f}', ha='left', va='center', fontweight='bold')
    
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.barh(['Vega'], [portfolio_vega], color='blue')
    ax3.set_xlim([0, 15])
    ax3.set_title('Net Vega', fontweight='bold')
    ax3.text(portfolio_vega, 0, f'{portfolio_vega:.1f}', ha='left', va='center', fontweight='bold')
    
    # P&L scenarios
    ax4 = fig.add_subplot(gs[1, :])
    stock_moves = np.linspace(-10, 10, 41)
    pnls = []
    
    for move in stock_moves:
        new_stock = 100 + move
        
        # Approximate P&L using delta and gamma
        pnl = (portfolio_delta * move + 
               0.5 * portfolio_gamma * move**2 +
               portfolio_theta)  # One day theta
        pnls.append(pnl)
    
    ax4.plot(stock_moves, pnls, 'b-', linewidth=3, label='Estimated P&L')
    ax4.fill_between(stock_moves, pnls, alpha=0.3)
    ax4.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax4.axvline(x=0, color='black', linestyle='--', linewidth=1)
    ax4.set_xlabel('Stock Price Move ($)')
    ax4.set_ylabel('Estimated P&L ($)')
    ax4.set_title('Portfolio P&L Scenario Analysis (1 Day)', fontweight='bold', fontsize=12)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    # Risk metrics table
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('tight')
    ax5.axis('off')
    
    risk_data = [
        ['Metric', 'Value', 'Interpretation'],
        ['Net Delta', f'{portfolio_delta:.2f}', f'Acts like {portfolio_delta:.0f} shares'],
        ['Net Gamma', f'{portfolio_gamma:.4f}', 'Delta changes per $1 move'],
        ['Net Vega', f'{portfolio_vega:.2f}', 'P&L per 1% vol change'],
        ['Net Theta', f'{portfolio_theta:.2f}', f'Loses ${abs(portfolio_theta):.2f}/day'],
        ['Daily Theta Loss', f'${abs(portfolio_theta):.2f}', f'${abs(portfolio_theta)*30:.2f}/month'],
        ['Hedge Required', f'Sell {abs(int(portfolio_delta))} shares', 'To achieve delta neutrality']
    ]
    
    table = ax5.table(cellText=risk_data, loc='center', cellLoc='left',
                      colWidths=[0.2, 0.2, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Style header row
    for i in range(3):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(risk_data)):
        for j in range(3):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
    
    plt.savefig('images/portfolio_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/portfolio_dashboard.png")
    plt.close()

def create_comparison_chart():
    """
    Chart 5: Black-Scholes vs Monte Carlo comparison.
    Shows validation of Monte Carlo implementation.
    """
    print("📊 Creating Black-Scholes vs Monte Carlo Comparison...")
    
    option = Option(
        symbol="COMPARE",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.25
    )
    
    # Calculate prices at different stock prices
    stock_prices = np.linspace(80, 120, 20)
    bs_prices = []
    mc_prices = []
    mc_errors = []
    
    mc_engine = MonteCarloEngine(random_seed=42)
    
    for stock_price in stock_prices:
        option.current_stock_price = stock_price
        
        # Black-Scholes
        bs_price = BlackScholesEngine.price_option(option)
        bs_prices.append(bs_price)
        
        # Monte Carlo
        mc_result = mc_engine.price_european_option(option, num_simulations=20000)
        mc_prices.append(mc_result.price)
        mc_errors.append(mc_result.standard_error * 1.96)  # 95% CI
    
    # Create plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle('Black-Scholes vs Monte Carlo Validation', fontsize=16, fontweight='bold')
    
    # Price comparison
    ax1.plot(stock_prices, bs_prices, 'b-', linewidth=3, label='Black-Scholes (Analytical)', marker='o')
    ax1.errorbar(stock_prices, mc_prices, yerr=mc_errors, fmt='ro', linewidth=2, 
                 markersize=6, capsize=4, label='Monte Carlo (20k sims)')
    ax1.set_xlabel('Stock Price ($)')
    ax1.set_ylabel('Option Price ($)')
    ax1.set_title('Price Comparison', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Error analysis
    errors = [(mc - bs) / bs * 100 for mc, bs in zip(mc_prices, bs_prices)]
    ax2.bar(stock_prices, errors, width=1.5, alpha=0.7, color='purple', edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.axhline(y=1, color='green', linestyle='--', alpha=0.5, label='±1% Error')
    ax2.axhline(y=-1, color='green', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Stock Price ($)')
    ax2.set_ylabel('Relative Error (%)')
    ax2.set_title('Monte Carlo Error vs Black-Scholes', fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('images/bs_vs_mc_comparison.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: images/bs_vs_mc_comparison.png")
    plt.close()

def main():
    """Generate all visualizations"""
    print("=" * 70)
    print("🎨 CREATING PROFESSIONAL VISUALIZATIONS")
    print("=" * 70)
    
    # Create images directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    try:
        # Generate all charts
        create_greeks_evolution_chart()
        create_monte_carlo_convergence_chart()
        create_price_surface_chart()
        create_portfolio_dashboard()
        create_comparison_chart()
        
        print("\n" + "=" * 70)
        print("🎉 ALL VISUALIZATIONS CREATED SUCCESSFULLY!")
        print("=" * 70)
        print("\n📁 Saved images:")
        print("   1. images/greeks_evolution.png - Greeks vs time")
        print("   2. images/monte_carlo_convergence.png - MC accuracy analysis")
        print("   3. images/price_surface.png - 3D option price surface")
        print("   4. images/portfolio_dashboard.png - Risk management dashboard")
        print("   5. images/bs_vs_mc_comparison.png - Validation chart")
        
        print("\n💡 Next steps:")
        print("   1. Add these images to your README.md")
        print("   2. Use them in presentations/interviews")
        print("   3. Share on LinkedIn to showcase your work!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

