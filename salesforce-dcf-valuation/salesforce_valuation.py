"""
SALESFORCE DCF & TRADING COMPS VALUATION
=========================================
This script performs a two-method valuation of Salesforce:
1. Discounted Cash Flow (DCF) analysis
2. Trading comparables (comps) analysis

Author: Priya Rastogi
Date: July 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# ============================================================================
# SECTION 1: INPUT ASSUMPTIONS (Easy to change for sensitivity)
# ============================================================================

# --- DCF Assumptions ---
RISK_FREE_RATE = 0.042        # 10-year Treasury yield (4.2%)
BETA = 1.05                    # Salesforce beta (source: Bloomberg/Yahoo Finance)
EQUITY_RISK_PREMIUM = 0.06     # Historical equity risk premium (6%)
COST_OF_DEBT = 0.045           # Pre-tax cost of debt (4.5%)
PERPETUAL_GROWTH_RATE = 0.025  # Terminal growth rate (2.5% conservative)

# --- Capital Structure (from most recent balance sheet FY2026) ---
# We'll read net debt from the model, but set target weights here
WEIGHT_EQUITY = 0.85           # 85% equity weight
WEIGHT_DEBT = 0.15             # 15% debt weight

# --- Current Market Data ---
CURRENT_STOCK_PRICE = 245.00   # Salesforce current price (update as needed)
SHARES_OUTSTANDING = 946       # Million shares (from FY2026 data)

# --- Trading Comps: Peer Multiples ---
# Input your own multiples from Bloomberg/CapIQ/FactSet
PEER_MULTIPLES = {
    'Adobe': {'EV/Revenue': 12.5, 'EV/FCF': 28.0},
    'ServiceNow': {'EV/Revenue': 14.2, 'EV/FCF': 32.5},
    'Workday': {'EV/Revenue': 8.9, 'EV/FCF': 25.0},
    'Oracle': {'EV/Revenue': 7.5, 'EV/FCF': 18.5}
}

# ============================================================================
# SECTION 2: DATA EXTRACTION FROM EXCEL
# ============================================================================

def load_financial_data(file_path):
    """
    Load forecast data from Excel file (5 years data copy.xlsx).

    Returns:
        Dictionary with forecasted financials for FY2027-2031
    """
    print("\n" + "="*70)
    print("STEP 1: LOADING FINANCIAL DATA FROM EXCEL")
    print("="*70)

    # Read the Forecasting sheet
    df = pd.read_excel(file_path, sheet_name='Forecasting', header=None)

    # Extract years (columns 7-11 represent FY2027-2031)
    years = [2027, 2028, 2029, 2030, 2031]

    # Extract key line items by row index
    # Row 3: Total Revenue
    # Row 17: EBITDA
    # Row 79: D&A
    # Row 83: Changes in working capital
    # Row 99: Capex
    # Row 32: Tax rate from Assumptions sheet

    revenue = df.iloc[3, 7:12].values  # Columns G-K (index 7-11)
    ebitda = df.iloc[17, 7:12].values
    da = df.iloc[79, 7:12].values
    change_in_nwc = df.iloc[83, 7:12].values
    capex = df.iloc[99, 7:12].values

    # Read tax rate from Assumptions sheet
    df_assumptions = pd.read_excel(file_path, sheet_name='Assumptions', header=None)
    tax_rate = df_assumptions.iloc[32, 1]  # Active Tax rate%

    # Calculate EBIT = EBITDA - D&A
    ebit = ebitda - da

    # Net Debt calculation (from FY2026 balance sheet for enterprise value)
    # Row 59: Long-term debt (column 6 = FY2026)
    # Row 56: Short-term debt
    # Row 32: Cash and cash equivalents
    lt_debt_fy26 = df.iloc[59, 6]
    st_debt_fy26 = df.iloc[56, 6]
    cash_fy26 = df.iloc[32, 6]
    net_debt = (lt_debt_fy26 + st_debt_fy26) - cash_fy26

    print(f"\nData loaded successfully for FY2027-2031")
    print(f"Tax Rate: {tax_rate:.2%}")
    print(f"Net Debt (FY2026): ${net_debt:,.0f}M")

    return {
        'years': years,
        'revenue': revenue,
        'ebit': ebit,
        'da': da,
        'capex': capex,
        'change_in_nwc': change_in_nwc,
        'tax_rate': tax_rate,
        'net_debt': net_debt
    }

# ============================================================================
# SECTION 3: DCF VALUATION
# ============================================================================

def calculate_wacc(rf, beta, erp, cost_of_debt, tax_rate, weight_equity, weight_debt):
    """
    Calculate Weighted Average Cost of Capital (WACC).

    WACC = (E/V)*Re + (D/V)*Rd*(1-Tax)
    where:
        Re = Cost of Equity (CAPM)
        Rd = Cost of Debt
        E/V = Equity weight
        D/V = Debt weight
    """
    # Step 1: Calculate cost of equity using CAPM
    # CAPM: Re = Rf + Beta * (Rm - Rf)
    cost_of_equity = rf + beta * erp

    # Step 2: After-tax cost of debt
    after_tax_cost_of_debt = cost_of_debt * (1 - tax_rate)

    # Step 3: WACC formula
    wacc = (weight_equity * cost_of_equity) + (weight_debt * after_tax_cost_of_debt)

    print(f"\n--- WACC Calculation ---")
    print(f"Cost of Equity (CAPM): {cost_of_equity:.2%}")
    print(f"  Risk-Free Rate: {rf:.2%}")
    print(f"  Beta: {beta}")
    print(f"  Equity Risk Premium: {erp:.2%}")
    print(f"After-Tax Cost of Debt: {after_tax_cost_of_debt:.2%}")
    print(f"WACC: {wacc:.2%}")

    return wacc

def calculate_unlevered_fcf(ebit, tax_rate, da, capex, change_in_nwc):
    """
    Calculate Unlevered Free Cash Flow (FCF).

    Formula:
    Unlevered FCF = EBIT * (1 - Tax) + D&A - Capex - Change in NWC

    This is the cash available to all investors (debt + equity holders)
    """
    # NOPAT = Net Operating Profit After Tax
    nopat = ebit * (1 - tax_rate)

    # Free Cash Flow calculation
    # Add back D&A (non-cash expense)
    # Subtract Capex (cash outflow for investments)
    # Subtract increase in working capital (cash tied up)
    fcf = nopat + da - capex - change_in_nwc

    return fcf

def calculate_terminal_value(final_fcf, wacc, perpetual_growth):
    """
    Calculate Terminal Value using Gordon Growth Model.

    Terminal Value = FCF(final year) * (1 + g) / (WACC - g)

    This represents the present value of all cash flows beyond the forecast period.
    """
    terminal_value = (final_fcf * (1 + perpetual_growth)) / (wacc - perpetual_growth)

    return terminal_value

def discount_cash_flows(fcf_array, terminal_value, wacc):
    """
    Discount all future cash flows to present value.

    PV = FCF / (1 + WACC)^t
    """
    pv_fcf = []

    # Discount each year's FCF
    for t, fcf in enumerate(fcf_array, start=1):
        pv = fcf / ((1 + wacc) ** t)
        pv_fcf.append(pv)

    # Discount terminal value (occurs at end of year 5)
    pv_terminal = terminal_value / ((1 + wacc) ** len(fcf_array))

    return pv_fcf, pv_terminal

def dcf_valuation(data):
    """
    Perform complete DCF valuation.
    """
    print("\n" + "="*70)
    print("STEP 2: DCF VALUATION")
    print("="*70)

    # Step 1: Calculate WACC
    wacc = calculate_wacc(
        RISK_FREE_RATE, BETA, EQUITY_RISK_PREMIUM,
        COST_OF_DEBT, data['tax_rate'],
        WEIGHT_EQUITY, WEIGHT_DEBT
    )

    # Step 2: Calculate unlevered FCF for each year
    fcf = calculate_unlevered_fcf(
        data['ebit'],
        data['tax_rate'],
        data['da'],
        data['capex'],
        data['change_in_nwc']
    )

    print("\n--- Free Cash Flow Forecast (FY2027-2031) ---")
    fcf_df = pd.DataFrame({
        'Year': data['years'],
        'EBIT': data['ebit'],
        'NOPAT': data['ebit'] * (1 - data['tax_rate']),
        'D&A': data['da'],
        'Capex': data['capex'],
        'Δ NWC': data['change_in_nwc'],
        'Unlevered FCF': fcf
    })
    print(fcf_df.to_string(index=False))

    # Step 3: Calculate terminal value
    terminal_value = calculate_terminal_value(fcf[-1], wacc, PERPETUAL_GROWTH_RATE)
    print(f"\n--- Terminal Value ---")
    print(f"Final Year FCF (FY2031): ${fcf[-1]:,.0f}M")
    print(f"Perpetual Growth Rate: {PERPETUAL_GROWTH_RATE:.1%}")
    print(f"Terminal Value: ${terminal_value:,.0f}M")

    # Step 4: Discount all cash flows to present value
    pv_fcf, pv_terminal = discount_cash_flows(fcf, terminal_value, wacc)

    print("\n--- Present Value of Cash Flows ---")
    pv_df = pd.DataFrame({
        'Year': data['years'],
        'FCF': fcf,
        'PV Factor': [(1/(1+wacc)**t) for t in range(1, 6)],
        'PV of FCF': pv_fcf
    })
    print(pv_df.to_string(index=False))
    print(f"\nPV of Terminal Value: ${pv_terminal:,.0f}M")

    # Step 5: Calculate Enterprise Value
    enterprise_value = sum(pv_fcf) + pv_terminal
    print(f"\n--- Enterprise Value ---")
    print(f"Sum of PV(FCF): ${sum(pv_fcf):,.0f}M")
    print(f"PV(Terminal Value): ${pv_terminal:,.0f}M")
    print(f"Enterprise Value: ${enterprise_value:,.0f}M")

    # Step 6: Calculate Equity Value and Price per Share
    equity_value = enterprise_value - data['net_debt']
    intrinsic_value_per_share = equity_value / SHARES_OUTSTANDING

    print(f"\n--- Equity Value & Intrinsic Price ---")
    print(f"Enterprise Value: ${enterprise_value:,.0f}M")
    print(f"Less: Net Debt: ${data['net_debt']:,.0f}M")
    print(f"Equity Value: ${equity_value:,.0f}M")
    print(f"Shares Outstanding: {SHARES_OUTSTANDING}M")
    print(f"Intrinsic Value per Share: ${intrinsic_value_per_share:.2f}")
    print(f"Current Stock Price: ${CURRENT_STOCK_PRICE:.2f}")

    upside = (intrinsic_value_per_share - CURRENT_STOCK_PRICE) / CURRENT_STOCK_PRICE
    print(f"Implied Upside/(Downside): {upside:+.1%}")

    return {
        'wacc': wacc,
        'fcf': fcf,
        'fcf_df': fcf_df,
        'terminal_value': terminal_value,
        'pv_fcf': pv_fcf,
        'pv_terminal': pv_terminal,
        'enterprise_value': enterprise_value,
        'equity_value': equity_value,
        'intrinsic_value_per_share': intrinsic_value_per_share,
        'upside': upside
    }

# ============================================================================
# SECTION 4: SENSITIVITY ANALYSIS
# ============================================================================

def sensitivity_analysis(data, base_wacc, base_growth):
    """
    Create sensitivity table showing intrinsic value across different
    WACC and terminal growth rate assumptions.
    """
    print("\n" + "="*70)
    print("STEP 3: SENSITIVITY ANALYSIS")
    print("="*70)

    # Define ranges for sensitivity
    wacc_range = np.arange(base_wacc - 0.02, base_wacc + 0.025, 0.005)  # ±2% around base
    growth_range = np.arange(0.015, 0.035, 0.005)  # 1.5% to 3.5%

    # Initialize results matrix
    sensitivity_matrix = np.zeros((len(growth_range), len(wacc_range)))

    # Calculate intrinsic value for each combination
    for i, growth in enumerate(growth_range):
        for j, wacc in enumerate(wacc_range):
            # Recalculate FCF with same assumptions
            fcf = calculate_unlevered_fcf(
                data['ebit'], data['tax_rate'],
                data['da'], data['capex'], data['change_in_nwc']
            )

            # Calculate terminal value with new assumptions
            tv = calculate_terminal_value(fcf[-1], wacc, growth)

            # Discount to present
            pv_fcf, pv_tv = discount_cash_flows(fcf, tv, wacc)

            # Enterprise value to equity value to price per share
            ev = sum(pv_fcf) + pv_tv
            equity = ev - data['net_debt']
            price = equity / SHARES_OUTSTANDING

            sensitivity_matrix[i, j] = price

    # Create DataFrame for display
    sensitivity_df = pd.DataFrame(
        sensitivity_matrix,
        index=[f'{g:.1%}' for g in growth_range],
        columns=[f'{w:.1%}' for w in wacc_range]
    )

    print("\nSensitivity Table: Intrinsic Value per Share")
    print(f"(Growth Rate vs. WACC)")
    print("\n" + sensitivity_df.to_string())

    return sensitivity_df, wacc_range, growth_range, sensitivity_matrix

# ============================================================================
# SECTION 5: TRADING COMPARABLES VALUATION
# ============================================================================

def comps_valuation(data):
    """
    Perform trading comparables valuation using peer multiples.
    """
    print("\n" + "="*70)
    print("STEP 4: TRADING COMPARABLES ANALYSIS")
    print("="*70)

    # Get Salesforce's metrics for FY2027 (or latest year)
    # Using FY2027 as the forward-looking year
    crm_revenue = data['revenue'][0]  # FY2027 revenue

    # Calculate Salesforce's FCF for FY2027
    crm_fcf = calculate_unlevered_fcf(
        data['ebit'][0:1],
        data['tax_rate'],
        data['da'][0:1],
        data['capex'][0:1],
        data['change_in_nwc'][0:1]
    )[0]

    print(f"\nSalesforce FY2027 Metrics:")
    print(f"  Revenue: ${crm_revenue:,.0f}M")
    print(f"  Unlevered FCF: ${crm_fcf:,.0f}M")

    # Extract peer multiples
    ev_revenue_multiples = [v['EV/Revenue'] for v in PEER_MULTIPLES.values()]
    ev_fcf_multiples = [v['EV/FCF'] for v in PEER_MULTIPLES.values()]

    # Calculate median multiples
    median_ev_revenue = np.median(ev_revenue_multiples)
    median_ev_fcf = np.median(ev_fcf_multiples)

    print(f"\n--- Peer Multiples ---")
    for peer, multiples in PEER_MULTIPLES.items():
        print(f"{peer:15s}: EV/Revenue = {multiples['EV/Revenue']:.1f}x, EV/FCF = {multiples['EV/FCF']:.1f}x")

    print(f"\nMedian EV/Revenue: {median_ev_revenue:.1f}x")
    print(f"Median EV/FCF: {median_ev_fcf:.1f}x")

    # Apply multiples to Salesforce
    ev_from_revenue = crm_revenue * median_ev_revenue
    ev_from_fcf = crm_fcf * median_ev_fcf

    # Convert to equity value
    equity_from_revenue = ev_from_revenue - data['net_debt']
    equity_from_fcf = ev_from_fcf - data['net_debt']

    # Price per share
    price_from_revenue = equity_from_revenue / SHARES_OUTSTANDING
    price_from_fcf = equity_from_fcf / SHARES_OUTSTANDING

    print(f"\n--- Implied Valuation from Comps ---")
    print(f"\nBased on EV/Revenue ({median_ev_revenue:.1f}x):")
    print(f"  Enterprise Value: ${ev_from_revenue:,.0f}M")
    print(f"  Equity Value: ${equity_from_revenue:,.0f}M")
    print(f"  Price per Share: ${price_from_revenue:.2f}")

    print(f"\nBased on EV/FCF ({median_ev_fcf:.1f}x):")
    print(f"  Enterprise Value: ${ev_from_fcf:,.0f}M")
    print(f"  Equity Value: ${equity_from_fcf:,.0f}M")
    print(f"  Price per Share: ${price_from_fcf:.2f}")

    return {
        'median_ev_revenue': median_ev_revenue,
        'median_ev_fcf': median_ev_fcf,
        'ev_from_revenue': ev_from_revenue,
        'ev_from_fcf': ev_from_fcf,
        'price_from_revenue': price_from_revenue,
        'price_from_fcf': price_from_fcf
    }

# ============================================================================
# SECTION 6: VALUATION SUMMARY & RECOMMENDATION
# ============================================================================

def valuation_summary(dcf_results, comps_results):
    """
    Compare DCF vs. Comps vs. Current Price and provide recommendation.
    """
    print("\n" + "="*70)
    print("STEP 5: VALUATION SUMMARY & RECOMMENDATION")
    print("="*70)

    dcf_price = dcf_results['intrinsic_value_per_share']
    comps_revenue_price = comps_results['price_from_revenue']
    comps_fcf_price = comps_results['price_from_fcf']
    current_price = CURRENT_STOCK_PRICE

    # Calculate average comps price
    avg_comps_price = (comps_revenue_price + comps_fcf_price) / 2

    # Calculate blended fair value (average of DCF and Comps)
    blended_fair_value = (dcf_price + avg_comps_price) / 2

    print(f"\n{'Method':<25s} {'Price':>12s} {'vs. Current':>15s}")
    print("-" * 55)
    print(f"{'DCF Intrinsic Value':<25s} ${dcf_price:>10.2f}  {((dcf_price/current_price-1)*100):>+13.1f}%")
    print(f"{'Comps (EV/Revenue)':<25s} ${comps_revenue_price:>10.2f}  {((comps_revenue_price/current_price-1)*100):>+13.1f}%")
    print(f"{'Comps (EV/FCF)':<25s} ${comps_fcf_price:>10.2f}  {((comps_fcf_price/current_price-1)*100):>+13.1f}%")
    print(f"{'Average Comps':<25s} ${avg_comps_price:>10.2f}  {((avg_comps_price/current_price-1)*100):>+13.1f}%")
    print("-" * 55)
    print(f"{'Blended Fair Value':<25s} ${blended_fair_value:>10.2f}  {((blended_fair_value/current_price-1)*100):>+13.1f}%")
    print(f"{'Current Market Price':<25s} ${current_price:>10.2f}")

    # Recommendation logic
    upside_downside = (blended_fair_value - current_price) / current_price

    print(f"\n{'='*70}")
    print("INVESTMENT RECOMMENDATION")
    print("="*70)

    if upside_downside > 0.15:
        recommendation = "UNDERVALUED - BUY"
        rationale = f"Stock trades at ${current_price:.2f}, {upside_downside:.1%} below blended fair value of ${blended_fair_value:.2f}."
    elif upside_downside < -0.15:
        recommendation = "OVERVALUED - SELL"
        rationale = f"Stock trades at ${current_price:.2f}, {abs(upside_downside):.1%} above blended fair value of ${blended_fair_value:.2f}."
    else:
        recommendation = "FAIRLY VALUED - HOLD"
        rationale = f"Stock trades within ±15% of fair value (current: ${current_price:.2f}, fair value: ${blended_fair_value:.2f})."

    print(f"\n{recommendation}")
    print(f"\n{rationale}")
    print(f"\nUpside/(Downside) to Fair Value: {upside_downside:+.1%}")

    return {
        'dcf_price': dcf_price,
        'avg_comps_price': avg_comps_price,
        'blended_fair_value': blended_fair_value,
        'recommendation': recommendation,
        'upside_downside': upside_downside
    }

# ============================================================================
# SECTION 7: VISUALIZATIONS
# ============================================================================

def create_visualizations(data, dcf_results, comps_results, summary, sensitivity_df,
                         wacc_range, growth_range, sensitivity_matrix):
    """
    Create three key charts:
    1. FCF Bridge (waterfall chart)
    2. Sensitivity Heatmap
    3. Football Field Chart (valuation range)
    """
    fig = plt.figure(figsize=(16, 12))

    # -------------------------
    # Chart 1: FCF Bridge
    # -------------------------
    ax1 = plt.subplot(2, 2, 1)

    # Calculate components for waterfall
    fcf_components = dcf_results['fcf_df']
    years = fcf_components['Year'].values

    # Use FY2027 as example for FCF bridge
    ebit_val = fcf_components.iloc[0]['EBIT']
    nopat_val = fcf_components.iloc[0]['NOPAT']
    da_val = fcf_components.iloc[0]['D&A']
    capex_val = fcf_components.iloc[0]['Capex']
    nwc_val = fcf_components.iloc[0]['Δ NWC']
    fcf_val = fcf_components.iloc[0]['Unlevered FCF']

    # Waterfall data
    categories = ['EBIT', 'Less: Tax', 'NOPAT', 'Add: D&A', 'Less: Capex', 'Less: Δ NWC', 'FCF']
    values = [ebit_val, -(ebit_val - nopat_val), 0, da_val, capex_val, nwc_val, 0]
    cumulative = [ebit_val, nopat_val, nopat_val, nopat_val + da_val,
                  nopat_val + da_val + capex_val,
                  nopat_val + da_val + capex_val + nwc_val,
                  fcf_val]

    colors = ['#2E86AB', '#A23B72', '#2E86AB', '#06A77D', '#D62828', '#D62828', '#2E86AB']

    for i, (cat, val, cum) in enumerate(zip(categories, values, cumulative)):
        if i == 0 or i == 2 or i == 6:
            # Starting points
            ax1.bar(i, cum, color=colors[i], edgecolor='black', linewidth=1.5)
        else:
            # Connecting bars
            prev_cum = cumulative[i-1]
            if val > 0:
                ax1.bar(i, val, bottom=prev_cum, color=colors[i], edgecolor='black', linewidth=1.5)
            else:
                ax1.bar(i, abs(val), bottom=cum, color=colors[i], edgecolor='black', linewidth=1.5)

    ax1.set_xticks(range(len(categories)))
    ax1.set_xticklabels(categories, rotation=45, ha='right')
    ax1.set_ylabel('$ Millions', fontsize=11, fontweight='bold')
    ax1.set_title('FCF Bridge (FY2027)', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)

    # -------------------------
    # Chart 2: Sensitivity Heatmap
    # -------------------------
    ax2 = plt.subplot(2, 2, 2)

    # Create heatmap
    im = ax2.imshow(sensitivity_matrix, cmap='RdYlGn', aspect='auto')

    # Set ticks
    ax2.set_xticks(np.arange(len(wacc_range)))
    ax2.set_yticks(np.arange(len(growth_range)))
    ax2.set_xticklabels([f'{w:.1%}' for w in wacc_range], fontsize=9)
    ax2.set_yticklabels([f'{g:.1%}' for g in growth_range], fontsize=9)

    # Labels
    ax2.set_xlabel('WACC', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Terminal Growth Rate', fontsize=11, fontweight='bold')
    ax2.set_title('Sensitivity Analysis: Intrinsic Value per Share', fontsize=13, fontweight='bold')

    # Add values to cells
    for i in range(len(growth_range)):
        for j in range(len(wacc_range)):
            text = ax2.text(j, i, f'${sensitivity_matrix[i, j]:.0f}',
                          ha="center", va="center", color="black", fontsize=8, fontweight='bold')

    # Colorbar
    cbar = plt.colorbar(im, ax=ax2)
    cbar.set_label('Price per Share ($)', rotation=270, labelpad=20, fontweight='bold')

    # -------------------------
    # Chart 3: Football Field Chart
    # -------------------------
    ax3 = plt.subplot(2, 1, 2)

    # Valuation ranges
    methods = ['DCF\nIntrinsic Value', 'Comps\n(EV/Revenue)', 'Comps\n(EV/FCF)',
               'Blended\nFair Value', 'Current\nMarket Price']

    values = [
        dcf_results['intrinsic_value_per_share'],
        comps_results['price_from_revenue'],
        comps_results['price_from_fcf'],
        summary['blended_fair_value'],
        CURRENT_STOCK_PRICE
    ]

    colors_bar = ['#2E86AB', '#06A77D', '#06A77D', '#F77F00', '#D62828']

    # Create horizontal bars
    y_pos = np.arange(len(methods))
    bars = ax3.barh(y_pos, values, color=colors_bar, edgecolor='black', linewidth=1.5)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax3.text(val + 5, i, f'${val:.2f}', va='center', fontweight='bold', fontsize=10)

    # Add reference line at current price
    ax3.axvline(x=CURRENT_STOCK_PRICE, color='red', linestyle='--', linewidth=2, label=f'Current Price: ${CURRENT_STOCK_PRICE:.2f}')

    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(methods, fontsize=11, fontweight='bold')
    ax3.set_xlabel('Price per Share ($)', fontsize=12, fontweight='bold')
    ax3.set_title('Football Field Chart: Valuation Summary', fontsize=14, fontweight='bold')
    ax3.legend(loc='lower right', fontsize=10)
    ax3.grid(axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig('salesforce_valuation_charts.png', dpi=300, bbox_inches='tight')
    print("\n✓ Charts saved as 'salesforce_valuation_charts.png'")
    plt.show()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function - runs complete valuation analysis.
    """
    print("\n" + "="*70)
    print(" " * 15 + "SALESFORCE VALUATION ANALYSIS")
    print("="*70)

    # Load data from Excel
    file_path = '5 years data copy.xlsx'
    data = load_financial_data(file_path)

    # Perform DCF valuation
    dcf_results = dcf_valuation(data)

    # Sensitivity analysis
    sensitivity_df, wacc_range, growth_range, sensitivity_matrix = sensitivity_analysis(
        data, dcf_results['wacc'], PERPETUAL_GROWTH_RATE
    )

    # Trading comps valuation
    comps_results = comps_valuation(data)

    # Summary and recommendation
    summary = valuation_summary(dcf_results, comps_results)

    # Create visualizations
    create_visualizations(data, dcf_results, comps_results, summary, sensitivity_df,
                         wacc_range, growth_range, sensitivity_matrix)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nAll results have been printed above.")
    print("Charts saved to: salesforce_valuation_charts.png\n")

if __name__ == "__main__":
    main()
