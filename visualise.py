import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from Option_Classes import UpAndInCallOption, BasketCallOption

def plot_spot_vol_sensitivity(option_class, label, base_spot, base_vol, 
                              spot_range=(80, 120, 50), vol_range=(0.1, 0.6, 50), **kwargs):
    """
    Generic spot and vol sensitivity plot for analytical options (e.g., European).
    """
    spot_vals = np.linspace(*spot_range)
    prices_spot = [option_class(spot=s, vol=base_vol, **kwargs).price() for s in spot_vals]

    vol_vals = np.linspace(*vol_range)
    prices_vol = [option_class(spot=base_spot, vol=v, **kwargs).price() for v in vol_vals]

    _plot_sensitivity_curves(spot_vals, prices_spot, vol_vals, prices_vol, label)


def plot_spot_vol_sensitivity_barrier(label, base_spot, base_vol, strike, expiry, rate,
                                      option_type, ticker, barrier,
                                      spot_range=(80, 120, 30), vol_range=(0.1, 0.6, 30)):
    """
    Spot/vol sensitivity plot for Up-and-In Barrier Call using Monte Carlo.
    """
    spot_vals = np.linspace(*spot_range)
    prices_spot = []
    for s in spot_vals:
        opt = UpAndInCallOption(
            ticker=ticker, spot=s, strike=strike, expiry=expiry,
            rate=rate, vol=base_vol, option_type=option_type, barrier=barrier
        )
        prices_spot.append(opt.price())

    vol_vals = np.linspace(*vol_range)
    prices_vol = []
    for v in vol_vals:
        opt = UpAndInCallOption(
            ticker=ticker, spot=base_spot, strike=strike, expiry=expiry,
            rate=rate, vol=v, option_type=option_type, barrier=barrier
        )
        prices_vol.append(opt.price())

    _plot_sensitivity_curves(spot_vals, prices_spot, vol_vals, prices_vol, label)


def plot_spot_vol_sensitivity_basket(label, base_spots, base_vols, weights, corr_matrix,
                                     strike, expiry, rate, tickers,
                                     spot_range=(80, 120, 30), vol_range=(0.1, 0.6, 30)):
    """
    Spot/vol sensitivity plot for Basket Call Option using Monte Carlo.
    """
    spot_vals = np.linspace(*spot_range)
    prices_spot = []
    for s in spot_vals:
        spots = [s] * len(base_spots)
        opt = BasketCallOption(
            tickers=tickers, spot_prices=spots, weights=weights, strike=strike,
            expiry=expiry, rate=rate, volatilities=base_vols, corr_matrix=corr_matrix
        )
        prices_spot.append(opt.price())

    vol_vals = np.linspace(*vol_range)
    prices_vol = []
    for v in vol_vals:
        vols = [v] * len(base_vols)
        opt = BasketCallOption(
            tickers=tickers, spot_prices=base_spots, weights=weights, strike=strike,
            expiry=expiry, rate=rate, volatilities=vols, corr_matrix=corr_matrix
        )
        prices_vol.append(opt.price())

    _plot_sensitivity_curves(spot_vals, prices_spot, vol_vals, prices_vol, label)


# ──────────────────────────────────────────────────────────────────────────────
# Internal utility plotter (used by all three)
def _plot_sensitivity_curves(spot_vals, prices_spot, vol_vals, prices_vol, label):
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    axs[0].plot(spot_vals, prices_spot, color="blue")
    axs[0].set_title(f"{label} – Price vs Spot")
    axs[0].set_xlabel("Spot Price")
    axs[0].set_ylabel("Option Price")
    axs[0].grid(True)

    axs[1].plot(vol_vals, prices_vol, color="purple")
    axs[1].set_title(f"{label} – Price vs Implied Volatility")
    axs[1].set_xlabel("Volatility")
    axs[1].set_ylabel("Option Price")
    axs[1].grid(True)

    plt.tight_layout()
    plt.show()




import numpy as np
import matplotlib.pyplot as plt

def plot_spot_vol_sensitivity_basket_bs(label, base_spots, base_vols, weights, corr_matrix,
                                        strike, expiry, rate, ticker, tickers,
                                        spot_range=(80, 120, 50), vol_range=(0.1, 0.6, 50),
                                        component_index=0, option_class=None):
    """
    Visualizes sensitivity of a Basket Call (Black-Scholes) option to changes in one asset's spot and vol.
    """
    if option_class is None:
        raise ValueError("Provide a valid option_class using Black-Scholes")

    representative_vol = np.mean(base_vols)

    # Spot sensitivity
    spot_vals = np.linspace(*spot_range)
    prices_spot = []

    for s in spot_vals:
        spots = base_spots.copy()
        spots[component_index] = s
        opt = option_class(
            tickers=tickers,
            spot_prices=spots,
            weights=weights,
            strike=strike,
            expiry=expiry,
            rate=rate,
            vol=representative_vol,             
            volatilities=base_vols,
            corr_matrix=corr_matrix
        )
        prices_spot.append(opt.price())

    # Volatility sensitivity
    vol_vals = np.linspace(*vol_range)
    prices_vol = []

    for v in vol_vals:
        vols = base_vols.copy()
        vols[component_index] = v
        opt = option_class(
            tickers=tickers,
            spot_prices=base_spots,
            weights=weights,
            strike=strike,
            expiry=expiry,
            rate=rate,
            vol=np.mean(vols),                    
            volatilities=vols,
            corr_matrix=corr_matrix
        )
        prices_vol.append(opt.price())

    # Plotting
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))

    axs[0].plot(spot_vals, prices_spot, color="blue")
    axs[0].set_title(f"{label} - Price vs Spot of {tickers[component_index]}")
    axs[0].set_xlabel("Spot Price")
    axs[0].set_ylabel("Option Price")
    axs[0].grid(True)

    axs[1].plot(vol_vals, prices_vol, color="purple")
    axs[1].set_title(f"{label} - Price vs Implied Vol of {tickers[component_index]}")
    axs[1].set_xlabel("Implied Volatility")
    axs[1].set_ylabel("Option Price")
    axs[1].grid(True)

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
