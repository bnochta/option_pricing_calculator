# Option Pricer — Black-Scholes & Binomial (CRR) Model

A valuation tool that prices European and American equity
options using both the **Black-Scholes** closed-form solution and the
**Cox-Ross-Rubinstein (CRR) binomial tree**. Market inputs — spot price,
risk-free rate, and volatility — are sourced automatically from Yahoo
Finance and the FRED API, so a full valuation can be produced from just a
ticker, a strike, and an expiration date.

Running both models side by side also serves as a built-in sanity check:
for European options, the binomial price should converge to the
Black-Scholes price as the number of steps increases.

---

## Calculation pipeline

### 1. Market data collection

- **Spot price** is pulled via `yfinance`. If `valuation_date` is today, the
  last traded price (`fast_info["last_price"]`) is used; otherwise the
  closing price on that trading day is retrieved.
- **Time to maturity (tenor)** is computed in years from the valuation and
  expiration dates:

  $$T = \frac{\text{expiration date} - \text{valuation date}}{365}$$

- **Risk-free rate** is derived from the U.S. Treasury yield curve (FRED),
  interpolated to match the option's tenor (see step 2).
- **Volatility** is estimated from historical returns (see step 3); an
  implied-volatility method is planned but not yet implemented.

### 2. Risk-free rate — yield curve interpolation

The FRED constant-maturity Treasury series bracketing the option's tenor are
identified, and the corresponding yields (observed closest to
`valuation_date`) are linearly interpolated to the exact tenor:

$$r = r_{lower} + \left(r_{upper} - r_{lower}\right)\cdot
\frac{T - T_{lower}}{T_{upper} - T_{lower}}$$

Series used: `DGS1MO`, `DGS3MO`, `DGS6MO`, `DGS1`, `DGS2`, `DGS5`, `DGS10`,
`DGS30`.

### 3. Historical volatility estimation

Daily log returns are computed from the closing price series over the
lookback window (`hist_vol_lookback`, in years), and annualized:

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right), \qquad
\sigma_{annual} = \sigma_{daily} \cdot \sqrt{252}$$

### 4. Black-Scholes pricing

Closed-form European option prices are computed as:

$$C = S e^{-qT}N(d_1) - Ke^{-rT}N(d_2)$$

$$P = Ke^{-rT}N(-d_2) - Se^{-qT}N(-d_1)$$

where

$$d_1 = \frac{\ln(S/K) + \left(r - q + \tfrac{1}{2}\sigma^2\right)T}
{\sigma\sqrt{T}}, \qquad d_2 = d_1 - \sigma\sqrt{T}$$

A **put-call parity check** is run automatically to validate the inputs:

$$C - P = Se^{-qT} - Ke^{-rT}$$

### 5. Binomial (CRR) tree pricing

A recombining binomial tree with $n$ steps is built using the standard CRR
parameterization:

$$u = e^{\sigma\sqrt{\Delta t}}, \qquad d = \frac{1}{u}, \qquad
p = \frac{e^{(r-q)\Delta t} - d}{u - d}, \qquad \Delta t = \frac{T}{n}$$

Terminal payoffs are computed at maturity, and the tree is solved backward
via risk-neutral discounting:

$$V_{i,j} = e^{-r\Delta t}\left[p \cdot V_{i+1,j+1} +
(1-p)\cdot V_{i+1,j}\right]$$

For **American** options, at each node the continuation value is compared
against immediate exercise, and the greater of the two is kept:

$$V_{i,j} = \max\left(\text{continuation},\ \text{exercise payoff}\right)$$

For **European** options, only the continuation (discounted expectation)
value is used, with no early-exercise comparison.

---

## Input parameters

| Parameter | Description |
|---|---|
| `option_style` | `european` or `american` |
| `option_type` | `call` or `put` |
| `ticker` | Underlying equity ticker |
| `valuation_date` | Pricing (as-of) date, `YYYY-MM-DD` |
| `expiration` | Option expiration date, `YYYY-MM-DD` |
| `strike` | Strike price |
| `volatility_method` | `historical` (`implied` planned, not yet implemented) |
| `hist_vol_lookback` | Lookback window for historical volatility, in years |
| `n_for_binomial` | Number of steps in the binomial tree |
| `q` | Continuous dividend yield (default `0.0`) |

---

## Data sources

- **Spot & historical price data:** Yahoo Finance (`yfinance` package)
- **Risk-free rate curve:** FRED API (`fredapi` package), U.S. Treasury
  constant-maturity series
- **Volatility:** Computed in-house from historical price data (no external
  vol source)

---

## Requirements

- Python 3.9+
- `yfinance`, `pandas`, `numpy`, `scipy`, `matplotlib`, `fredapi`,
  `python-dotenv`

A FRED API key is required — register at
https://fred.stlouisfed.org/docs/api/api_key.html and store it in a `.env`
file in the project root:


---

## Usage

Set the inputs at the top of `main.ipynb` and run all cells:

```python
option_style = "american"      # "european" or "american"
valuation_date = "2026-08-04"  # YYYY-MM-DD
ticker = "MSFT"
expiration = "2026-08-05"
strike = 487.5
option_type = "Call"           # "call" or "put"
volatility_method = "historical"
hist_vol_lookback = 0.01       # in years
n_for_binomial = 1500          # number of binomial tree steps
```

The notebook fetches all market data, displays a summary input table, runs
the put-call parity check, and prints both the Black-Scholes and binomial
option prices.


---

## Notes & limitations

- Only `historical` volatility is implemented; `implied` volatility is
  planned.
- Black-Scholes assumes European exercise; early exercise is only modeled
  in the binomial tree.
- Spot price lookup supports the current day (last price) or a valid past
  trading day; weekends/holidays raise an error.
- Data quality depends on Yahoo Finance and FRED availability.

---

## Future development

- **Implied volatility support** — deriving `vol` from observed option
  market prices instead of historical returns.
- **Greeks calculation** (delta, gamma, vega, theta, rho) for both models.
- **Convergence visualization** — plotting binomial price vs. number of
  steps against the Black-Scholes benchmark.

---