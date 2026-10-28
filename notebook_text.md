# Tail Risk Modelling of NIFTY 50 Using Extreme Value Theory
### A 15-Year Empirical Study (2011–2026) | EVT / GARCH-EVT Framework

---

> To know
> **Confidence Level:** 99% (α = 0.01) throughout.
> **Dataset:** 3,716 daily closing prices of the NIFTY 50 index sourced from [Investing.com](https://in.investing.com/indices/s-p-cnx-nifty-historical-data).
> **Models Evaluated:** Normal Distribution, Historical Simulation, Student-*t*, Standalone POT (EVT), GARCH-EVT.

---

## 1. Introduction

Standard risk models — such as parametric Value-at-Risk (VaR) under the Normal distribution — systematically underestimate the probability and magnitude of extreme market losses. This occurs because equity return distributions exhibit **fat tails** (more extreme outcomes than the Gaussian predicts) and **volatility clustering** (large shocks tend to be followed by further large shocks).

**Extreme Value Theory (EVT)** provides a statistically principled framework for modelling the tail of a distribution beyond the range of historical observation. When combined with a GARCH filter that first removes time-varying volatility, the resulting **GARCH-EVT model** produces conditional, dynamic VaR and Expected Shortfall (ES/CVaR) estimates that adapt day-to-day to market regimes.

This report presents the results of applying this full pipeline to 15 years of NIFTY 50 daily returns.

---

## 2. Dataset Overview

| Property | Value |
|:---|:---|
| Index | NIFTY 50 |
| Data period | 2011 – 2026 |
| Total observations | 3,716 trading days |
| Return type | Daily log returns |
| Returns available (after differencing) | **3,715** |

The return distribution exhibits the characteristic **leptokurtic** (fat-tailed) shape — a tall central peak and heavier tails than a Normal distribution — providing immediate visual evidence that Gaussian VaR will be inadequate.

---

## 3. Benchmark Model Results

Three classical models were estimated at **99% confidence** (α = 0.01):

### 3.1 Normal Distribution

| Metric | Value |
|:---|:---:|
| 99% VaR | **2.41%** |
| 99% CVaR (Expected Shortfall) | **2.76%** |

### 3.2 Historical Simulation

| Metric | Value |
|:---|:---:|
| 99% VaR | **2.53%** |
| 99% CVaR | **3.49%** |

### 3.3 Student-*t* Distribution

The Student-*t* was fitted by Maximum Likelihood Estimation. The fitted degrees of freedom ν = **2.38** indicate an extremely heavy-tailed distribution.

| Metric | Value |
|:---|:---:|
| Fitted degrees of freedom (ν) | 2.38 |
| 99% VaR | **3.63%** |
| 99% CVaR | **6.28%** |

> The very low degrees of freedom (ν ≈ 2.38) causes the Student-*t* to set an overly wide VaR threshold globally — a consequence shown clearly in the backtesting results (Section 5).

### 3.4 Summary: Static Benchmark VaR & CVaR at 99%

| Model | 99% VaR | 99% CVaR |
|:---|:---:|:---:|
| Normal | 2.41% | 2.76% |
| Historical Simulation | 2.53% | 3.49% |
| Student-*t* | 3.63% | 6.28% |

---

## 4. Standalone POT (Unconditional EVT) Results

The Peaks Over Threshold (POT) method was applied directly to raw NIFTY 50 losses, fitting a **Generalized Pareto Distribution (GPD)** to loss exceedances above the 90th percentile threshold.

### 4.1 Fitted GPD Parameters

| Parameter | Value |
|:---|:---:|
| Loss threshold *u* (90th percentile) | **1.997%** |
| GPD tail shape ξ | **−0.1643** |
| GPD scale β | **0.01218** |



### 4.2 Static EVT Risk Estimates at 99%

| Metric | Value |
|:---|:---:|
| 99% VaR (Standalone POT) | **4.33%** |
| 99% CVaR (Standalone POT) | **5.05%** |

---

## 5. GARCH-EVT Results

### 5.1 Volatility Clustering: Engle ARCH LM Test

Before building the GARCH model, the presence of ARCH effects (time-varying volatility) was formally tested using **Engle's Lagrange Multiplier test** with 10 lags.

| Statistic | Value | p-value |
|:---|:---:|:---:|
| LM statistic | 919.658 | **3.74 × 10⁻¹⁹¹** |
| F statistic | 121.978 | **2.51 × 10⁻²²⁰** |
| **Conclusion** | **Reject H₀** | **Strong ARCH effects present** |

 3.74 × 10⁻¹⁹¹ is effectively zero. NIFTY 50 volatility is **not constant over time**. Static risk models that assume constant variance are fundamentally misspecified for this data.

### 5.2 GARCH(1,1) Fit and GPD on Standardized Residuals

A GARCH(1,1) model with Student-*t* innovations was fitted to the chronologically ordered returns. The fitted GPD was then applied to the upper tail of the **standardized residuals** (returns divided by their estimated daily volatility), removing time-varying effects before EVT modelling.

| Parameter | Value |
|:---|:---:|
| GARCH next-day conditional volatility σ̂ | **0.825%** |
| GPD tail shape ξ (on standardized losses) | **+0.0347** |
| GPD scale β (on standardized losses) | **0.6278** |

After GARCH filtering, ξ is **positive** — correctly revealing a heavy-tailed innovation process.

### 5.3 GARCH Residual Diagnostics (Ljung-Box Test)

Standardized residuals and their squares were tested for remaining serial autocorrelation:

| Test | Lag | Statistic | p-value | Result |
|:---|:---:|:---:|:---:|:---:|
| Residuals | 10 | 16.264 | 0.0923 | ✅ No autocorrelation |
| Residuals | 20 | 21.808 | 0.3510 | ✅ No autocorrelation |
| Squared residuals | 10 | 16.762 | 0.0798 | ✅ No ARCH effects remain |
| Squared residuals | 20 | 25.803 | 0.1724 | ✅ No ARCH effects remain |

The GARCH(1,1) model has successfully captured all serial structure in the NIFTY 50 return series.

### 5.4 GARCH-EVT Risk Estimates (Next-Day Conditional Forecast)

| Metric | Value |
|:---|:---:|
| **99% Conditional VaR** | **2.224%** |
| **99% Conditional Expected Shortfall** | **2.806%** |

---

## 6. In-Sample Backtesting (3,715 Days)

### 6.1 Kupiec POF Test — Unconditional Coverage

Tests whether the observed number of VaR breaches matches the expected number at 99% confidence.

**Expected breaches:** 3,715 × 0.01 = **37.15 days**

| Model | Exceptions | Rate | LR Statistic | p-value | Verdict |
|:---|:---:|:---:|:---:|:---:|:---:|
| Normal | 45 / 3,715 | 1.211% | 1.570 | 0.2103 | ✅ PASS |
| Historical Simulation | 38 / 3,715 | 1.023% | 0.019 | 0.8889 | ✅ PASS |
| Student-*t* | 12 / 3,715 | 0.323% | 23.350 | 1.35 × 10⁻⁶ | ❌ FAIL |
| Standalone POT | 31 / 3,715 | 0.834% | 1.090 | 0.2965 | ✅ PASS |
| **GARCH-EVT** | **36 / 3,714** | **0.969%** | **0.036** | **0.8501** | ✅ **PASS** |

**Interpretation:**
- The **Student-*t*** model produces only 12 breaches (expected 37.2) — its global over-wide threshold is a failure.
- **Normal, Historical, POT, and GARCH-EVT** all pass with breach counts close to the expected 37.2.
- **GARCH-EVT** achieves the closest match (36 breaches, p = 0.85).

### 6.2 Christoffersen Independence Test — Conditional Coverage

Tests whether VaR breaches cluster together across consecutive trading days. The critical cell is **n₁₁ — back-to-back breach days**. A model with n₁₁ > 0 is failing during crisis regimes, when it matters most.

| Model | n₀₀ | n₀₁ | n₁₀ | **n₁₁** | LR Statistic | p-value | Verdict |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Normal | 3,628 | 41 | 41 | **4** | 9.588 | 0.00196 | ❌ FAIL |
| Historical Simulation | 3,641 | 35 | 35 | **3** | 7.411 | 0.00648 | ❌ FAIL |
| Student-*t* | 3,691 | 11 | 11 | **1** | 4.737 | 0.02953 | ❌ FAIL |
| Standalone POT | 3,654 | 29 | 29 | **2** | 4.900 | 0.02686 | ❌ FAIL |
| **GARCH-EVT** | **3,641** | **36** | **36** | **0** | **0.705** | **0.4011** | ✅ **PASS** |

> [!IMPORTANT]
> **GARCH-EVT is the only model achieving n₁₁ = 0** — zero consecutive breach days — across the full 15-year sample. Every static model, including those that passed the Kupiec test, failed here. This is the most practically significant finding: during market crashes, GARCH dynamically widens the VaR threshold, preventing repeated violations on consecutive days.

---

## 7. Out-of-Sample Rolling Walk-Forward Backtest (992 Days)

To test the model on genuinely unseen data, a rolling walk-forward backtest was run over the final **4 years** (2022–2026). At each step, the model was refitted exclusively on past data — no lookahead bias.

| Configuration | Value |
|:---|:---|
| Out-of-sample period | 2022-10-06 to 2026-10-06 |
| Observations | 992 trading days |
| Training window | 10 years, refitted monthly |
| Expected breaches | 992 × 0.01 = **9.9 days** |

### Out-of-Sample Backtest Results

| Test | Statistic | p-value | Verdict |
|:---|:---:|:---:|:---:|
| Exceptions observed | **7** (rate: 0.706%) | — | — |
| **Kupiec POF** | LR = 0.968 | **0.3253** | ✅ PASS |
| **Christoffersen Independence** | LR = 0.100 | **0.7523** | ✅ PASS |

The model passed both tests on genuinely unseen data. All 7 breaches were isolated — no consecutive breach days occurred in the 4-year out-of-sample period.

---

## 8. Expected Shortfall Calibration Backtest

Beyond VaR frequency, the **ES calibration test** validates whether the model accurately predicts the *average severity* of losses on breach days.

A Newey-West HAC-robust z-test was applied to the mean calibration residual across all 992 out-of-sample days:

| Metric | Value |
|:---|:---:|
| Observations | 992 |
| VaR breaches | 7 (expected ≈ 9.92) |
| Mean ES calibration residual | −0.000897 |
| HAC z-statistic | −0.286 |
| **p-value** | **0.7745** |
| **Verdict** | ✅ **PASS** |

The p-value of 0.77 provides no statistical basis for rejecting correct ES calibration. The slight negative residual (model marginally over-predicts loss severity) is negligible.


ly 7 breach days, the ES backtest has limited statistical power. Basel IV uses 97.5% confidence (not 99%) precisely to generate more breach observations for a well-powered ES test.
---

## 9. Final Model Scorecard

### Combined Kupiec + Christoffersen Results

| Model | Kupiec | Christoffersen | n₁₁ | Overall |
|:---|:---:|:---:|:---:|:---:|
| Normal | ✅ | ❌ | 4 | ❌ |
| Historical Simulation | ✅ | ❌ | 3 | ❌ |
| Student-*t* | ❌ | ❌ | 1 | ❌ |
| Standalone POT | ✅ | ❌ | 2 | ❌ |
| **GARCH-EVT (in-sample)** | ✅ | ✅ | **0** | ✅ |
| **GARCH-EVT (out-of-sample)** | ✅ | ✅ | **0** | ✅ |

### Complete Risk Metric Comparison at 99%

| Model | 99% VaR | 99% CVaR/ES | Type |
|:---|:---:|:---:|:---|
| Normal | 2.41% | 2.76% | Static |
| Historical Simulation | 2.53% | 3.49% | Static |
| Student-*t* | 3.63% | 6.28% | Static (over-conservative) |
| Standalone POT | 4.33% | 5.05% | Static EVT |
| **GARCH-EVT** | **2.22%** | **2.81%** | **Dynamic EVT** |

---

## 10. Key Findings

**1. NIFTY 50 volatility is strongly time-varying.**
The Engle ARCH LM test (LR = 919.7, p ≈ 0) provides near-conclusive evidence of volatility clustering. Any risk model assuming constant variance is fundamentally misspecified for this data.

**2. All static models fail the independence test.**
At 99% confidence, Normal, Historical Simulation, Student-*t*, and Standalone POT all experience consecutive breach days (n₁₁ ≥ 1) and fail the Christoffersen test. During market stress, static models are breached repeatedly on consecutive days — the most dangerous scenario for a risk manager.

**3. GARCH-EVT is the only model to pass all tests.**
GARCH-EVT passes both Kupiec (frequency) and Christoffersen (independence) tests — both in-sample across 15 years and out-of-sample across 4 years. Its dynamic threshold correctly widens during volatile regimes, preventing clustering of failures.

**4. EVT alone is not sufficient — the GARCH filter is essential.**
Standalone POT uses the theoretically correct GPD for tail modelling but still fails the independence test (n₁₁ = 2). The GARCH volatility filter, not just EVT, is the critical ingredient.

**5. The model generalizes cleanly out-of-sample.**
7 out-of-sample breaches vs. 9.9 expected (Kupiec p = 0.33), zero consecutive breach days (Christoffersen p = 0.75), and a passing ES calibration test (p = 0.77) together confirm the GARCH-EVT model is not over-fitted.

---

## 11. Limitations and Future Work

| Limitation | Proposed Extension |
|:---|:---|
| Single asset (NIFTY 50 only) | Multi-asset portfolio with **Copula-based tail dependence** |
| ES backtest underpowered at 99% | Re-run at 97.5% (Basel IV standard) |
| GARCH(1,1) only — symmetric volatility | Test **GJR-GARCH** (negative shock leverage effect) |
| No stress test / return-level analysis | Compute GPD return levels for 1-in-10, 50, 100 year scenarios |
| GPD threshold fixed at 90th percentile | Apply Mean Excess Plot and Hill estimator for optimal threshold selection |

---

## 12. References

1. McNeil, A. J., & Frey, R. (2000). Estimation of tail-related risk measures for heteroscedastic financial time series: an extreme value approach. *Journal of Empirical Finance*, 7(3–4), 271–300.
2. Kupiec, P. H. (1995). Techniques for verifying the accuracy of risk measurement models. *Journal of Derivatives*, 3(2), 73–84.
3. Christoffersen, P. F. (1998). Evaluating interval forecasts. *International Economic Review*, 39(4), 841–862.
4. Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007.
5. Pickands, J. (1975). Statistical inference using extreme order statistics. *Annals of Statistics*, 3(1), 119–131.
6. Acerbi, C., & Szekely, B. (2014). Back-testing expected shortfall. *Risk Magazine*, December 2014.

---

*NIFTY 50 Historical Data (2011–2026) · Confidence Level: 99% · October 2026*
