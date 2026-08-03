import numpy as np
import yfinance as yf
import pandas as pd


def price_data(ticker:str, val_date: str, lookback):
    val_date_obj = pd.to_datetime(val_date)
    start_date = val_date_obj - pd.Timedelta(days = lookback * 365)
    end_date = val_date_obj + pd.Timedelta(days=1)
    data = yf.download(tickers = ticker, start = start_date, end = end_date)
    return data

def clean_filter(data:pd.DataFrame):
    data = data.dropna()
    return data ["Close"]

def historical_vol(data:pd.DataFrame):
    data = data
    log_ret = np.log(data / data.shift(1))
    log_returns = log_ret.dropna()
    daily_vol = log_returns.std()
    annualized_vol = daily_vol * np.sqrt(252)
    return annualized_vol.item()


def get_volatility(ticker:str, val_date:str, lookback):
    data = price_data(ticker, val_date, lookback)
    cleaned_data = clean_filter(data)
    hist_vol = historical_vol(cleaned_data)
    return hist_vol