
import copy

class HedgingCalculator:
    def __init__(self, bump=0.01, dt=1/252, dr=0.0001):
        self.bump = bump
        self.dt = dt
        self.dr = dr

    def calculate_delta_fd(self, option):
        S = option.spot
        h = self.bump

        if isinstance(S, list):
            deltas = []
            for i in range(len(S)):
                bumped_up = S.copy()
                bumped_up[i] += h
                option.spot = bumped_up
                up = option.price()

                bumped_down = S.copy()
                bumped_down[i] -= h
                option.spot = bumped_down
                down = option.price()

                deltas.append((up - down) / (2 * h))

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
        h = self.bump

        if isinstance(S, list):
            gammas = []
            for i in range(len(S)):
                bumped_up = S.copy()
                bumped_up[i] += h
                option.spot = bumped_up
                up = option.price()

                option.spot = S
                base = option.price()

                bumped_down = S.copy()
                bumped_down[i] -= h
                option.spot = bumped_down
                down = option.price()

                gammas.append((up - 2 * base + down) / (h ** 2))

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
        h = self.bump

        if isinstance(sigma, list):
            vegas = []
            for i in range(len(sigma)):
                bumped_up = sigma.copy()
                bumped_up[i] += h
                option.vol = bumped_up
                up = option.price()

                bumped_down = sigma.copy()
                bumped_down[i] -= h
                option.vol = bumped_down
                down = option.price()

                vegas.append((up - down) / (2 * h))

            option.vol = sigma
            return vegas
        else:
            option.vol = sigma + h
            up = option.price()
            option.vol = sigma - h
            down = option.price()
            option.vol = sigma
            return (up - down) / (2 * h)

    def calculate_theta_fd(self, option):
        T = option.expiry
        dt = self.dt
        option.expiry = T - dt
        value = option.price()
        option.expiry = T
        return (option.price() - value) / dt

    def calculate_rho_fd(self, option):
        r = option.rate
        dr = self.dr
        option.rate = r + dr
        up = option.price()
        option.rate = r - dr
        down = option.price()
        option.rate = r
        return (up - down) / (2 * dr)

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
