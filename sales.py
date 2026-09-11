"""
Sales Management Module
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


def show_sales(data: dict):
    sales = data["sales"].copy()
    won   = sales[sales["status"] == "Closed Won"]

    st.markdown("# 🛒 Sales Management")
    st.markdown("*Track deals, analyse product performance, and understand sales trends.*")
    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────
    with st.expander("🔍 Filters", expanded=True):
        fc1, fc2, fc3, fc4 = st.columns(4)
        months    = sorted(sales["month"].unique())
        month_labels = [sales[sales["month"]==m]["month_label"].iloc[0] for m in months]

        all_months = st.session_state.get("sales_all_months", True)
        with fc1:
            selected_months = st.multiselect(
                "Month(s)", month_labels,
                default=month_labels[-6:],
                key="sales_months"
            )
        with fc2:
            selected_cats = st.multiselect(
                "Category", sales["category"].unique().tolist(),
                default=sales["category"].unique().tolist(),
                key="sales_cats"
            )
        with fc3:
            selected_reps = st.multiselect(
                "Sales Rep", sales["sales_rep"].unique().tolist(),
                default=sales["sales_rep"].unique().tolist(),
                key="sales_reps"
            )
        with fc4:
            selected_status = st.multiselect(
                "Status", sales["status"].unique().tolist(),
                default=["Closed Won"],
                key="sales_status"
            )

    # Apply filters
    month_map = {lbl: m for m, lbl in zip(months, month_labels)}
    sel_m = [month_map[l] for l in selected_months] if selected_months else months
    filt = sales[
        (sales["month"].isin(sel_m)) &
        (sales["category"].isin(selected_cats if selected_cats else sales["category"].unique())) &
        (sales["sales_rep"].isin(selected_reps if selected_reps else sales["sales_rep"].unique())) &
        (sales["status"].isin(selected_status if selected_status else sales["status"].unique()))
    ]

    # ── Summary KPIs ──────────────────────────────────────────────────
    st.markdown("### 📊 Sales Summary")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Revenue",     fmt_currency(filt["revenue"].sum()))
    k2.metric("Gross Profit",      fmt_currency(filt["gross_profit"].sum()))
    k3.metric("Avg GP Margin",     f"{filt['gp_margin'].mean():.1f}%")
    k4.metric("No. of Deals",      f"{len(filt):,}")
    k5.metric("Avg Deal Size",     fmt_currency(filt["revenue"].mean() if len(filt) else 0))

    st.markdown("---")

    # ── Charts Row 1 ─────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Monthly Revenue by Category")
        if len(filt):
            monthly_cat = (
                filt.groupby(["month_label","category"])["revenue"]
                .sum().reset_index()
            )
            ord_labels = [l for l in month_labels if l in monthly_cat["month_label"].values]
            fig = px.bar(monthly_cat, x="month_label", y="revenue", color="category",
                         category_orders={"month_label": ord_labels},
                         labels={"revenue": "Revenue (₹)", "month_label": "Month"},
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=330, margin=dict(l=5,r=5,t=10,b=5),
                               xaxis_tickangle=-30, yaxis_tickformat=",.0f",
                               legend=dict(orientation="h",y=1.12, font=dict(size=10)),
                               plot_bgcolor="#fafafa", paper_bgcolor="#fff")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected filters.")

    with col2:
        st.markdown("#### Sales Funnel by Status")
        funnel_data = sales[sales["month"].isin(sel_m)].groupby("status")["revenue"].sum().reset_index()
        if len(funnel_data):
            fig_f = px.funnel(funnel_data, x="revenue", y="status",
                              color_discrete_sequence=["#6366f1","#10b981","#f59e0b","#ef4444"])
            fig_f.update_layout(height=330, margin=dict(l=5,r=5,t=10,b=5))
            st.plotly_chart(fig_f, use_container_width=True)

    # ── Charts Row 2 ─────────────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### Top Products by Revenue")
        prod_rev = filt.groupby("product")["revenue"].sum().reset_index().sort_values("revenue", ascending=False).head(8)
        if len(prod_rev):
            fig_p = px.bar(prod_rev, x="revenue", y="product", orientation="h",
                           color="revenue", color_continuous_scale="Blues",
                           labels={"revenue": "Revenue (₹)", "product": ""})
            fig_p.update_layout(height=330, margin=dict(l=5,r=5,t=10,b=5),
                                 coloraxis_showscale=False, xaxis_tickformat=",.0f",
                                 plot_bgcolor="#fafafa", paper_bgcolor="#fff")
            st.plotly_chart(fig_p, use_container_width=True)

    with col4:
        st.markdown("#### Sales Rep Performance")
        rep_perf = filt.groupby("sales_rep").agg(
            revenue=("revenue","sum"),
            deals=("sale_id","count"),
            avg_margin=("gp_margin","mean")
        ).reset_index().sort_values("revenue", ascending=False)

        if len(rep_perf):
            fig_r = px.scatter(rep_perf, x="deals", y="revenue",
                               size="avg_margin", color="avg_margin",
                               text="sales_rep",
                               color_continuous_scale="Greens",
                               labels={"deals":"Number of Deals","revenue":"Revenue (₹)","avg_margin":"GP Margin %"})
            fig_r.update_traces(textposition="top center", textfont_size=10)
            fig_r.update_layout(height=330, margin=dict(l=5,r=5,t=10,b=5),
                                 yaxis_tickformat=",.0f",
                                 plot_bgcolor="#fafafa", paper_bgcolor="#fff")
            st.plotly_chart(fig_r, use_container_width=True)

    # ── Discount Impact ───────────────────────────────────────────────
    st.markdown("#### 📉 Discount Impact Analysis")
    dc1, dc2 = st.columns(2)
    with dc1:
        disc = filt.groupby("discount_pct").agg(
            revenue=("revenue","sum"),
            deals=("sale_id","count"),
            avg_margin=("gp_margin","mean")
        ).reset_index()
        fig_d = go.Figure()
        fig_d.add_bar(x=disc["discount_pct"].astype(str)+" %", y=disc["revenue"], name="Revenue",
                      marker_color="#6366f1")
        fig_d.add_trace(go.Scatter(x=disc["discount_pct"].astype(str)+" %", y=disc["avg_margin"],
                                    mode="lines+markers", name="Avg GP Margin %",
                                    yaxis="y2", line=dict(color="#f59e0b",width=2)))
        fig_d.update_layout(
            height=300, yaxis=dict(title="Revenue ₹", tickformat=",.0f"),
            yaxis2=dict(title="GP Margin %", overlaying="y", side="right"),
            legend=dict(orientation="h", y=1.12), hovermode="x unified",
            plot_bgcolor="#fafafa", paper_bgcolor="#fff",
            margin=dict(l=5,r=5,t=10,b=5)
        )
        st.plotly_chart(fig_d, use_container_width=True)

    with dc2:
        st.markdown("**Industry-wise Revenue Distribution**")
        ind_rev = filt.groupby("industry")["revenue"].sum().reset_index().sort_values("revenue", ascending=False)
        fig_i = px.pie(ind_rev, names="industry", values="revenue",
                       color_discrete_sequence=px.colors.qualitative.Pastel,
                       hole=0.4)
        fig_i.update_layout(height=300, margin=dict(l=5,r=5,t=5,b=5),
                             legend=dict(font=dict(size=10)))
        st.plotly_chart(fig_i, use_container_width=True)

    # ── Data Table ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Sales Transactions")
    show_cols = ["sale_id","date","product","category","customer_name","sales_rep",
                 "quantity","unit_price","discount_pct","revenue","gross_profit","gp_margin","status"]
    display = filt[show_cols].copy()
    display["date"] = display["date"].dt.strftime("%d %b %Y")
    display.columns = ["ID","Date","Product","Category","Customer","Rep","Qty",
                        "Unit Price","Disc%","Revenue","Gross Profit","GP%","Status"]

    # Style status
    def color_status(val):
        colors = {"Closed Won":"#d1fae5","Closed Lost":"#fee2e2","In Progress":"#fef3c7"}
        return f"background-color: {colors.get(val,'#f9fafb')}"

    st.dataframe(
        display.sort_values("Date", ascending=False).head(200),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Revenue":      st.column_config.NumberColumn(format="₹%.2f"),
            "Gross Profit": st.column_config.NumberColumn(format="₹%.2f"),
            "GP%":          st.column_config.NumberColumn(format="%.1f%%"),
            "Unit Price":   st.column_config.NumberColumn(format="₹%.2f"),
        }
    )
    if has_permission("can_export"):
        csv = display.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export to CSV", csv, "sales_data.csv", "text/csv")
