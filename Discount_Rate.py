
# This module builds a discount curve from bank bills and bonds, and provides functions to retrieve discount factors and zero rates
from instrument_classes import Bank_bill, Bond, Portfolio
from curve_classes_and_functions import YieldCurve

# Builds bootstrapped discount curve from bank bills and bonds. 

def build_discount_curve():
    # Step 1: Create instruments
    bill1 = Bank_bill(face_value=100, maturity=0.25, price=98.5)
    bill2 = Bank_bill(face_value=100, maturity=0.5, price=97.3)
    bill1.set_cash_flows()
    bill2.set_cash_flows()

    bond1 = Bond(face_value=100, maturity=1.0, coupon=0.04, frequency=4, price=99.2)
    bond2 = Bond(face_value=100, maturity=2.0, coupon=0.045, frequency=4, price=98.7)
    bond3 = Bond(face_value=100, maturity=3.0, coupon=0.05, frequency=4, price=97.0)
    bond1.set_cash_flows()
    bond2.set_cash_flows()
    bond3.set_cash_flows()

    # Step 2: Add to portfolio
    portfolio = Portfolio()
    portfolio.add_bank_bill(bill1)
    portfolio.add_bank_bill(bill2)
    portfolio.add_bond(bond1)
    portfolio.add_bond(bond2)
    portfolio.add_bond(bond3)
    portfolio.set_cash_flows()

    # Step 3: Bootstrap yield curve
    yc = YieldCurve()
    yc.set_constituent_portfolio(portfolio)
    yc.bootstrap()

    return yc

# Retrieves the discount factor for a given maturity from the bootstrapped yield curve
def get_discount_factor(yield_curve, maturity):
    return yield_curve.get_discount_factor(maturity)

# Returns the interpolated zero rate for a given maturity from the yield curve
def get_zero_rate(yield_curve, maturity):
    return yield_curve.get_zero_rate(maturity)
