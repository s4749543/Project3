
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

def visualize_option_price_vs_spot(option_class, label, spot_range, **kwargs):
    spots = np.linspace(*spot_range)
    prices = []

    for s in spots:
        option = option_class(spot=s, **kwargs)
        prices.append(option.price())

    plt.figure(figsize=(8, 5))
    plt.plot(spots, prices, label=label)
    plt.title(f"{label}\nPricing Method: {option_class.__name__}")
    plt.xlabel("Spot Price")
    plt.ylabel("Option Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def visualize_basket_vs_strike(basket_class, strike_range, **kwargs):
    strikes = np.linspace(*strike_range)
    prices = []

    for k in strikes:
        option = basket_class(strike=k, **kwargs)
        prices.append(option.price())

    plt.figure(figsize=(8, 5))
    plt.plot(strikes, prices, label="Basket Option")
    plt.title("Basket Call: Price vs Strike")
    plt.xlabel("Strike Price")
    plt.ylabel("Option Price")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

def visualize_up_and_in_barrier_call(S0, K, T, r, sigma, B, M=100, steps=252, random_seed=42):
    np.random.seed(random_seed)
    dt = T / steps
    time_grid = np.linspace(0, T, steps + 1)

    contributing_paths = []
    inactivated_paths = []
    knocked_in_no_payoff = []

    for _ in range(M):
        prices = [S0]
        barrier_hit = False
        for _ in range(steps):
            Z = np.random.normal()
            S_next = prices[-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
            prices.append(S_next)
            if S_next >= B:
                barrier_hit = True

        if barrier_hit:
            if prices[-1] > K:
                contributing_paths.append(prices)
            else:
                knocked_in_no_payoff.append(prices)
        else:
            inactivated_paths.append(prices)

    # Plotting
    plt.figure(figsize=(10, 6))

    red_line = None
    green_line = None
    gray_line = None

    for path in knocked_in_no_payoff:
        red_line, = plt.plot(time_grid, path, color="red", alpha=0.2)
    for path in contributing_paths:
        green_line, = plt.plot(time_grid, path, color="green", alpha=0.3)
    for path in inactivated_paths:
        gray_line, = plt.plot(time_grid, path, color="gray", alpha=0.1)

    barrier_line = plt.axhline(B, color="blue", linestyle="--")

    plt.title(f"Up-and-In Barrier Call Option Paths\n($S_0$={S0}, K={K}, B={B})")
    plt.xlabel("Time (Years)")
    plt.ylabel("Stock Price")
    plt.grid(True)

    # Proper legend handles
    handles = [
        Line2D([0], [0], color="red", lw=2, label="Knocked In (No Payoff)"),
        Line2D([0], [0], color="green", lw=2, label="Contributing Paths"),
        Line2D([0], [0], color="gray", lw=2, label="Never Knocked In"),
        Line2D([0], [0], color="blue", lw=2, linestyle="--", label=f"Barrier Level (B={B})")
    ]
    plt.legend(handles=handles)
    plt.tight_layout()
    plt.show()
