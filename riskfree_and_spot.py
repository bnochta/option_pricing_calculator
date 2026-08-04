import yfinance as yf
import pandas as pd
import datetime as dt
import fredapi
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
fred_api_key = os.environ.get("fred_api_key")
if not fred_api_key:
    raise RuntimeError("Missing FRED_API_KEY environment variable. Create a .env file containing FRED_API_KEY=<your_api_key>.")

fred = fredapi.Fred(api_key=fred_api_key)

FRED_SERIES = {
    "DGS1MO": 1/12,
    "DGS3MO": 3/12,
    "DGS6MO": 6/12,
    "DGS1": 1,
    "DGS2": 2,
    "DGS5": 5,
    "DGS10": 10,
    "DGS30": 30,
}

#SPOT_PRICE_DATA

def get_spot_price_data(ticker:str, valuation_date):
    valuation_date_obj = pd.to_datetime(valuation_date)
    today = dt.datetime.today().strftime('%Y-%m-%d')
    if valuation_date == today:
        price = yf.Ticker(ticker).fast_info["last_price"]
        return price
    elif valuation_date_obj.weekday() < 5:
        start_date = valuation_date_obj
        end_date = valuation_date_obj + pd.Timedelta(days=1)
        data = yf.download(tickers = ticker, start = start_date, end = end_date)
        return data["Close"].iloc[0].item()
    else:
        if valuation_date_obj.weekday() >= 5:
            raise ValueError("Non-trading day")


#RISK_FREE_RATE_DATA

def option_tenor_calc(val_date:str, exp_date:str):
    valuation_date_obj = pd.to_datetime(val_date)
    expiration_obj = pd.to_datetime(exp_date)
    tenor_in_year = int((expiration_obj - valuation_date_obj).days)/365
    return tenor_in_year

def surrounding_lower(option_tenor, FRED_SERIES):
    smaller_tenors = {
        series_id: tenor
        for series_id, tenor in FRED_SERIES.items()
        if tenor <= option_tenor
    }
    if len(smaller_tenors) == 0:
        lower_id = min(FRED_SERIES, key=FRED_SERIES.get)
        return lower_id

    lower_id = max(smaller_tenors, key=smaller_tenors.get)
    return lower_id

def surrounding_upper(option_tenor, FRED_SERIES):
    higher_tenors = {
        series_id: tenor
        for series_id, tenor in FRED_SERIES.items()
        if tenor >= option_tenor
    }
    higher_id = min(higher_tenors, key=higher_tenors.get)
    return higher_id


def fred_rf_rate(val_date: str, lower_id: str, upper_id: str):
    val_date_obj = pd.to_datetime(val_date)
    obs_start = val_date_obj - pd.Timedelta(days=14)

    lower_series = fred.get_series(lower_id, observation_end=val_date_obj, observation_start=obs_start)
    upper_series = fred.get_series(upper_id, observation_end=val_date_obj, observation_start=obs_start)

    combined = pd.DataFrame({
        lower_id: lower_series,
        upper_id: upper_series
    })
    return combined


def interpolated_rate(data: pd.DataFrame, opt_tenor: str, surr_low: str, surr_up: str):
    latest_row = data.dropna().iloc[-1]

    lower_rate = latest_row[surr_low] / 100
    upper_rate = latest_row[surr_up] / 100

    lower_tenor = FRED_SERIES[surr_low]
    upper_tenor = FRED_SERIES[surr_up]

    interpolated_rate = np.interp(opt_tenor, [lower_tenor, upper_tenor], [lower_rate, upper_rate])

    return interpolated_rate



def get_risk_free_rate(val_date:str, exp_date:str):
    option_tenor = option_tenor_calc(val_date=val_date, exp_date=exp_date)
    surr_lower = surrounding_lower(option_tenor=option_tenor, FRED_SERIES=FRED_SERIES)
    surr_upper = surrounding_upper(option_tenor=option_tenor, FRED_SERIES=FRED_SERIES)
    data = fred_rf_rate(val_date=val_date, lower_id=surr_lower, upper_id=surr_upper)
    int_rate = interpolated_rate(data=data, opt_tenor=option_tenor, surr_low=surr_lower, surr_up=surr_upper)
    return int_rate



