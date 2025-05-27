import numpy as np
import copy

class HedgingCalculator:
    def __init__(self, spot_bump_pct=0.01, vol_bump_pct=0.01, dt_days=5, rate_bump_pct=0.0001):
        self.spot_bump_pct = spot_bump_pct      # 1% bump for delta/gamma
        self.vol_bump_pct = vol_bump_pct        # 1% bump for vega (relative to vol)
        self.dt = dt_days / 252                 # 5 trading days (smoothed theta)
        self.rate_bump_pct = rate_bump_pct      # 1 basis point bump (for rho)

    def calculate_delta_fd(self, option):
        S = option.spot
        h = self.spot_bump_pct * np.array(S) if isinstance(S, list) else self.spot_bump_pct * S

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
        S = option.spot
        h = self.spot_bump_pct * np.array(S) if isinstance(S, list) else self.spot_bump_pct * S

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
            return [v / 100 for v in vegas]
        else:
            option.vol = sigma + h
            up = option.price()
            option.vol = sigma - h
            down = option.price()
            option.vol = sigma
            vega = (up - down) / (2 * h)
            return vega / 100

    def calculate_theta_fd(self, option):
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
        r = option.rate
        dr = self.rate_bump_pct

        option.rate = r + dr
        up = option.price()
        option.rate = r - dr
        down = option.price()
        option.rate = r

        rho = (up - down) / (2 * dr)
        return rho / 100

    def get_all_greeks(self, option, method="fd"):
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
