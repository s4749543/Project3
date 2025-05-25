
from instrument_classes1 import Bank_bill, Bond, Portfolio
from curve_classes_and_functions import YieldCurve

def build_discount_curve():
    # Step 1: Create and configure instruments
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

    # Step 2: Add instruments to a portfolio
    portfolio = Portfolio()
    portfolio.add_bank_bill(bill1)
    portfolio.add_bank_bill(bill2)
    portfolio.add_bond(bond1)
    portfolio.add_bond(bond2)
    portfolio.add_bond(bond3)
    portfolio.set_cash_flows()

    # Step 3: Build the yield curve
    yc = YieldCurve()
    yc.set_constituent_portfolio(portfolio)
    yc.bootstrap()

    return yc

def get_discount_rate(maturity_years):
    """
    Returns the zero-coupon rate (continuously compounded) for a given maturity.
    """
    yc = build_discount_curve()
    return yc.get_zero_rate(maturity_years)

def get_discount_factor(maturity_years):
    """
    Returns the discount factor for a given maturity.
    """
    yc = build_discount_curve()
    return yc.get_discount_factor(maturity_years)
