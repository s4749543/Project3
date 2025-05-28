# This module provides a HedgingCalculator class to compute option Greeks (sensitivities)
# using finite difference (FD) methods. Greeks include delta, gamma, vega, theta, and rho.
# The class supports both single-asset and multi-asset options.

import numpy as np
import copy

class HedgingCalculator:
    def __init__(self, spot_bump_pct=0.01, vol_bump_pct=0.01, dt_days=5, rate_bump_pct=0.0001):
        # spot_bump_pct: Percentage bump for spot price (for delta/gamma)
        # vol_bump_pct: Percentage bump for volatility (for vega)
        # dt_days: Number of days for theta calculation (time decay)
        # rate_bump_pct: Bump size for interest rate (for rho)
        self.spot_bump_pct = spot_bump_pct      # 1% bump for delta/gamma
        self.vol_bump_pct = vol_bump_pct        # 1% bump for vega (relative to vol)
        self.dt = dt_days / 252                 # 5 trading days (smoothed theta)
        self.rate_bump_pct = rate_bump_pct      # 1 basis point bump (for rho)

    def calculate_delta_fd(self, option):
        # Computes delta using central finite difference method
        S = option.spot
        h = [1.0] * len(S) if isinstance(S, list) else 1.0  # $1 bump

        if isinstance(S, list):
            deltas = []
            for i in range(len(S)):
                bumped_up = copy.deepcopy(S)
                bumped_up[i] += h[i]
                option.spot = bumped_up
                up = option.price()

                bumped_down = copy.deepcopy(S)
                bumped_down[i] -= h[i]
                option.spot = bumped_down
                down = option.price()

                deltas.append((up - down) / (2 * h[i]))

            option.spot = S
            return deltas
        else:
            option.spot = S + h
            up = option.price()
            option.spot = S - h
            down = option.price()
            option.spot = S
            return (up - down) / (2 * h)

    def calculate_gamma_fd(self, option):
        # Computes gamma using central finite difference method
        S = option.spot
        h = [1.0] * len(S) if isinstance(S, list) else 1.0  # $1 bump

        if isinstance(S, list):
            gammas = []
            for i in range(len(S)):
                bumped_up = copy.deepcopy(S)
                bumped_up[i] += h[i]
                option.spot = bumped_up
                up = option.price()

                option.spot = S
                base = option.price()

                bumped_down = copy.deepcopy(S)
                bumped_down[i] -= h[i]
                option.spot = bumped_down
                down = option.price()

                gammas.append((up - 2 * base + down) / (h[i] ** 2))

            option.spot = S
            return gammas
        else:
            option.spot = S + h
            up = option.price()
            option.spot = S
            base = option.price()
            option.spot = S - h
            down = option.price()
            option.spot = S
            return (up - 2 * base + down) / (h ** 2)

    def calculate_vega_fd(self, option):
        # Computes vega using central finite difference method
        sigma = option.vol
        h = [v * self.vol_bump_pct for v in sigma] if isinstance(sigma, list) else sigma * self.vol_bump_pct

        if isinstance(sigma, list):
            vegas = []
            for i in range(len(sigma)):
                bumped_up = copy.deepcopy(sigma)
                bumped_up[i] += h[i]
                option.vol = bumped_up
                up = option.price()

                bumped_down = copy.deepcopy(sigma)
                bumped_down[i] -= h[i]
                option.vol = bumped_down
                down = option.price()

                vegas.append((up - down) / (2 * h[i]))

            option.vol = sigma
            return [v / 100 for v in vegas]  # Standardize vega to 1% change
        else:
            option.vol = sigma + h
            up = option.price()
            option.vol = sigma - h
            down = option.price()
            option.vol = sigma
            vega = (up - down) / (2 * h)
            return vega / 100  # Standardize vega to 1% change

    def calculate_theta_fd(self, option):
        # Computes theta (time decay) using forward difference
        T = option.expiry
        dt = self.dt

        if T <= dt:
            return 0.0  # Too close to expiry

        base = option.price()
        option.expiry = T + dt
        price_forward = option.price()
        option.expiry = T  # Reset expiry

        theta = (base - price_forward) / dt
        return theta

    def calculate_rho_fd(self, option):
        # Computes rho (interest rate sensitivity) using central finite difference
        r = option.rate
        dr = self.rate_bump_pct

        option.rate = r + dr
        up = option.price()
        option.rate = r - dr
        down = option.price()
        option.rate = r

        rho = (up - down) / (2 * dr)
        return rho / 100  # Standardize rho to 1% change

    def get_all_greeks(self, option, method="fd"):
        # Returns all Greeks as a dictionary using the finite difference method
        if method == "fd":
            return {
                "delta": self.calculate_delta_fd(option),
                "gamma": self.calculate_gamma_fd(option),
                "vega": self.calculate_vega_fd(option),
                "theta": self.calculate_theta_fd(option),
                "rho": self.calculate_rho_fd(option)
            }
        else:
            raise NotImplementedError("Only finite difference method ('fd') is supported.")
