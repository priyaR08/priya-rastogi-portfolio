"""
Salesforce DCF Valuation Dashboard - Executive View
Clean, visual dashboard with all key metrics at a glance
Author: Priya Rastogi
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data_loader import SalesforceDataLoader


# Page configuration
st.set_page_config(
    page_title="Salesforce DCF Valuation | Priya Rastogi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Tableau-like styling
st.markdown("""
    <style>
    /* Main container */
    .main {
        background-color: #F8F9FA;
        padding: 1rem;
    }

    /* Compact header */
    .dashboard-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.2rem 2rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .dashboard-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
        display: inline-block;
    }

    .dashboard-author {
        color: #bfdbfe;
        font-size: 0.9rem;
        float: right;
        margin-top: 0.5rem;
    }

    /* KPI metric cards */
    .metric-card {
        background: white;
        padding: 1.3rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #3b82f6;
        height: 120px;
        transition: transform 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    .metric-icon {
        font-size: 2rem;
        float: right;
        opacity: 0.3;
    }

    .metric-label {
        font-size: 0.75rem;
        color: #374151 !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.4rem;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #000000 !important;
        line-height: 1.1;
        margin: 0.3rem 0;
    }

    .metric-change {
        font-size: 0.8rem;
        font-weight: 500;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        display: inline-block;
        margin-top: 0.3rem;
    }

    .positive-change {
        background: #d1fae5;
        color: #065f46;
    }

    .negative-change {
        background: #fee2e2;
        color: #991b1b;
    }

    .neutral-change {
        background: #e0e7ff;
        color: #3730a3;
    }

    /* Chart containers */
    .chart-box {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    .chart-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #000000 !important;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e5e7eb;
    }

    /* Section dividers */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, #3b82f6 0%, transparent 100%);
        margin: 1.5rem 0;
    }

    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Spacing adjustments */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


def load_data():
    """Load financial data from Excel model."""
    loader = SalesforceDataLoader()
    return loader


def render_compact_header():
    """Render compact dashboard header."""
    st.markdown("""
        <div class="dashboard-header">
            <div class="dashboard-title">📊 Salesforce DCF Valuation</div>
            <div class="dashboard-author">by Priya Rastogi</div>
            <div style="clear: both;"></div>
        </div>
    """, unsafe_allow_html=True)


