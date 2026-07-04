# Salesforce DCF & Trading Comps Valuation

**Author:** Priya Rastogi
**Date:** July 2026
**Purpose:** Two-method valuation of Salesforce (CRM) using DCF and trading comparables

---

## 📋 Overview

This Python-based valuation module performs a comprehensive analysis of Salesforce using two industry-standard methods:

1. **Discounted Cash Flow (DCF) Analysis** — intrinsic value based on future cash flow projections
2. **Trading Comparables Analysis** — relative valuation using SaaS peer multiples

The script reads financial forecasts from your integrated 3-statement Excel model and outputs:
- Intrinsic value per share
- Sensitivity analysis (WACC vs. terminal growth)
- Comparables-implied valuation range
- Investment recommendation (Buy/Hold/Sell)
- Visual charts (FCF bridge, heatmap, football field)

---

## 🚀 Quick Start

### Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure your Excel file is in the same directory:**
   - File name: `5 years data copy.xlsx`
   - Required sheets: `Forecasting`, `Assumptions`

3. **Run the valuation:**
   ```bash
   python salesforce_valuation.py
   ```

### Output

The script will:
- Print detailed valuation steps to the console
- Save charts as `salesforce_valuation_charts.png`

---

## 📊 Valuation Methods Explained (Plain Language)

### Method 1: Discounted Cash Flow (DCF)

**What is it?**
DCF calculates what Salesforce is worth *today* based on all the cash it will generate *in the future*. It's like asking: "If I buy this company, how much cash will I get back, and what's that worth to me right now?"

**How it works:**

1. **Project Free Cash Flows (FCF)** — For each year (FY2027-2031), we calculate:
   - Start with **EBIT** (operating profit before interest and taxes)
   - Subtract taxes → **NOPAT** (Net Operating Profit After Tax)
   - Add back **D&A** (non-cash depreciation expense)
   - Subtract **Capex** (cash spent on new equipment/infrastructure)
   - Subtract **Change in Working Capital** (cash tied up in operations)
   - **Result = Unlevered Free Cash Flow** (cash available to all investors)

2. **Calculate Terminal Value** — After FY2031, we assume Salesforce keeps growing forever at a steady rate (2.5%). We use the Gordon Growth Model to value all those future years in one number.

3. **Discount Everything to Today** — Money tomorrow is worth less than money today. We use the **WACC** (Weighted Average Cost of Capital) as the discount rate. WACC represents what investors expect to earn, calculated as:
   - **Cost of Equity** (from CAPM: Risk-Free Rate + Beta × Equity Risk Premium)
   - **After-Tax Cost of Debt**
   - Weighted by Salesforce's capital structure (85% equity, 15% debt)

4. **Add it all up:**
   - Sum of discounted FCFs (2027-2031)
   - Plus discounted Terminal Value
   - **= Enterprise Value** (what the whole business is worth)
   - Subtract Net Debt (debt minus cash)
   - Divide by shares outstanding
   - **= Intrinsic Value per Share**

**Key Assumption:** If the stock price is *below* intrinsic value, it's undervalued (BUY). If *above*, it's overvalued (SELL).

---

### Method 2: Trading Comparables (Comps)

**What is it?**
Comps ask: "How are similar companies valued by the market?" If Adobe trades at 12x revenue, maybe Salesforce should too.

**How it works:**

1. **Pick Peer Companies** — We use SaaS peers with similar business models:
   - Adobe (Creative Cloud, Experience Cloud)
   - ServiceNow (enterprise workflow software)
   - Workday (HR & finance cloud)
   - Oracle (cloud applications)

2. **Gather Multiples** — For each peer, we look at:
   - **EV/Revenue** — Enterprise Value divided by Revenue (how many dollars of value per dollar of sales)
   - **EV/FCF** — Enterprise Value divided by Free Cash Flow (how many dollars of value per dollar of cash generated)

