
import numpy as np
import matplotlib.pyplot as plt

def get_stock_and_option_trees(spot, strike, expiry, rate, vol, steps):
    S, K, T, r, sigma, N = spot, strike, expiry, rate, vol, steps
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)

    stock_tree = np.zeros((N + 1, N + 1))
    option_tree = np.zeros((N + 1, N + 1))

    for i in range(N + 1):
        for j in range(i + 1):
            stock_tree[i, j] = S * (u ** j) * (d ** (i - j))
            option_tree[i, j] = max(K - stock_tree[i, j], 0)

    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            hold = discount * (p * option_tree[i + 1, j + 1] + (1 - p) * option_tree[i + 1, j])
            exercise = K - stock_tree[i, j]
            option_tree[i, j] = max(hold, exercise)

    return stock_tree, option_tree

def plot_binomial_tree(tree, title="Tree"):
    N = tree.shape[0] - 1
    plt.figure(figsize=(12, 6))
    for i in range(N + 1):
        for j in range(i + 1):
            x = i
            y = j
            value = tree[i, j]
            plt.plot(x, y, 'o', color='black')
            plt.text(x, y, f"{value:.2f}", ha='center', va='center',
                     fontsize=8, bbox=dict(boxstyle="round,pad=0.3", fc="w", ec="0.5"))
    plt.title(title)
    plt.xlabel("Time Step")
    plt.ylabel("Node")
    plt.grid(True)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
