import numpy as np
from scipy.stats import norm


def bs_call (S, K, T, r, vol):
    d1 = (np.log(S/K) + (r + 0.5 * vol ** 2) * T) / (vol*np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    return S * norm.cdf(d1) - np.exp(-r * T) * K * norm.cdf(d2)

def bs_put(S, K, T, r, vol):
    d1 = (np.log(S/K) + (r + 0.5 * vol ** 2) * T) / (vol * np.sqrt(T))
    d2 = d1 - vol * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def bs_result(opt_type:str, S:float, K:float, T:float, r:float, vol:float):
    if opt_type.lower() == "call":
        return bs_call(S=S, K=K, T=T, r=r, vol=vol)
    elif opt_type.lower() == "put":
        return bs_put(S=S, K=K, T=T, r=r, vol=vol)
    else:
        raise ValueError("opt_type must be 'call' or 'put'")



def test_parity(S, K, T, r, vol):
    call_p = bs_call(S, K, T, r, vol)
    put_p = bs_put(S, K, T, r, vol)
    lhs = call_p - put_p
    rhs = S - K * np.exp(-r * T)

    assert np.isclose(lhs, rhs, atol=1e-6), f"Parity violated: {lhs} != {rhs}"
    print("Put-call parity OK:", lhs, "≈", rhs)

#divYIELD?