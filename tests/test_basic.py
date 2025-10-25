"""
Basic Unit Tests for Options Pricing Engine
-------------------------------------------
Tests core functionality of the pricing models.

Run with:
    python -m pytest tests/
    or
    python tests/test_basic.py

Author: Lawrence (2025)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from src.models.option import Option, OptionType
from src.models.black_scholes import BlackScholesEngine
from src.models.monte_carlo import MonteCarloEngine


def test_black_scholes_call():
    """Test Black-Scholes call option pricing"""
    print("\n🧪 Testing Black-Scholes Call Option...")
    
    option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    price = BlackScholesEngine.price_option(option)
    
    # Expected price should be between $2 and $4 for these parameters
    assert 2.0 < price < 4.0, f"Price {price} outside expected range"
    print(f"   ✅ BS Call Price: ${price:.4f} (within expected range)")
    return price


def test_black_scholes_put():
    """Test Black-Scholes put option pricing"""
    print("\n🧪 Testing Black-Scholes Put Option...")
    
    option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.PUT,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    price = BlackScholesEngine.price_option(option)
    
    # Expected price should be between $1.5 and $3.5 for these parameters
    assert 1.5 < price < 3.5, f"Price {price} outside expected range"
    print(f"   ✅ BS Put Price: ${price:.4f} (within expected range)")
    return price


def test_put_call_parity():
    """Test put-call parity relationship: C - P = S - K*e^(-rT)"""
    print("\n🧪 Testing Put-Call Parity...")
    
    S = 100.0
    K = 100.0
    r = 0.05
    T = 30/365.0
    
    call_option = Option(
        symbol="TEST",
        strike_price=K,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=S,
        risk_free_rate=r,
        volatility=0.20
    )
    
    put_option = Option(
        symbol="TEST",
        strike_price=K,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.PUT,
        current_stock_price=S,
        risk_free_rate=r,
        volatility=0.20
    )
    
    call_price = BlackScholesEngine.price_option(call_option)
    put_price = BlackScholesEngine.price_option(put_option)
    
    # Put-call parity: C - P = S - K*e^(-rT)
    import math
    left_side = call_price - put_price
    right_side = S - K * math.exp(-r * T)
    
    difference = abs(left_side - right_side)
    
    assert difference < 0.01, f"Put-call parity violated! Difference: {difference}"
    print(f"   C - P = ${left_side:.4f}")
    print(f"   S - K*e^(-rT) = ${right_side:.4f}")
    print(f"   ✅ Difference: ${difference:.6f} (< 0.01 threshold)")


def test_monte_carlo_convergence():
    """Test that Monte Carlo converges to Black-Scholes"""
    print("\n🧪 Testing Monte Carlo Convergence...")
    
    option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    bs_price = BlackScholesEngine.price_option(option)
    
    mc_engine = MonteCarloEngine(random_seed=42)
    mc_result = mc_engine.price_european_option(option, num_simulations=50000)
    
    error_pct = abs(bs_price - mc_result.price) / bs_price * 100
    
    # Monte Carlo should be within 2% of Black-Scholes with 50k simulations
    assert error_pct < 2.0, f"MC error {error_pct:.2f}% exceeds 2% threshold"
    print(f"   BS Price: ${bs_price:.4f}")
    print(f"   MC Price: ${mc_result.price:.4f}")
    print(f"   ✅ Error: {error_pct:.2f}% (< 2% threshold)")


def test_intrinsic_value():
    """Test that intrinsic value is calculated correctly"""
    print("\n🧪 Testing Intrinsic Value...")
    
    # ITM Call
    call_option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=110.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    assert call_option.intrinsic_value == 10.0, "Call intrinsic value incorrect"
    print(f"   ✅ ITM Call intrinsic value: ${call_option.intrinsic_value:.2f}")
    
    # ITM Put
    put_option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.PUT,
        current_stock_price=90.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    assert put_option.intrinsic_value == 10.0, "Put intrinsic value incorrect"
    print(f"   ✅ ITM Put intrinsic value: ${put_option.intrinsic_value:.2f}")
    
    # OTM options should have zero intrinsic value
    otm_call = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=90.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    assert otm_call.intrinsic_value == 0.0, "OTM call should have zero intrinsic value"
    print(f"   ✅ OTM Call intrinsic value: ${otm_call.intrinsic_value:.2f}")


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("\n🧪 Testing Edge Cases...")
    
    # Very high volatility
    option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=30),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=1.0  # 100% volatility!
    )
    
    price = BlackScholesEngine.price_option(option)
    assert price > 0, "Price should be positive even with high volatility"
    print(f"   ✅ High volatility (100%) handled: ${price:.2f}")
    
    # Very short expiration
    short_option = Option(
        symbol="TEST",
        strike_price=100.0,
        expiration_date=datetime.now() + timedelta(days=1),
        option_type=OptionType.CALL,
        current_stock_price=100.0,
        risk_free_rate=0.05,
        volatility=0.20
    )
    
    short_price = BlackScholesEngine.price_option(short_option)
    assert short_price > 0, "Price should be positive for short expiration"
    print(f"   ✅ Short expiration (1 day) handled: ${short_price:.2f}")


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("🧪 RUNNING UNIT TESTS")
    print("="*70)
    
    try:
        test_black_scholes_call()
        test_black_scholes_put()
        test_put_call_parity()
        test_monte_carlo_convergence()
        test_intrinsic_value()
        test_edge_cases()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🎯 Test Summary:")
        print("   • Black-Scholes pricing: ✅")
        print("   • Put-call parity: ✅")
        print("   • Monte Carlo convergence: ✅")
        print("   • Intrinsic value calculation: ✅")
        print("   • Edge cases: ✅")
        print("="*70 + "\n")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)