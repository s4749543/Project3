# This module defines option classes for pricing various types of options.
# It includes a base Option class and implementations for European, American, Barrier, and Basket options.
# Each class provides a price() method for computing the option's fair value using appropriate models.

import numpy as np
from scipy.stats import norm

class Option:
    def __init__(self, ticker, spot, strike, expiry, rate, vol, option_type="call", dividend_yield=0.0):
        # Base class for options. Stores common attributes.
        self.ticker = ticker
        self.spot = spot
        self.strike = strike
        self.expiry = expiry
        self.rate = rate
        self.vol = vol
        self.option_type = option_type
        self.dividend_yield = dividend_yield

    def get_dividend_yield(self):
        return self.dividend_yield

    def set_dividend_yield(self, q):
        self.dividend_yield = q

class EuropeanOption(Option):
    def price(self):
        # Black-Scholes formula for European call/put option pricing
        S, K, T, r, sigma, q = self.spot, self.strike, self.expiry, self.rate, self.vol, self.dividend_yield
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if self.option_type == "call":
            return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)

class AmericanPutOption(Option):
    def __init__(self, *args, steps=100, **kwargs):
        # American put option using a binomial tree for early exercise
        super().__init__(*args, **kwargs)
        self.steps = steps

    def price(self):
        S, K, T, r, sigma, N, q = self.spot, self.strike, self.expiry, self.rate, self.vol, self.steps, self.dividend_yield
        dt = T / N
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp((r - q) * dt) - d) / (u - d)
        discount = np.exp(-r * dt)

        stock_tree = np.zeros((N + 1, N + 1))
        option_tree = np.zeros((N + 1, N + 1))

        # Build stock and option value trees
        for i in range(N + 1):
            for j in range(i + 1):
                stock_tree[i, j] = S * (u ** j) * (d ** (i - j))
                option_tree[i, j] = max(K - stock_tree[i, j], 0)

        # Backward induction for early exercise
        for i in range(N - 1, -1, -1):
            for j in range(i + 1):
                hold = discount * (p * option_tree[i + 1, j + 1] + (1 - p) * option_tree[i + 1, j])
                exercise = K - stock_tree[i, j]
                option_tree[i, j] = max(hold, exercise)

        return option_tree[0, 0]

class UpAndInCallOption(Option):
    def __init__(self, barrier, simulations=10000, steps=252, *args, **kwargs):
        # Barrier option (up-and-in call) priced via Monte Carlo simulation
        super().__init__(*args, **kwargs)
        self.barrier = barrier
        self.simulations = simulations
        self.steps = steps

    def price(self):
        dt = self.expiry / self.steps
        disc = np.exp(-self.rate * self.expiry)
        q = self.dividend_yield
        payoffs = []

        for _ in range(self.simulations):
            prices = [self.spot]
            barrier_hit = False

            for _ in range(self.steps):
                Z = np.random.normal()
                S_next = prices[-1] * np.exp((self.rate - q - 0.5 * self.vol ** 2) * dt + self.vol * np.sqrt(dt) * Z)
                prices.append(S_next)
                if S_next >= self.barrier:
                    barrier_hit = True

            if barrier_hit:
                payoff = max(prices[-1] - self.strike, 0)
                payoffs.append(disc * payoff)
            else:
                payoffs.append(0)

        return np.mean(payoffs)

class BasketCallOption(Option):
    def __init__(self, tickers, spot_prices, weights, strike, expiry, rate, vol, corr_matrix, dividend_yield=0.0, **kwargs):
        # Basket call option using an effective Black-Scholes approach
        super().__init__(ticker="BASKET", spot=spot_prices, strike=strike, expiry=expiry,
                         rate=rate, vol=vol, option_type="call", dividend_yield=dividend_yield)
        self.tickers = tickers
        self.weights = np.array(weights)
        self.corr = np.array(corr_matrix)

    def price(self):
        S = np.array(self.spot)
        w = np.array(self.weights)
        vols = np.array(self.vol)
        cov_matrix = np.outer(vols, vols) * self.corr
        q = self.dividend_yield

        S_eff = np.dot(w, S)
        sigma_eff = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))

        K = self.strike
        T = self.expiry
        r = self.rate

        d1 = (np.log(S_eff / K) + (r - q + 0.5 * sigma_eff ** 2) * T) / (sigma_eff * np.sqrt(T))
        d2 = d1 - sigma_eff * np.sqrt(T)

        price = S_eff * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return price