def render_metric_cards(loader):
    """Render visual KPI metric cards."""
    kpis = loader.get_kpi_summary()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Card 1: FY2031 Revenue
    with col1:
        revenue_billions = kpis['fy2031_revenue'] / 1000
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">💰</div>
                <div class="metric-label">FY2031 Revenue</div>
                <div class="metric-value">${revenue_billions:.1f}B</div>
                <div class="metric-change neutral-change">Projected</div>
            </div>
        """, unsafe_allow_html=True)

    # Card 2: DCF Value
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #10b981;">
                <div class="metric-icon">🎯</div>
                <div class="metric-label">Intrinsic Value</div>
                <div class="metric-value">${kpis['intrinsic_value']:.0f}</div>
                <div class="metric-change neutral-change">Per Share</div>
            </div>
        """, unsafe_allow_html=True)

    # Card 3: Current Price
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #f59e0b;">
                <div class="metric-icon">💵</div>
                <div class="metric-label">Market Price</div>
                <div class="metric-value">${kpis['current_price']:.0f}</div>
                <div class="metric-change neutral-change">Current</div>
            </div>
        """, unsafe_allow_html=True)

    # Card 4: Revenue CAGR
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #059669;">
                <div class="metric-icon">📈</div>
                <div class="metric-label">Revenue CAGR</div>
                <div class="metric-value">{kpis['revenue_cagr']*100:.1f}%</div>
                <div class="metric-change positive-change">FY27-FY31</div>
            </div>
        """, unsafe_allow_html=True)

    # Card 5: Net Margin
    with col5:
        margin_pct = kpis['fy2031_margin'] * 100
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #8b5cf6;">
                <div class="metric-icon">📊</div>
                <div class="metric-label">Net Margin</div>
                <div class="metric-value">{margin_pct:.1f}%</div>
                <div class="metric-change positive-change">FY2031</div>
            </div>
        """, unsafe_allow_html=True)

    # Card 6: WACC
    with col6:
        wacc_pct = kpis['wacc'] * 100
        st.markdown(f"""
            <div class="metric-card" style="border-left-color: #ef4444;">
                <div class="metric-icon">🎲</div>
                <div class="metric-label">WACC</div>
                <div class="metric-value">{wacc_pct:.1f}%</div>
                <div class="metric-change neutral-change">Discount Rate</div>
            </div>
        """, unsafe_allow_html=True)


def render_assets_vs_liabilities(loader):
    """Render Current Assets vs Current Liabilities breakdown with tabs."""

    st.subheader("Balance Sheet Breakdown (FY2031)")

    # Create tabs
    tab1, tab2 = st.tabs(["Current Assets", "Current Liabilities"])

    with tab1:
        # Get assets breakdown
        assets_data = loader.get_assets_breakdown(year=2031)
        total_assets = assets_data['total']
        components = assets_data['components']

        # Display total in center
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem 0 1rem 0;">
                <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">Total Current Assets</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #10b981;">${total_assets/1000:.1f}B</div>
            </div>
        """, unsafe_allow_html=True)

        # Display breakdown
        for item in components:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                    <div style="padding: 0.8rem 0;">
                        <div style="font-size: 1rem; font-weight: 600; color: #3b82f6; margin-bottom: 0.2rem;">{item['name']}</div>
                        <div style="font-size: 0.9rem; color: #6b7280;">${item['amount']/1000:.2f}B</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-align: center; margin-top: 0.8rem;">
                        <div style="font-size: 1.1rem; font-weight: 600;">{item['pct']:.0f}%</div>
                    </div>
                """, unsafe_allow_html=True)

    with tab2:
        # Get liabilities breakdown
        liab_data = loader.get_liabilities_breakdown(year=2031)
        total_liabilities = liab_data['total']
        components = liab_data['components']

        # Display total in center
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem 0 1rem 0;">
                <div style="font-size: 0.9rem; color: #6b7280; margin-bottom: 0.5rem;">Total Current Liabilities</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #ef4444;">${total_liabilities/1000:.1f}B</div>
            </div>
        """, unsafe_allow_html=True)

        # Display breakdown
        for item in components:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                    <div style="padding: 0.8rem 0;">
                        <div style="font-size: 1rem; font-weight: 600; color: #3b82f6; margin-bottom: 0.2rem;">{item['name']}</div>
                        <div style="font-size: 0.9rem; color: #6b7280;">${item['amount']/1000:.2f}B</div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 6px; text-align: center; margin-top: 0.8rem;">
                        <div style="font-size: 1.1rem; font-weight: 600;">{item['pct']:.0f}%</div>
                    </div>
                """, unsafe_allow_html=True)


def render_revenue_and_margins(loader):
    """Render revenue growth and margins in side-by-side layout."""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue Growth (FY2027-2031)")

        revenue_data = loader.get_revenue_data()
        years = list(revenue_data.keys())
        revenues = [v/1000 for v in revenue_data.values()]  # Convert to billions

        fig = go.Figure()

        # Bar chart
        fig.add_trace(go.Bar(
            x=years,
            y=revenues,
            marker=dict(
                color=revenues,
                colorscale='Blues',
                showscale=False,
                line=dict(color='white', width=1.5)
            ),
            text=[f'${v:.1f}B' for v in revenues],
            textposition='outside',
            textfont=dict(size=12, weight='bold', color='#000000'),
            hovertemplate='<b>FY%{x}</b><br>Revenue: $%{y:.1f}B<extra></extra>'
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=10, b=40),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title='Fiscal Year',
                showgrid=False,
                tickfont=dict(size=11, color='#000000'),
                titlefont=dict(color='#000000')
            ),
            yaxis=dict(
                title='Revenue ($ Billions)',
                showgrid=True,
                gridcolor='#f3f4f6',
                tickfont=dict(size=11, color='#000000'),
                titlefont=dict(color='#000000')
            ),
            font=dict(family='Arial', size=11, color='#000000')
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Net Profit Margin (%)")

        margin_data = loader.get_margin_data()

        # Extract years and net margins
        years = margin_data['Year'].tolist()
        net_margins = margin_data['Net Income Margin'].tolist()

        # Convert to percentages (multiply by 100)
        net_margins_pct = [m * 100 if m is not None else 0 for m in net_margins]

        fig = go.Figure()

        # Net Margin Line Chart with markers
        fig.add_trace(go.Scatter(
            x=years,
            y=net_margins_pct,
            mode='lines+markers+text',
            line=dict(color='#8b5cf6', width=3),
            marker=dict(size=12, color='#8b5cf6', line=dict(color='white', width=2)),
            text=[f'{v:.1f}%' for v in net_margins_pct],
            textposition='top center',
            textfont=dict(size=12, weight='bold', color='#000000'),
            hovertemplate='<b>FY%{x}</b><br>Net Margin: %{y:.1f}%<extra></extra>'
        ))

        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=30, b=40),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                title='Fiscal Year',
                showgrid=False,
                tickfont=dict(size=11, color='#000000'),
                titlefont=dict(color='#000000')
            ),
            yaxis=dict(
                title='Net Profit Margin (%)',
                showgrid=True,
                gridcolor='#f3f4f6',
                tickfont=dict(size=11, color='#000000'),
                titlefont=dict(color='#000000'),
                range=[0, max(net_margins_pct) * 1.3]
            ),
            font=dict(family='Arial', size=11, color='#000000')
        )

        st.plotly_chart(fig, use_container_width=True)


def render_valuation_comparison(loader):
    """Render valuation comparison chart."""
    st.subheader("Valuation Summary: Multiple Methodologies")

    dcf_data = loader.get_dcf_valuation()
    comps_data = loader.get_comps_valuation_estimate()

    # Create valuation comparison
    methods = ['DCF<br>Intrinsic', 'EV/Revenue<br>Comps', 'EV/FCF<br>Comps', 'Current<br>Market']
    values = [
        dcf_data['intrinsic_value_per_share'],
        comps_data['value_per_share_revenue'],
        comps_data['value_per_share_fcf'],
        dcf_data['current_price']
    ]
    colors = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b']

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=methods,
        y=values,
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=[f'${v:.0f}' for v in values],
        textposition='outside',
        textfont=dict(size=14, weight='bold', color='#000000'),
        hovertemplate='<b>%{x}</b><br>Value: $%{y:.2f}/share<extra></extra>'
    ))

    # Add reference line at current price
    fig.add_hline(
        y=dcf_data['current_price'],
        line_dash="dash",
        line_color="#ef4444",
        annotation_text=f"Current Price: ${dcf_data['current_price']:.0f}",
        annotation_position="right"
    )

    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=20, b=40),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title='',
            showgrid=False,
            tickfont=dict(size=11, color='#000000')
        ),
        yaxis=dict(
            title='Value per Share ($)',
            showgrid=True,
            gridcolor='#f3f4f6',
            tickfont=dict(size=11, color='#000000'),
            titlefont=dict(color='#000000'),
            range=[0, max(values) * 1.2]
        ),
        font=dict(family='Arial', size=11, color='#000000'),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Add note
    st.caption("📌 Trading comps based on typical SaaS multiples (6.5x NTM Revenue, 25x FCF)")


def render_key_assumptions(loader):
    """Render key valuation assumptions in a compact format."""

    st.subheader("Key Valuation Assumptions")

    dcf_data = loader.get_dcf_valuation()
    kpis = loader.get_kpi_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #eff6ff; border-radius: 6px;">
                <div style="font-size: 0.75rem; color: #1e40af; font-weight: 600; margin-bottom: 0.3rem;">WACC</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1e3a8a;">{dcf_data['wacc']*100:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #f0fdf4; border-radius: 6px;">
                <div style="font-size: 0.75rem; color: #15803d; font-weight: 600; margin-bottom: 0.3rem;">REVENUE CAGR</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #166534;">{kpis['revenue_cagr']*100:.2f}%</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #faf5ff; border-radius: 6px;">
                <div style="font-size: 0.75rem; color: #7c3aed; font-weight: 600; margin-bottom: 0.3rem;">SHARES (M)</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #6b21a8;">{dcf_data['shares_outstanding']:.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem; background: #fef3c7; border-radius: 6px;">
                <div style="font-size: 0.75rem; color: #b45309; font-weight: 600; margin-bottom: 0.3rem;">NET DEBT ($M)</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #92400e;">{dcf_data['net_debt']:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # Load data
    loader = load_data()

    # Render dashboard sections
    render_compact_header()

    # Top metrics row
    render_metric_cards(loader)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Revenue and margins charts
    render_revenue_and_margins(loader)

    # Footer
    st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem 1rem 1rem; color: #9ca3af; font-size: 0.85rem;">
            <strong>Portfolio Project:</strong> 3-Statement Financial Model • DCF Valuation • SaaS Template<br>
            Full Excel model available on request | Built with Python (Pandas, Plotly, Streamlit)
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
