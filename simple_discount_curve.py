
import math

# Basic exponential interpolation
def exp_interp(x, x0, x1, y0, y1):
    if x1 == x0:
        return y0
    log_y0 = math.log(y0)
    log_y1 = math.log(y1)
    slope = (log_y1 - log_y0) / (x1 - x0)
    return math.exp(log_y0 + slope * (x - x0))

# Discount Curve Builder and Query Utility
class DiscountCurve:
    def __init__(self):
        self.maturities = []
        self.discount_factors = []

    def add(self, maturity, df):
        self.maturities.append(maturity)
        self.discount_factors.append(df)

    def get_discount_factor(self, t):
        if t in self.maturities:
            return self.discount_factors[self.maturities.index(t)]
        elif t < self.maturities[0] or t > self.maturities[-1]:
            raise ValueError("Requested maturity is out of curve range")
        else:
            for i in range(1, len(self.maturities)):
                if t < self.maturities[i]:
                    return exp_interp(t, self.maturities[i-1], self.maturities[i],
                                         self.discount_factors[i-1], self.discount_factors[i])

    def get_zero_rate(self, t):
        df = self.get_discount_factor(t)
        return -math.log(df) / t

def build_discount_curve():
    dc = DiscountCurve()

    # Add Bank Bills (discounted instruments)
    bill1_maturity = 0.16986301369863013 # Trade 4: Basket Call
    bill1_price = 98.5 # Simulated Price (3.5% implied rate)
    bill1_face = 100
    df1 = bill1_price / bill1_face
    dc.add(bill1_maturity, df1)

    bill2_maturity = 0.5
    bill2_price = 97.3
    df2 = bill2_price / bill1_face
    dc.add(bill2_maturity, df2)

    # Add Bonds (requires bootstrapping, simplified here for example)
    bond1_maturity = 1.0 # Trade 2: CBA American put
    bond1_coupon = 0.04
    bond1_price = 99.2
    df3 = (bond1_price - bond1_coupon * 100) / 100
    dc.add(bond1_maturity, df3)

    bond2_maturity = 2.33 # Trade 1 & 3: BHP and WES European/Barrier Calls
    bond2_coupon = 0.045
    bond2_price = 96.8
    df4 = (bond2_price - bond2_coupon * 100 * 2) / 100
    dc.add(bond2_maturity, df4)

    bond3_maturity = 3.0
    bond3_coupon = 0.05
    bond3_price = 97.0
    df5 = (bond3_price - bond3_coupon * 100 * 3) / 100
    dc.add(bond3_maturity, df5)

    return dc

# rate for Black-Scholes model or Monte Carlo simulations
def get_discount_rate(maturity):
    dc = build_discount_curve()
    return dc.get_zero_rate(maturity)

# rate for 
def get_discount_factor(maturity):
    dc = build_discount_curve()
    return dc.get_discount_factor(maturity)