3. **Calculate Median** — Take the middle value across all peers (median is better than average because it ignores outliers).

4. **Apply to Salesforce** — Multiply Salesforce's FY2027 revenue and FCF by the peer medians:
   - EV = Salesforce Revenue × Median EV/Revenue
   - EV = Salesforce FCF × Median EV/FCF

5. **Convert to Price per Share:**
   - Subtract Net Debt from Enterprise Value → Equity Value
   - Divide by shares outstanding → Price per Share

**Key Assumption:** If Salesforce trades *below* the comps-implied range, it's undervalued relative to peers.

---

## 🔧 Customizing Assumptions

All key inputs are at the **top of the script** (lines 24-44). You can easily change:

### DCF Inputs:
```python
RISK_FREE_RATE = 0.042        # 10-year Treasury (update from FRED or Bloomberg)
BETA = 1.05                    # Salesforce beta (Yahoo Finance / Bloomberg)
EQUITY_RISK_PREMIUM = 0.06     # Historical ERP (~6%)
COST_OF_DEBT = 0.045           # Pre-tax cost of debt (weighted avg of bonds)
PERPETUAL_GROWTH_RATE = 0.025  # Terminal growth (2-3% typical for mature tech)
WEIGHT_EQUITY = 0.85           # Target capital structure
WEIGHT_DEBT = 0.15
```

### Market Data:
```python
CURRENT_STOCK_PRICE = 245.00   # Update with latest price
SHARES_OUTSTANDING = 946       # Million shares (from 10-K)
```

### Peer Multiples:
```python
PEER_MULTIPLES = {
    'Adobe': {'EV/Revenue': 12.5, 'EV/FCF': 28.0},
    'ServiceNow': {'EV/Revenue': 14.2, 'EV/FCF': 32.5},
    'Workday': {'EV/Revenue': 8.9, 'EV/FCF': 25.0},
    'Oracle': {'EV/Revenue': 7.5, 'EV/FCF': 18.5}
}
```
*Update these from CapIQ, Bloomberg, or Koyfin*

---

## 📈 Output Explained

### Console Output

The script prints step-by-step results:

1. **Data Loading** — Confirms Excel data read successfully
2. **WACC Calculation** — Shows cost of equity (CAPM), cost of debt, and final WACC
3. **Free Cash Flow Forecast** — Year-by-year breakdown (EBIT → NOPAT → FCF)
4. **Terminal Value** — Perpetual growth calculation
5. **Present Value** — Discounted FCFs and intrinsic value per share
6. **Sensitivity Table** — Intrinsic value across different WACC and growth assumptions
7. **Comps Analysis** — Peer multiples and implied valuation range
8. **Investment Recommendation** — Buy/Hold/Sell based on blended fair value

### Visual Charts (PNG file)

1. **FCF Bridge (Waterfall)** — Shows how EBIT flows to FCF (adds D&A, subtracts Capex & NWC)
2. **Sensitivity Heatmap** — Color-coded matrix showing intrinsic value sensitivity to WACC and terminal growth
3. **Football Field Chart** — Horizontal bar chart comparing:
   - DCF intrinsic value
   - Comps (EV/Revenue)
   - Comps (EV/FCF)
   - Blended fair value
   - Current market price

---

## 🎯 Interpretation Guide

### DCF vs. Comps: Which to Trust?

**DCF is better when:**
- You have high confidence in your cash flow forecasts
- The company has clear, predictable operations
- You want an **intrinsic** (fundamental) view

**Comps are better when:**
- The company is growing rapidly (less predictable long-term)
- You want to understand **relative** valuation (vs. market)
- DCF assumptions are highly uncertain

**Best practice:** Use **both** methods and take a blended average. If they diverge significantly, ask why:
- Is the market overvaluing peers? (DCF < Comps → market exuberance)
- Are your DCF assumptions too conservative? (DCF > Comps → check growth/WACC)

