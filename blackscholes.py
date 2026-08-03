import numpy as np
from scipy.stats import norm


def bs_call (S, K, T, r, vol):
    d1 = (np.log(S/K) + (r + 0.5 * vol ** 2) * T) / (vol*np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    return S * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)

#divYIELD?