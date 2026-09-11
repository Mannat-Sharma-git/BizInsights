"""
Executive Dashboard Module
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from modules.auth import has_permission


def fmt_currency(val: float) -> str:
    if val >= 1_000_000:
        return f"₹{val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"₹{val/1_000:.1f}K"
    return f"₹{val:,.0f}"


def fmt_pct(val: float) -> str:
    return f"{val:+.1f}%" if val != 0 else "0.0%"


def show_dashboard(data: dict):
    kpis    = data["kpis"]
    sales   = data["sales"]
    expenses = data["expenses"]
    targets  = data["targets"]
    customers = data["customers"]

    won = sales[sales["status"] == "Closed Won"]

    st.markdown("# 📊 Executive Dashboard")
    st.markdown(f"*{data['company']} — Performance Overview as of June 2025*")
    st.markdown("---")

    # ── KPI Metric Cards ──────────────────────────────────────────────
    st.markdown("### 🎯 Key Business Metrics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Revenue (H1)",  fmt_currency(kpis["total_revenue"]),
              fmt_pct(kpis["revenue_growth"]))
    c2.metric("📈 Gross Profit",         fmt_currency(kpis["gross_profit"]),
              fmt_pct(kpis["gp_growth"]))
    c3.metric("💹 GP Margin",            f"{kpis['gp_margin']}%",
              f"Target: 55%")
    c4.metric("🔻 Total Expenses",       fmt_currency(kpis["total_expenses"]),
              fmt_pct(kpis["expense_growth"]), delta_color="inverse")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("🏆 Net Profit",           fmt_currency(kpis["net_profit"]),
              f"Margin: {kpis['net_profit_margin']}%")
    c6.metric("🤝 Active Customers",     str(kpis["active_customers"]),
              f"Total: {kpis['total_customers']}")
    c7.metric("🎯 Win Rate",             f"{kpis['win_rate']}%",
              f"Deals: {kpis['total_transactions']}")
    c8.metric("📦 Avg Deal Size",        fmt_currency(kpis["avg_deal_size"]),
              f"Target Ach: {kpis['latest_achievement']}%")

    st.markdown("---")

    # ── Revenue & GP Trend ────────────────────────────────────────────
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 📉 Monthly Revenue & Gross Profit Trend")
        monthly = (
            won.groupby("month_label")
            .agg(revenue=("revenue","sum"), gross_profit=("gross_profit","sum"))
            .reset_index()
        )
        # Maintain chronological order
        month_order = sorted(won["month"].unique())
        label_order = [won[won["month"]==m]["month_label"].iloc[0] for m in month_order]
        monthly["month_label"] = pd.Categorical(monthly["month_label"], categories=label_order, ordered=True)
        monthly = monthly.sort_values("month_label")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["month_label"], y=monthly["revenue"],
            name="Revenue", mode="lines+markers",
            line=dict(color="#3b82f6", width=2.5),
            fill="tonexty", fillcolor="rgba(59,130,246,0.08)"
        ))
        fig.add_trace(go.Scatter(
            x=monthly["month_label"], y=monthly["gross_profit"],
            name="Gross Profit", mode="lines+markers",
            line=dict(color="#10b981", width=2.5),
        ))
        fig.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.1),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            yaxis=dict(tickformat=",.0f"),
            hovermode="x unified",
            plot_bgcolor="#fafafa", paper_bgcolor="#ffffff",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### 🍩 Revenue by Category")
        cat_rev = won.groupby("category")["revenue"].sum().reset_index()
        fig_pie = px.pie(cat_rev, names="category", values="revenue",
                         color_discrete_sequence=px.colors.qualitative.Set2,
                         hole=0.42)
        fig_pie.update_layout(height=320, margin=dict(l=5, r=5, t=5, b=5),
                               legend=dict(font=dict(size=11)))
        fig_pie.update_traces(textinfo="percent+label", textfont_size=11)
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Expenses Breakdown & Target vs Actual ─────────────────────────
    col_l2, col_r2 = st.columns([2, 3])

    with col_l2:
        st.markdown("#### 💸 Expense Breakdown")
        approved_exp = expenses[expenses["status"] == "Approved"]
        exp_cat = approved_exp.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=True)
        fig_bar = px.bar(exp_cat, y="category", x="amount", orientation="h",
                         color="amount", color_continuous_scale="Reds",
                         labels={"amount": "Amount (₹)", "category": ""})
        fig_bar.update_layout(height=340, margin=dict(l=5, r=5, t=5, b=5),
                               coloraxis_showscale=False,
                               xaxis=dict(tickformat=",.0f"))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r2:
        st.markdown("#### 🎯 Revenue: Target vs Actual (Monthly)")
        tgt_last12 = targets.tail(12)
        fig_tv = go.Figure()
        fig_tv.add_trace(go.Bar(
            x=tgt_last12["month_label"], y=tgt_last12["rev_target"],
            name="Target", marker_color="rgba(99,102,241,0.5)"
        ))
        fig_tv.add_trace(go.Bar(
            x=tgt_last12["month_label"], y=tgt_last12["rev_actual"],
            name="Actual", marker_color="rgba(16,185,129,0.85)"
        ))
        fig_tv.update_layout(
            barmode="group", height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.12),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            yaxis=dict(tickformat=",.0f"),
            hovermode="x unified",
            plot_bgcolor="#fafafa", paper_bgcolor="#ffffff",
        )
        st.plotly_chart(fig_tv, use_container_width=True)

    st.markdown("---")

    # ── Customer & Employee ───────────────────────────────────────────
    col_c, col_e = st.columns(2)

    with col_c:
        st.markdown("#### 🏆 Top 8 Customers by Revenue")
        top_cust = (
            customers.sort_values("total_revenue", ascending=False)
            .head(8)[["name", "total_revenue", "segment", "industry", "health_score"]]
        )
        top_cust["total_revenue"] = top_cust["total_revenue"].apply(fmt_currency)
        top_cust.columns = ["Customer", "Revenue", "Segment", "Industry", "Health Score"]
        st.dataframe(top_cust, hide_index=True, use_container_width=True)

    with col_e:
        st.markdown("#### 👥 Sales by Representative")
        rep_sales = (
            won.groupby("sales_rep")["revenue"]
            .sum().reset_index()
            .sort_values("revenue", ascending=False)
        )
        fig_rep = px.bar(rep_sales, x="sales_rep", y="revenue",
                         color="revenue", color_continuous_scale="Blues",
                         labels={"sales_rep": "Sales Rep", "revenue": "Revenue (₹)"})
        fig_rep.update_layout(height=280, margin=dict(l=5, r=5, t=5, b=5),
                               coloraxis_showscale=False, xaxis_tickangle=-30,
                               plot_bgcolor="#fafafa", paper_bgcolor="#ffffff")
        st.plotly_chart(fig_rep, use_container_width=True)

    # ── Profitability Gauge ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🔄 Business Health Gauges")
    g1, g2, g3, g4 = st.columns(4)
    gauges = [
        (g1, "GP Margin",          kpis["gp_margin"],           55,  "%"),
        (g2, "Win Rate",           kpis["win_rate"],             65,  "%"),
        (g3, "Revenue Achievement",kpis["latest_achievement"],  100, "%"),
        (g4, "Net Profit Margin",  kpis["net_profit_margin"],    20,  "%"),
    ]
    for col, title, value, target, suffix in gauges:
        with col:
            color = "#10b981" if value >= target * 0.95 else ("#f59e0b" if value >= target * 0.80 else "#ef4444")
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                number={"suffix": suffix, "font": {"size": 22}},
                title={"text": title, "font": {"size": 13}},
                gauge={
                    "axis":       {"range": [0, max(target * 1.2, value * 1.1)]},
                    "bar":        {"color": color},
                    "threshold":  {"line": {"color": "#6366f1", "width": 2}, "value": target},
                    "steps": [
                        {"range": [0, target * 0.8],  "color": "rgba(239,68,68,0.12)"},
                        {"range": [target * 0.8, target],"color": "rgba(245,158,11,0.12)"},
                        {"range": [target, target * 1.2],"color": "rgba(16,185,129,0.12)"},
                    ],
                },
            ))
            fig_g.update_layout(height=200, margin=dict(l=10, r=10, t=30, b=10),
                                 paper_bgcolor="#ffffff")
            st.plotly_chart(fig_g, use_container_width=True)
