import yfinance as yf
import pandas as pd
import datetime as dt
from scipy.sparse import csc_matrix
import matplotlib.pyplot as plt
import numpy as np

import hist_volatility
from riskfree_and_spot import *
from hist_volatility import *

def get_binomial(opt_style:str,opt_type:str,n:int, S:float, K:float, T:float, r:float, vol:float):
    N = n + 1

    S0 = S
    K = K
    t = T
    delta_t = t / N
    sigma = vol
    u = np.exp(sigma * np.sqrt(delta_t))
    d = 1 / u
    r = r
    p = (np.exp(r * delta_t) - d) / (u - d)

    stock_prices = np.zeros( (N, N) )
    opt_prices = np.zeros( (N, N) )

    stock_prices[0,0] = S0

    for i in range(1, N):
        M = i + 1
        stock_prices[i, 0] = d * stock_prices[i-1, 0]
        for j in range(1, M):
            stock_prices[i, j] = u * stock_prices[i - 1, j - 1]

    if opt_type == "call":
        expir = stock_prices[-1, :] - K
    elif opt_type == "put":
        expir = K - stock_prices[-1, :]

    expir = np.where(expir >= 0, expir, 0)


    opt_prices[-1, : ] = expir

    for i in range(N -2, -1, -1):
        for j in range(i + 1):
            continuation = np.exp(-r * delta_t) * ((1 -p) * opt_prices[i + 1, j] + p * opt_prices[i +1 , j + 1])

            if opt_style.lower() == "american":
                if opt_type == "call":
                    exercise = max(stock_prices[i, j] - K, 0)
                elif opt_type == "put":
                    exercise = max(K - stock_prices[i, j], 0)
                opt_prices[i, j] = max(continuation, exercise)
            elif opt_style.lower() == "european":
                opt_prices[i, j] = continuation

    return (opt_prices[0,0].item())