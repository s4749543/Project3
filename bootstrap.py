from math import log, exp

class Instrument:
    def __init__(self, face_value, maturity, price):
        self.face_value = face_value
        self.maturity = maturity
        self.price = price
        self.cash_flows = []

    def add_cash_flow(self, time, amount):
        self.cash_flows.append((time, amount))

    def get_cash_flows(self):
        return self.cash_flows

    def get_maturity(self):
        return self.maturity

    def get_price(self):
        return self.price

    def get_face_value(self):
        return self.face_value

    def get_maturities(self):
        return [cf[0] for cf in self.cash_flows]

    def get_amounts(self):
        return [cf[1] for cf in self.cash_flows]


class BankBill(Instrument):
    def set_cash_flows(self):
        self.add_cash_flow(0, -self.price)
        self.add_cash_flow(self.maturity, self.face_value)


class Bond(Instrument):
    def __init__(self, face_value, maturity, coupon, frequency, price):
        super().__init__(face_value, maturity, price)
        self.coupon = coupon
        self.frequency = frequency

    def set_cash_flows(self):
        self.add_cash_flow(0, -self.price)
        num_periods = int(round(self.maturity * self.frequency))
        for i in range(1, num_periods):
            t = i / self.frequency
            cf = self.face_value * self.coupon / self.frequency
            self.add_cash_flow(t, cf)
        # Final payment
        self.add_cash_flow(self.maturity, self.face_value + (self.face_value * self.coupon / self.frequency))


class Portfolio:
    def __init__(self):
        self.bills = []
        self.bonds = []

    def add_bank_bill(self, bill):
        self.bills.append(bill)

    def add_bond(self, bond):
        self.bonds.append(bond)

    def get_bank_bills(self):
        return self.bills

    def get_bonds(self):
        return self.bonds


class YieldCurve:
    def __init__(self):
        self.maturities = []
        self.discount_factors = []

    def add_discount_factor(self, t, df):
        self.maturities.append(t)
        self.discount_factors.append(df)

    def get_discount_factor(self, t):
        if t in self.maturities:
            return self.discount_factors[self.maturities.index(t)]
        elif t < self.maturities[0] or t > self.maturities[-1]:
            raise ValueError("Requested maturity is out of curve range")
        else:
            # Linear interpolation in log DF space
            for i in range(1, len(self.maturities)):
                if self.maturities[i-1] < t < self.maturities[i]:
                    t0, t1 = self.maturities[i-1], self.maturities[i]
                    df0, df1 = self.discount_factors[i-1], self.discount_factors[i]
                    rate = (log(df0) - log(df1)) / (t1 - t0)
                    return exp(-rate * t)

    def get_zero_rate(self, t):
        df = self.get_discount_factor(t)
        return -log(df) / t

    def bootstrap(self, portfolio):
        self.add_discount_factor(0.0, 1.0)

        for bill in portfolio.get_bank_bills():
            t = bill.get_maturity()
            df = bill.get_price() / bill.get_face_value()
            self.add_discount_factor(t, df)

        for bond in portfolio.get_bonds():
            dates = bond.get_maturities()
            amounts = bond.get_amounts()
            pv = 0.0

            for i in range(1, len(dates) - 1):
                try:
                    df = self.get_discount_factor(dates[i])
                    pv += amounts[i] * df
                except ValueError:
                    continue

            final_t = dates[-1]
            final_cf = amounts[-1]
            df_final = (bond.get_price() - pv) / final_cf
            self.add_discount_factor(final_t, df_final)