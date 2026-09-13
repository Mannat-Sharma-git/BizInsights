"""
Business Target Management Module
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from modules.auth import has_permission


def fmt_currency(val):
    if val >= 1_000_000:
        return f"₹{val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"₹{val/1_000:.1f}K"
    return f"₹{val:,.0f}"


def achievement_badge(pct: float) -> str:
    if pct >= 100:
        return "🟢 Achieved"
    elif pct >= 85:
        return "🟡 Near Target"
    else:
        return "🔴 Below Target"


def show_targets(data: dict):
    targets  = data["targets"].copy()
    sales    = data["sales"]
    expenses = data["expenses"]

    won = sales[sales["status"] == "Closed Won"]

    st.markdown("# 🎯 Business Target Management")
    st.markdown("*Set, track, and analyse performance against business objectives.*")
    st.markdown("---")

    # ── Current Month Snapshot ────────────────────────────────────────
    latest = targets.iloc[-1]
    st.markdown(f"### 📍 Latest Period Snapshot — {latest['month_label']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Revenue Target",    fmt_currency(latest["rev_target"]),
              f"Actual: {fmt_currency(latest['rev_actual'])}")
    ach_delta = latest["rev_achievement"] - 100
    c2.metric("Achievement %",     f"{latest['rev_achievement']:.1f}%",
              f"{ach_delta:+.1f}% vs target",
              delta_color="normal" if ach_delta >= 0 else "inverse")
    c3.metric("Expense Limit",     fmt_currency(latest["exp_limit"]),
              f"Actual: {fmt_currency(latest['exp_actual'])}",
              delta_color="inverse")
    c4.metric("GP Margin Target",  f"{latest['gp_margin_target']}%",
              f"Actual: {latest['gp_margin_actual']}%",
              delta_color="normal" if latest["gp_margin_actual"] >= latest["gp_margin_target"] else "inverse")

    st.markdown("---")

    # ── Revenue Target vs Actual Timeline ────────────────────────────
    st.markdown("#### 📈 Revenue Target vs Actual — Full Timeline")
    fig_rv = go.Figure()
    fig_rv.add_trace(go.Scatter(
        x=targets["month_label"], y=targets["rev_target"],
        name="Target", mode="lines+markers",
        line=dict(color="#6366f1", width=2, dash="dash"),
        marker=dict(symbol="diamond", size=7)
    ))
    fig_rv.add_trace(go.Bar(
        x=targets["month_label"], y=targets["rev_actual"],
        name="Actual", marker_color=[
            "#10b981" if r >= 100 else ("#f59e0b" if r >= 85 else "#ef4444")
            for r in targets["rev_achievement"]
        ],
        opacity=0.8
    ))
    # Add achievement % annotations
    for _, row in targets.tail(6).iterrows():
        fig_rv.add_annotation(
            x=row["month_label"], y=row["rev_actual"],
            text=f"{row['rev_achievement']:.0f}%",
            showarrow=False, yshift=14,
            font=dict(size=9, color="#374151")
        )
    fig_rv.update_layout(
        height=380, margin=dict(l=10,r=10,t=10,b=10),
        yaxis_tickformat=",.0f",
        xaxis_tickangle=-30,
        legend=dict(orientation="h", y=1.1),
        hovermode="x unified",
        plot_bgcolor="#fafafa", paper_bgcolor="#fff",
    )
    st.plotly_chart(fig_rv, use_container_width=True)

    # ── GP Margin Target vs Actual ─────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 GP Margin: Target vs Actual")
        fig_gp = go.Figure()
        fig_gp.add_trace(go.Scatter(
            x=targets["month_label"], y=targets["gp_margin_target"],
            name="Target %", mode="lines",
            line=dict(color="#6366f1", width=2, dash="dot")
        ))
        fig_gp.add_trace(go.Scatter(
            x=targets["month_label"], y=targets["gp_margin_actual"],
            name="Actual %", mode="lines+markers",
            line=dict(color="#10b981", width=2.5),
            fill="tonexty", fillcolor="rgba(16,185,129,0.08)"
        ))
        fig_gp.update_layout(
            height=300, margin=dict(l=5,r=5,t=10,b=5),
            yaxis_title="GP Margin %",
            xaxis_tickangle=-30,
            legend=dict(orientation="h",y=1.12),
            hovermode="x unified",
            plot_bgcolor="#fafafa", paper_bgcolor="#fff",
        )
        st.plotly_chart(fig_gp, use_container_width=True)

    with col2:
        st.markdown("#### 💸 Expense: Budget vs Actual")
        fig_exp = go.Figure()
        fig_exp.add_trace(go.Bar(
            x=targets["month_label"], y=targets["exp_limit"],
            name="Budget", marker_color="rgba(99,102,241,0.4)"
        ))
        fig_exp.add_trace(go.Bar(
            x=targets["month_label"], y=targets["exp_actual"],
            name="Actual", marker_color=[
                "#10b981" if v <= 0 else "#ef4444"
                for v in targets["exp_variance"]
            ],
            opacity=0.8
        ))
        fig_exp.update_layout(
            barmode="group", height=300,
            margin=dict(l=5,r=5,t=10,b=5),
            yaxis_tickformat=",.0f", xaxis_tickangle=-30,
            legend=dict(orientation="h",y=1.12),
            hovermode="x unified",
            plot_bgcolor="#fafafa", paper_bgcolor="#fff",
        )
        st.plotly_chart(fig_exp, use_container_width=True)

    # ── Customer Acquisition ──────────────────────────────────────────
    st.markdown("#### 👥 Customer Acquisition: Target vs Actual")
    fig_ca = go.Figure()
    fig_ca.add_trace(go.Bar(
        x=targets["month_label"], y=targets["new_cust_target"],
        name="Target Customers", marker_color="rgba(245,158,11,0.5)"
    ))
    fig_ca.add_trace(go.Bar(
        x=targets["month_label"], y=targets["new_cust_actual"],
        name="Actual Customers", marker_color="rgba(16,185,129,0.85)"
    ))
    fig_ca.update_layout(
        barmode="group", height=280,
        margin=dict(l=5,r=5,t=10,b=5),
        legend=dict(orientation="h",y=1.12),
        xaxis_tickangle=-30,
        hovermode="x unified",
        plot_bgcolor="#fafafa", paper_bgcolor="#fff",
    )
    st.plotly_chart(fig_ca, use_container_width=True)

    # ── Achievement Table ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Monthly Targets & Achievement Summary")
    tbl = targets.copy()
    tbl["status"] = tbl["rev_achievement"].apply(achievement_badge)

    display_cols = ["month_label","rev_target","rev_actual","rev_achievement",
                    "exp_limit","exp_actual","exp_variance",
                    "new_cust_target","new_cust_actual",
                    "gp_margin_target","gp_margin_actual","status"]
    tbl = tbl[display_cols].copy()
    tbl.columns = ["Month","Rev Target","Rev Actual","Achievement %",
                   "Exp Budget","Exp Actual","Exp Variance",
                   "Cust Target","Cust Actual",
                   "GP% Target","GP% Actual","Status"]

    st.dataframe(
        tbl.sort_values("Month", ascending=False),
        hide_index=True, use_container_width=True,
        column_config={
            "Rev Target":    st.column_config.NumberColumn(format="₹%.0f"),
            "Rev Actual":    st.column_config.NumberColumn(format="₹%.0f"),
            "Achievement %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=150),
            "Exp Budget":    st.column_config.NumberColumn(format="₹%.0f"),
            "Exp Actual":    st.column_config.NumberColumn(format="₹%.0f"),
            "Exp Variance":  st.column_config.NumberColumn(format="₹%.0f"),
        }
    )
    if has_permission("can_export"):
        csv = tbl.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export Targets Data", csv, "targets.csv", "text/csv")

    # ── Annual Summary ────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📅 Annual Target Achievement Summary")
    targets["year"] = targets["month"].str[:4]
    annual = targets.groupby("year").agg(
        total_target=("rev_target","sum"),
        total_actual=("rev_actual","sum"),
        avg_achievement=("rev_achievement","mean"),
        avg_gp_target=("gp_margin_target","mean"),
        avg_gp_actual=("gp_margin_actual","mean"),
    ).reset_index()
    annual["gap"] = annual["total_target"] - annual["total_actual"]

    a1, a2 = st.columns(2)
    for i, row in annual.iterrows():
        col = a1 if i == 0 else a2
        with col:
            year_color = "#10b981" if row["avg_achievement"] >= 95 else "#f59e0b"
            st.markdown(f"**{row['year']} Performance**")
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Revenue", fmt_currency(row["total_actual"]),
                       f"Target: {fmt_currency(row['total_target'])}")
            m2.metric("Achievement",  f"{row['avg_achievement']:.1f}%")
            m3.metric("Revenue Gap",  fmt_currency(abs(row["gap"])),
                       "Surplus" if row["gap"] <= 0 else "Shortfall",
                       delta_color="normal" if row["gap"] <= 0 else "inverse")
