from Option_Classes import EuropeanOption
from Option_Classes import AmericanPutOption
from Option_Classes import UpAndInCallOption
from Option_Classes import BasketCallOption
from Hedging_Parameters import HedgingCalculator
from market_data import get_close_price
from market_data import get_volatility
from market_data import get_correlation_matrix
from market_data import get_all_market_data
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import importlib
from simple_discount_curve import get_discount_rate
from simple_discount_curve import get_discount_factor

ticker = "BHP.AX"
date = "2025-05-16"

spot_bhp = get_close_price(ticker, date) #good
vol_bhp = get_volatility(ticker, end_date=date, window=60) #good
strike_bhp = 0.98 * spot_bhp

def time_to_expiry(start, end):
    return (end - start).days / 365.0

expiry_bhp = time_to_expiry(datetime(2025, 5, 16), datetime(2027, 9, 15))

rate_bhp = get_discount_rate(expiry_bhp)  # good
print(rate_bhp)

bhp_option = EuropeanOption(ticker=ticker,spot=spot_bhp, strike=strike_bhp, expiry=expiry_bhp, rate=rate_bhp, vol=vol_bhp, option_type="call")

print(f"Option Price: {bhp_option.price()}")


