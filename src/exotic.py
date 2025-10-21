
import numpy as np
import math
from scipy.stats import norm

def barrier_up_and_out_mc(S0, K, H, r, sigma, T, option_type="call", m=252, n_paths=100_000, seed=None):
    """
    Monte Carlo for an up-and-out barrier option.
    H: barrier level > S0. If path crosses H at any observation point, option knocked out (payoff 0).
    """
    rng = np.random.default_rng(seed)
    dt = T / m
    nudt = (r - 0.5 * sigma * sigma) * dt
    sigsqrtdt = sigma * math.sqrt(dt)

    Z = rng.standard_normal(size=(n_paths, m))
    S = np.empty_like(Z)
    S[:, 0] = S0 * np.exp(nudt + sigsqrtdt * Z[:, 0])
    for t in range(1, m):
        S[:, t] = S[:, t - 1] * np.exp(nudt + sigsqrtdt * Z[:, t])

    # detect barrier crossing at discrete times
    crossed = (S >= H).any(axis=1)
    avg = S.mean(axis=1)
    if option_type == "call":
        payoffs = np.where(~crossed, np.maximum(avg - K, 0.0), 0.0)
    else:
        payoffs = np.where(~crossed, np.maximum(K - avg, 0.0), 0.0)

    price = math.exp(-r * T) * payoffs.mean()
    stderr = math.exp(-r * T) * payoffs.std(ddof=0) / math.sqrt(n_paths)
    return price, stderr

def american_binomial_crr(S0, K, r, sigma, T, option_type="call", steps=1000):
    """
    CRR binomial tree for American options (supports early exercise).
    steps: number of steps in the binomial tree.
    """
    dt = T / steps
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    p = (math.exp(r * dt) - d) / (u - d)
    # stock price tree (only current column kept)
    prices = np.array([S0 * (u ** j) * (d ** (0)) for j in range(steps + 1)], dtype=float)
    # option values at maturity
    if option_type == "call":
        values = np.maximum(prices - K, 0.0)
    else:
        values = np.maximum(K - prices, 0.0)

    # backward induction with early exercise
    disc = math.exp(-r * dt)
    for i in range(steps - 1, -1, -1):
        prices = prices[: i + 1] / u  # move to prior level
        continuation = disc * (p * values[1 : i + 2] + (1 - p) * values[: i + 1])
        intrinsic = (np.maximum(prices - K, 0.0) if option_type == "call" else np.maximum(K - prices, 0.0))
        values = np.maximum(continuation, intrinsic)  # American option allows early exercise
    return float(values[0])

if __name__ == "__main__":
    print("Barrier MC example:", barrier_up_and_out_mc(100, 100, 120, 0.01, 0.2, 30/365, n_paths=20000))
    print("American CRR:", american_binomial_crr(100, 100, 0.01, 0.2, 30/365, option_type="put", steps=500))
