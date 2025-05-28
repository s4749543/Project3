# This module provides functions to build and visualize binomial trees for option pricing.
# It includes a function to generate the stock and option value trees, and a function to plot these trees using networkx and matplotlib.

import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

# Constructs the binomial tree for stock prices and option values (American put by default)
def get_stock_and_option_trees(spot, strike, expiry, rate, vol, steps):
    S, K, T, r, sigma, N = spot, strike, expiry, rate, vol, steps
    dt = T / N
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)

    stock_tree = np.zeros((N + 1, N + 1))
    option_tree = np.zeros((N + 1, N + 1))

    # Build the stock price tree and initialize option values at maturity
    for i in range(N + 1):
        for j in range(i + 1):
            stock_tree[i, j] = S * (u ** j) * (d ** (i - j))
            option_tree[i, j] = max(K - stock_tree[i, j], 0)

    # Backward induction for option values (American put)
    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            hold = discount * (p * option_tree[i + 1, j + 1] + (1 - p) * option_tree[i + 1, j])
            exercise = K - stock_tree[i, j]
            option_tree[i, j] = max(hold, exercise)

    return stock_tree, option_tree

# Plots a binomial tree using networkx and matplotlib for visualization
def plot_binomial_tree_networkx(tree, title="Binomial Tree", color="skyblue"):
    G = nx.DiGraph()
    pos = {}
    labels = {}

    N = tree.shape[0] - 1

    for i in range(N + 1):
        for j in range(i + 1):
            node = f"{i},{j}"
            value = f"{tree[i,j]:.2f}"
            G.add_node(node)
            pos[node] = (i, j - i/2)  # Pyramid layout
            labels[node] = value
            if i < N:
                G.add_edge(node, f"{i+1},{j}")
                G.add_edge(node, f"{i+1},{j+1}")

    plt.figure(figsize=(10, 6))
    nx.draw_networkx_nodes(G, pos, node_color=color, node_size=800)
    nx.draw_networkx_edges(G, pos, edge_color='gray')
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
