import yfinance as yf
import pandas as pd
import datetime as dt
import fredapi
import numpy as np
from pandas.core.interchange.dataframe_protocol import DataFrame
from scipy.stats import norm
from riskfree_and_spot import *


N = norm.cdf

def bs_call (S, K, T, r, vol):
    d1 = (np.log(S/K) + (r + 0.5 * vol ** 2) * T) / (vol*np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    return S * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)

def bs_put(S, K, T, r, vol):
    d1 = (np.log(S/K) + (r + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def bs_vega(S, K, T, r, vol):
    d1 = (np.log(S/K) + (r + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    return S * norm.pdf(d1) * np.sqrt(T)

def find_vol_bs(target_value, S, K, T, r, vol, opt_type:str):
    MAX_ITERATIONS = 200
    PRECISION = 1.0e-5
    for i in range (0, MAX_ITERATIONS):
        if opt_type.lower() == 'call':
            price = bs_call(S, K, T, r, vol)
        elif opt_type.lower() == 'put':
            price = bs_put(S, K, T, r, vol)
        else:
            raise ValueError("option type must be 'call' or 'put'")

        vega = bs_vega(S, K, T, r, vol)
        diff = target_value - price

        if (abs(diff) < PRECISION):
            return float(vol)

        if vega == 0 or np.isnan(vega) or np.isinf(vega):
            return np.nan

        vol = vol + diff/vega

        if vol <= 0 or np.isnan(vol) or np.isinf(vol):
            return np.nan

    return np.nan