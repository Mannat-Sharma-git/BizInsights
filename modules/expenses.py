"""
Expense & Profitability Analysis Module
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modules.auth import has_permission


def fmt_currency(val):
    if val >= 1_000_000:
        return f"₹{val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"₹{val/1_000:.1f}K"
    return f"₹{val:,.0f}"


def show_expenses(data: dict):
    expenses = data["expenses"].copy()
    sales    = data["sales"]
    targets  = data["targets"]
    won      = sales[sales["status"] == "Closed Won"]

    st.markdown("# 💸 Expense & Profitability Analysis")
    st.markdown("*Monitor costs, analyse profitability, and stay within budget.*")
    st.markdown("---")

    approved = expenses[expenses["status"] == "Approved"]

    # ── Summary KPIs ──────────────────────────────────────────────────
    total_exp   = approved["amount"].sum()
    total_rev   = won["revenue"].sum()
    total_gp    = won["gross_profit"].sum()
    net_profit  = total_rev - total_exp
    npm         = net_profit / total_rev * 100 if total_rev else 0
    gpm         = total_gp / total_rev * 100 if total_rev else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Expenses",    fmt_currency(total_exp))
    k2.metric("Total Revenue",     fmt_currency(total_rev))
    k3.metric("Gross Profit",      fmt_currency(total_gp), f"GP Margin: {gpm:.1f}%")
    k4.metric("Net Profit",        fmt_currency(net_profit))
    k5.metric("Net Profit Margin", f"{npm:.1f}%")

    st.markdown("---")

    # ── P&L Waterfall ─────────────────────────────────────────────────
    st.markdown("#### 📊 Profit & Loss Waterfall")
    # Build monthly P&L
    monthly_rev = won.groupby("month")["revenue"].sum()
    monthly_gp  = won.groupby("month")["gross_profit"].sum()
    monthly_exp = approved.groupby("month")["amount"].sum()

    pl_months = sorted(set(monthly_rev.index) | set(monthly_exp.index))
    pl_data = []
    for m in pl_months:
        rev = monthly_rev.get(m, 0)
        exp = monthly_exp.get(m, 0)
        gp  = monthly_gp.get(m, 0)
        pl_data.append({
            "month": m,
            "label": pd.to_datetime(m).strftime("%b %Y"),
            "revenue": rev,
            "cogs": rev - gp,
            "gross_profit": gp,
            "opex": exp,
            "net_profit": gp - exp,
        })
    pl_df = pd.DataFrame(pl_data)

    fig_wf = go.Figure()
    fig_wf.add_trace(go.Bar(name="Revenue",       x=pl_df["label"], y=pl_df["revenue"],      marker_color="#3b82f6"))
    fig_wf.add_trace(go.Bar(name="COGS",          x=pl_df["label"], y=-pl_df["cogs"],         marker_color="#f87171"))
    fig_wf.add_trace(go.Bar(name="Operating Exp", x=pl_df["label"], y=-pl_df["opex"],         marker_color="#fbbf24"))
    fig_wf.add_trace(go.Scatter(name="Net Profit", x=pl_df["label"], y=pl_df["net_profit"],
                                mode="lines+markers", line=dict(color="#10b981", width=2.5)))
    fig_wf.update_layout(
        barmode="relative", height=380,
        margin=dict(l=10,r=10,t=10,b=10),
        yaxis_tickformat=",.0f",
        legend=dict(orientation="h", y=1.12),
        xaxis_tickangle=-30,
        hovermode="x unified",
        plot_bgcolor="#fafafa", paper_bgcolor="#fff",
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    # ── Expense Category Breakdown ────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Expense by Category")
        cat_exp = approved.groupby("category")["amount"].sum().reset_index().sort_values("amount", ascending=False)
        cat_exp["pct"] = (cat_exp["amount"] / cat_exp["amount"].sum() * 100).round(1)
        fig_cat = px.bar(cat_exp, x="amount", y="category", orientation="h",
                         color="pct", color_continuous_scale="Oranges",
                         labels={"amount":"Total Amount (₹)","category":""},
                         hover_data={"pct": True})
        fig_cat.update_layout(height=340, margin=dict(l=5,r=5,t=10,b=5),
                               xaxis_tickformat=",.0f",
                               coloraxis_showscale=False,
                               plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_cat, use_container_width=True)

    with col2:
        st.markdown("#### 📈 Monthly Expense Trend")
        monthly_cat_exp = approved.groupby(["month","category"])["amount"].sum().reset_index()
        month_order = sorted(monthly_cat_exp["month"].unique())
        label_map   = {m: pd.to_datetime(m).strftime("%b %Y") for m in month_order}
        monthly_cat_exp["month_label"] = monthly_cat_exp["month"].map(label_map)
        ord_labels = [label_map[m] for m in month_order]

        # Top 5 categories only for readability
        top5_cats = cat_exp.head(5)["category"].tolist()
        monthly_top = monthly_cat_exp[monthly_cat_exp["category"].isin(top5_cats)]
        monthly_top["month_label"] = pd.Categorical(monthly_top["month_label"], categories=ord_labels, ordered=True)

        fig_trend = px.line(monthly_top.sort_values("month_label"),
                            x="month_label", y="amount", color="category",
                            markers=True,
                            color_discrete_sequence=px.colors.qualitative.Set1,
                            labels={"amount":"Amount (₹)","month_label":"Month","category":""})
        fig_trend.update_layout(height=340, margin=dict(l=5,r=5,t=10,b=5),
                                 xaxis_tickangle=-30, yaxis_tickformat=",.0f",
                                 legend=dict(font=dict(size=10)),
                                 plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_trend, use_container_width=True)

    # ── Budget vs Actual ──────────────────────────────────────────────
    st.markdown("#### 🎯 Budget Utilisation by Category")
    budget_data = approved.groupby("category").agg(
        actual=("amount","sum"),
        budget=("budget","mean")
    ).reset_index()
    budget_data["budget_total"] = budget_data["budget"] * 18  # 18 months
    budget_data["utilisation"]  = (budget_data["actual"] / budget_data["budget_total"] * 100).round(1)
    budget_data["variance"]     = budget_data["actual"] - budget_data["budget_total"]

    fig_bv = go.Figure()
    fig_bv.add_trace(go.Bar(name="Budget",  x=budget_data["category"], y=budget_data["budget_total"],
                             marker_color="rgba(99,102,241,0.45)"))
    fig_bv.add_trace(go.Bar(name="Actual",  x=budget_data["category"], y=budget_data["actual"],
                             marker_color="rgba(239,68,68,0.75)"))
    fig_bv.update_layout(
        barmode="group", height=320, margin=dict(l=5,r=5,t=10,b=10),
        yaxis_tickformat=",.0f", xaxis_tickangle=-20,
        legend=dict(orientation="h", y=1.12),
        hovermode="x unified",
        plot_bgcolor="#fafafa", paper_bgcolor="#fff",
    )
    st.plotly_chart(fig_bv, use_container_width=True)

    # ── Profitability by Product ──────────────────────────────────────
    st.markdown("#### 📦 Product Profitability")
    prod_profit = won.groupby("product").agg(
        revenue=("revenue","sum"),
        gp=("gross_profit","sum"),
        qty=("quantity","sum"),
        avg_margin=("gp_margin","mean")
    ).reset_index()
    prod_profit["margin_flag"] = prod_profit["avg_margin"].apply(
        lambda x: "High (>50%)" if x >= 50 else ("Mid (35-50%)" if x >= 35 else "Low (<35%)")
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_pp = px.scatter(prod_profit, x="revenue", y="avg_margin",
                            size="qty", color="margin_flag",
                            hover_name="product",
                            color_discrete_map={"High (>50%)":"#10b981","Mid (35-50%)":"#f59e0b","Low (<35%)":"#ef4444"},
                            labels={"revenue":"Revenue ₹","avg_margin":"Avg GP Margin %","qty":"Units Sold"})
        fig_pp.update_layout(height=300, margin=dict(l=5,r=5,t=10,b=5),
                              xaxis_tickformat=",.0f",
                              plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_pp, use_container_width=True)

    with col_p2:
        tbl = prod_profit[["product","revenue","gp","avg_margin","qty"]].copy()
        tbl.columns = ["Product","Revenue","Gross Profit","Avg Margin %","Units"]
        tbl = tbl.sort_values("Revenue", ascending=False)
        st.dataframe(tbl, hide_index=True, use_container_width=True,
                     column_config={
                         "Revenue":      st.column_config.NumberColumn(format="₹%.0f"),
                         "Gross Profit": st.column_config.NumberColumn(format="₹%.0f"),
                         "Avg Margin %": st.column_config.NumberColumn(format="%.1f%%"),
                     })

    # ── Expense Transactions ──────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Expense Transactions")
    months = sorted(expenses["month"].unique())
    sel_months = st.multiselect("Filter Months", months, default=months[-3:], key="exp_months")
    sel_cats   = st.multiselect("Filter Categories", expenses["category"].unique().tolist(),
                                 default=expenses["category"].unique().tolist(), key="exp_cats")

    exp_filt = expenses[
        (expenses["month"].isin(sel_months if sel_months else months)) &
        (expenses["category"].isin(sel_cats if sel_cats else expenses["category"].unique()))
    ]

    disp = exp_filt[["expense_id","date","category","amount","approved_by","status"]].copy()
    disp["date"] = disp["date"].dt.strftime("%d %b %Y")
    disp.columns = ["ID","Date","Category","Amount","Approved By","Status"]
    st.dataframe(disp.sort_values("Date", ascending=False).head(300),
                 hide_index=True, use_container_width=True,
                 column_config={
                     "Amount": st.column_config.NumberColumn(format="₹%.2f"),
                 })
    if has_permission("can_export"):
        csv = disp.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export Expenses", csv, "expenses.csv", "text/csv")
