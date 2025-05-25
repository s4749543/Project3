# hedging.py

import numpy as np
from scipy.stats import norm

class HedgingCalculator:
    def __init__(self, bump_size=0.01, time_bump=1/365):
        self.bump = bump_size
        self.time_bump = time_bump

    def calculate_delta_analytical(self, option):
        S, K, T, r, sigma = option.spot, option.strike, option.expiry, option.rate, option.vol
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        if option.option_type == "call":
            return norm.cdf(d1)
        if option.option_type == "put":
            return norm.cdf(d1) - 1

    def calculate_delta_fd(self, option):
        S = option.spot
        h = self.bump
        option.spot = S + h
        up = option.price()
        option.spot = S - h
        down = option.price()
        option.spot = S
        return (up - down) / (2 * h)

    def calculate_gamma_fd(self, option):
        S = option.spot
        h = self.bump
        option.spot = S + h
        up = option.price()
        option.spot = S
        mid = option.price()
        option.spot = S - h
        down = option.price()
        option.spot = S
        return (up - 2 * mid + down) / (h ** 2)

    def calculate_vega_fd(self, option):
        sigma = option.vol
        h = self.bump
        option.vol = sigma + h
        up = option.price()
        option.vol = sigma - h
        down = option.price()
        option.vol = sigma
        return (up - down) / (2 * h)

    def calculate_theta_fd(self, option):
        T = option.expiry
        h = self.time_bump
        option.expiry = T - h
        price_early = option.price()
        option.expiry = T
        price_now = option.price()
        return (price_early - price_now) / h

    def calculate_rho_fd(self, option):
        r = option.rate
        h = self.bump
        option.rate = r + h
        up = option.price()
        option.rate = r - h
        down = option.price()
        option.rate = r
        return (up - down) / (2 * h)

    def get_all_greeks(self, option, method="fd"):
        """
        Returns all Greeks in a dictionary.
        method = "fd" for finite difference
        method = "analytical" (only delta supported)
        """
        if method == "analytical":
            delta = self.calculate_delta_analytical(option)
        elif method == "fd":
            delta = self.calculate_delta_fd(option)

        return {
            "delta": delta,
            "gamma": self.calculate_gamma_fd(option),
            "vega": self.calculate_vega_fd(option),
            "theta": self.calculate_theta_fd(option),
            "rho": self.calculate_rho_fd(option)
        }