### Sensitivity Analysis

The heatmap shows how sensitive your valuation is to two key assumptions:
- **WACC** (horizontal axis) — higher WACC = lower value (future cash is worth less)
- **Terminal Growth** (vertical axis) — higher growth = higher value (more cash forever)

**Red flag:** If a small change in WACC or growth swings the value by 50%+, your model is **highly sensitive**. Be cautious with your recommendation.

---

## 🧠 Interview Talking Points

When presenting this model, emphasize:

1. **Two-method triangulation** — "I didn't rely on a single method; I cross-checked DCF with trading comps to validate the range."

2. **Sensitivity awareness** — "I ran a sensitivity table because WACC and terminal growth are judgment calls. A 50bps change in WACC moves the value by X%, so I'm mindful of that uncertainty."

3. **Unlevered FCF = correct metric** — "I used unlevered FCF (available to all investors) because we're valuing the enterprise, then backed out debt to get to equity value."

4. **CAPM for cost of equity** — "I calculated WACC using CAPM for the equity component. Beta of 1.05 means Salesforce is slightly more volatile than the market."

5. **Gordon Growth for terminal value** — "I used a 2.5% perpetual growth rate, in line with long-term GDP growth, because Salesforce is a mature SaaS business."

6. **Comps cross-check** — "I benchmarked against Adobe, ServiceNow, Workday, and Oracle. Salesforce trades at a [premium/discount] to peers, which makes sense given its [market share/growth/margins]."

---

## 📁 File Structure

```
salesforce_valuation/
│
├── salesforce_valuation.py       # Main Python script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── 5 years data copy.xlsx         # Your Excel model (input)
└── salesforce_valuation_charts.png  # Output charts
```

---

## ⚠️ Common Errors & Fixes

### Error: "FileNotFoundError: 5 years data copy.xlsx"
**Fix:** Ensure the Excel file is in the same directory as the script.

### Error: "ModuleNotFoundError: No module named 'pandas'"
**Fix:** Install dependencies: `pip install -r requirements.txt`

### Error: Chart not displaying
**Fix:** If running in a non-GUI environment (e.g., SSH), the chart will still save as PNG. Check `salesforce_valuation_charts.png`.

### Warning: "RuntimeWarning: divide by zero"
**Fix:** Check that WACC > perpetual growth rate. If WACC = 8% and growth = 8%, the Gordon Growth formula breaks (denominator = 0).

---

## 🔗 Data Sources

- **Risk-Free Rate:** [FRED 10-Year Treasury](https://fred.stlouisfed.org/series/DGS10)
- **Beta:** Yahoo Finance, Bloomberg Terminal
- **Peer Multiples:** CapIQ, Bloomberg, Koyfin, FactSet
- **Shares Outstanding:** Salesforce 10-K (latest filing)

---

## 📚 Further Reading

**DCF Methodology:**
- *Investment Valuation* by Aswath Damodaran (NYU Stern)
- McKinsey Valuation Handbook

**Trading Comps:**
- *Valuation* by McKinsey & Company
- Investment Banking textbooks (Rosenbaum & Pearl)

**Python for Finance:**
- *Python for Finance* by Yves Hilpisch

---

## ✅ Next Steps

1. **Update inputs** — Refresh risk-free rate, beta, and peer multiples with latest data
2. **Run the script** — `python salesforce_valuation.py`
3. **Review output** — Check if recommendation aligns with your investment thesis
4. **Iterate** — Test different scenarios (Bull case: higher growth, Bear case: higher WACC)
5. **Present** — Use the football field chart in pitches or interviews

---

## 📧 Contact

**Priya Rastogi**
priya08rastogi@gmail.com
[LinkedIn](https://www.linkedin.com/in/priya-rastogi-/)
[Portfolio](https://priyar08.github.io/priya-rastogi-portfolio/)

---

**Happy Valuing! 📊**
