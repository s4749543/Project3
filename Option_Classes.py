# Define base class for pricing options
from scipy.stats import norm
import numpy as np

class Option:
    def __init__(self, ticker, spot, strike, expiry, rate, vol, option_type="call"):
        self.ticker = ticker
        self.spot = spot
        self.strike = strike
        self.expiry = expiry  # in years
        self.rate = rate
        self.vol = vol
        self.option_type = option_type

# Define European Option (Black-Scholes)

class EuropeanOption(Option):
    def price(self):
        S, K, T, r, sigma = self.spot, self.strike, self.expiry, self.rate, self.vol
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if self.option_type == "call":
            return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        else:
            return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1) #returns put option

# Define American Option (Bionomial Tree Pricing)

class AmericanPutOption(Option):
    def __init__(self, *args, steps=100, **kwargs):
        super().__init__(*args, **kwargs)
        self.steps = steps

    def price(self):
        S, K, T, r, sigma, N = self.spot, self.strike, self.expiry, self.rate, self.vol, self.steps
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

        return option_tree[0, 0]


# Up-and-In Barrier Call Option

class UpAndInCallOption(Option):
    def __init__(self, barrier, simulations=10000, steps=252, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier = barrier
        self.simulations = simulations
        self.steps = steps

    def price(self):
        dt = self.expiry / self.steps
        disc = np.exp(-self.rate * self.expiry)
        payoffs = []

        for _ in range(self.simulations):
            prices = [self.spot]
            barrier_hit = False

            for _ in range(self.steps):
                Z = np.random.normal()
                S_next = prices[-1] * np.exp((self.rate - 0.5 * self.vol ** 2) * dt + self.vol * np.sqrt(dt) * Z)
                prices.append(S_next)
                if S_next >= self.barrier:
                    barrier_hit = True

            if barrier_hit:
                payoff = max(prices[-1] - self.strike, 0)
                payoffs.append(disc * payoff)
            else:
                payoffs.append(0)

        return np.mean(payoffs)

# European Basket Call Option

# option_models/basket.py

class BasketCallOption(Option):
    def __init__(self, tickers, spot_prices, weights, strike, expiry, rate, volatilities, corr_matrix, simulations=10000):
        super().__init__(ticker="BASKET", spot=spot_prices, strike=strike, expiry=expiry,
                         rate=rate, vol=volatilities, option_type="call")
        self.tickers = tickers
        self.weights = np.array(weights)
        self.corr = np.array(corr_matrix)
        self.simulations = simulations

    def price(self):
        S = np.array(self.spot)
        vols = np.array(self.vol)
        cov = np.outer(vols, vols) * self.corr
        L = np.linalg.cholesky(cov)
        disc = np.exp(-self.rate * self.expiry)

        payoffs = []
        for _ in range(self.simulations):
            Z = np.random.normal(size=len(S))
            correlated = L @ Z
            S_T = S * np.exp((self.rate - 0.5 * vols**2) * self.expiry + correlated * np.sqrt(self.expiry))
            basket = np.dot(self.weights, S_T)
            payoffs.append(disc * max(basket - self.strike, 0))

        return np.mean(payoffs)
