"""
Reports & Analytics Module
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


def show_reports(data: dict):
    sales     = data["sales"]
    expenses  = data["expenses"]
    customers = data["customers"]
    emp_perf  = data["emp_perf"]
    targets   = data["targets"]

    won = sales[sales["status"] == "Closed Won"]

    st.markdown("# 📑 Reports & Analytics")
    st.markdown("*Comprehensive business intelligence reports across all domains.*")
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary",
        "🛒 Sales Analytics",
        "💸 Financial Report",
        "👥 HR Analytics",
        "📈 Trend Analysis",
    ])

    # ─────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 📊 Executive Summary Report")

        # YTD figures
        won_2025 = won[won["month"].str.startswith("2025")]
        won_2024 = won[won["month"].str.startswith("2024")]
        exp_2025 = expenses[(expenses["month"].str.startswith("2025")) & (expenses["status"]=="Approved")]
        exp_2024 = expenses[(expenses["month"].str.startswith("2024")) & (expenses["status"]=="Approved")]

        kpis_2025 = {
            "revenue":    won_2025["revenue"].sum(),
            "gp":         won_2025["gross_profit"].sum(),
            "expenses":   exp_2025["amount"].sum(),
            "deals":      len(won_2025),
            "customers":  won_2025["customer_id"].nunique(),
        }
        kpis_2024 = {
            "revenue":    won_2024["revenue"].sum(),
            "gp":         won_2024["gross_profit"].sum(),
            "expenses":   exp_2024["amount"].sum(),
            "deals":      len(won_2024),
            "customers":  won_2024["customer_id"].nunique(),
        }

        col_y, col_p = st.columns(2)
        for col, yr, kpi in [(col_y,"2025 (H1)",kpis_2025),(col_p,"2024 (Full Year)",kpis_2024)]:
            with col:
                st.markdown(f"**{yr}**")
                m1,m2,m3 = st.columns(3)
                m1.metric("Revenue",   fmt_currency(kpi["revenue"]))
                m2.metric("Gross P.",  fmt_currency(kpi["gp"]))
                m3.metric("Expenses",  fmt_currency(kpi["expenses"]))
                m4,m5,m6 = st.columns(3)
                m4.metric("Net P.",    fmt_currency(kpi["gp"]-kpi["expenses"]))
                m5.metric("Deals",     str(kpi["deals"]))
                m6.metric("Customers", str(kpi["customers"]))

        st.markdown("---")
        st.markdown("#### Quarter-over-Quarter Summary")
        quarterly_rev = won.copy()
        quarterly_rev["quarter"] = pd.PeriodIndex(quarterly_rev["date"], freq="Q").astype(str)
        qtr_summary = quarterly_rev.groupby("quarter").agg(
            revenue=("revenue","sum"),
            deals=("sale_id","count"),
            avg_deal=("revenue","mean"),
            gp=("gross_profit","sum"),
        ).reset_index()
        qtr_summary["gp_margin"] = (qtr_summary["gp"]/qtr_summary["revenue"]*100).round(1)

        fig_q = px.bar(qtr_summary, x="quarter", y="revenue",
                       color="gp_margin", color_continuous_scale="Greens",
                       text=qtr_summary["revenue"].apply(fmt_currency),
                       labels={"revenue":"Revenue","quarter":"Quarter","gp_margin":"GP Margin %"})
        fig_q.update_traces(textposition="outside")
        fig_q.update_layout(height=320, margin=dict(l=5,r=5,t=10,b=5),
                             yaxis_tickformat=",.0f",
                             plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_q, use_container_width=True)

        # Summary table
        qtr_display = qtr_summary.copy()
        qtr_display["revenue"] = qtr_display["revenue"].apply(fmt_currency)
        qtr_display["avg_deal"] = qtr_display["avg_deal"].apply(fmt_currency)
        qtr_display["gp"] = qtr_display["gp"].apply(fmt_currency)
        qtr_display.columns = ["Quarter","Revenue","Deals","Avg Deal","Gross Profit","GP Margin %"]
        st.dataframe(qtr_display, hide_index=True, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 🛒 Sales Analytics Report")

        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### Product Mix Analysis")
            prod_rev = won.groupby("product").agg(
                revenue=("revenue","sum"),
                gp=("gross_profit","sum"),
                qty=("quantity","sum")
            ).reset_index()
            prod_rev["gp_margin"] = (prod_rev["gp"]/prod_rev["revenue"]*100).round(1)
            prod_rev["rev_share"] = (prod_rev["revenue"]/prod_rev["revenue"].sum()*100).round(1)
            fig_pm = px.treemap(prod_rev, path=["product"], values="revenue",
                                color="gp_margin", color_continuous_scale="RdYlGn",
                                hover_data={"rev_share":True,"qty":True,"gp_margin":True})
            fig_pm.update_layout(height=360, margin=dict(l=5,r=5,t=10,b=5))
            st.plotly_chart(fig_pm, use_container_width=True)

        with col_s2:
            st.markdown("#### Sales Velocity (Rolling 3M)")
            monthly_deals = won.groupby("month").agg(
                revenue=("revenue","sum"),
                deals=("sale_id","count"),
            ).reset_index().sort_values("month")
            monthly_deals["rolling_rev"] = monthly_deals["revenue"].rolling(3).mean()
            monthly_deals["rolling_deals"] = monthly_deals["deals"].rolling(3).mean()
            monthly_deals["label"] = monthly_deals["month"].apply(
                lambda m: pd.to_datetime(m).strftime("%b %Y")
            )
            fig_vel = go.Figure()
            fig_vel.add_trace(go.Bar(x=monthly_deals["label"], y=monthly_deals["revenue"],
                                      name="Monthly Revenue", marker_color="rgba(99,102,241,0.4)"))
            fig_vel.add_trace(go.Scatter(x=monthly_deals["label"], y=monthly_deals["rolling_rev"],
                                          name="3M Rolling Avg", mode="lines",
                                          line=dict(color="#ef4444",width=2.5,dash="dash")))
            fig_vel.update_layout(height=360, margin=dict(l=5,r=5,t=10,b=5),
                                   yaxis_tickformat=",.0f", xaxis_tickangle=-30,
                                   legend=dict(orientation="h",y=1.12),
                                   hovermode="x unified",
                                   plot_bgcolor="#fafafa", paper_bgcolor="#fff")
            st.plotly_chart(fig_vel, use_container_width=True)

        st.markdown("#### Segment-wise Sales Deep Dive")
        seg_deep = won.groupby(["segment","category"]).agg(
            revenue=("revenue","sum"),
            deals=("sale_id","count"),
            avg_gp=("gp_margin","mean")
        ).reset_index()
        fig_sd = px.sunburst(seg_deep, path=["segment","category"], values="revenue",
                              color="avg_gp", color_continuous_scale="Viridis",
                              labels={"revenue":"Revenue","avg_gp":"Avg GP%"})
        fig_sd.update_layout(height=420, margin=dict(l=5,r=5,t=10,b=5))
        st.plotly_chart(fig_sd, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 💸 Financial Report")
        approved = expenses[expenses["status"]=="Approved"]

        st.markdown("#### Monthly P&L Statement")
        months = sorted(won["month"].unique())
        pl_rows = []
        for m in months:
            rev  = won[won["month"]==m]["revenue"].sum()
            cogs = won[won["month"]==m]["cogs"].sum()
            gp   = won[won["month"]==m]["gross_profit"].sum()
            opex = approved[approved["month"]==m]["amount"].sum()
            ebit = gp - opex
            lbl  = pd.to_datetime(m).strftime("%b %Y")
            pl_rows.append({
                "Month": lbl, "Revenue": rev, "COGS": cogs,
                "Gross Profit": gp, "GP Margin": f"{gp/rev*100:.1f}%" if rev else "0%",
                "Operating Exp": opex, "EBIT": ebit,
                "EBIT Margin": f"{ebit/rev*100:.1f}%" if rev else "0%"
            })
        pl_df = pd.DataFrame(pl_rows)
        st.dataframe(
            pl_df.sort_values("Month", ascending=False),
            hide_index=True, use_container_width=True,
            column_config={
                "Revenue":      st.column_config.NumberColumn(format="₹%.0f"),
                "COGS":         st.column_config.NumberColumn(format="₹%.0f"),
                "Gross Profit": st.column_config.NumberColumn(format="₹%.0f"),
                "Operating Exp":st.column_config.NumberColumn(format="₹%.0f"),
                "EBIT":         st.column_config.NumberColumn(format="₹%.0f"),
            }
        )

        st.markdown("#### Expense Approval Status")
        status_exp = expenses.groupby("status")["amount"].sum().reset_index()
        fig_es = px.pie(status_exp, names="status", values="amount",
                        color_discrete_map={"Approved":"#10b981","Pending":"#f59e0b","Rejected":"#ef4444"},
                        hole=0.4)
        fig_es.update_layout(height=280, margin=dict(l=5,r=5,t=5,b=5))
        st.plotly_chart(fig_es, use_container_width=True)

        if has_permission("can_export"):
            csv = pl_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export P&L Report", csv, "pl_report.csv", "text/csv")

    # ─────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown("### 👥 HR Analytics Report")

        col_hr1, col_hr2 = st.columns(2)
        with col_hr1:
            st.markdown("#### Department Headcount")
            dept_hc = data["employees"].groupby("dept")["id"].count().reset_index()
            fig_hc = px.pie(dept_hc, names="dept", values="id",
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            hole=0.4, labels={"id":"Headcount","dept":"Dept"})
            fig_hc.update_layout(height=280, margin=dict(l=5,r=5,t=5,b=5))
            st.plotly_chart(fig_hc, use_container_width=True)

        with col_hr2:
            if has_permission("can_view_salary"):
                st.markdown("#### Salary Distribution by Department")
                sal_dist = data["employees"].groupby("dept")["salary"].agg(["sum","mean"]).reset_index()
                sal_dist.columns = ["Dept","Total Salary","Avg Salary"]
                fig_sal = px.bar(sal_dist, x="Dept", y="Total Salary",
                                  color="Avg Salary", color_continuous_scale="Blues",
                                  labels={"Total Salary":"Total Monthly Salary ₹"})
                fig_sal.update_layout(height=280, margin=dict(l=5,r=5,t=5,b=5),
                                       yaxis_tickformat=",.0f",
                                       plot_bgcolor="#fafafa", paper_bgcolor="#fff")
                st.plotly_chart(fig_sal, use_container_width=True)
            else:
                st.info("🔒 Salary data requires Manager or Administrator role.")

        st.markdown("#### KPI Trend by Quarter")
        kpi_trend = emp_perf.groupby(["quarter","department"])["kpi_score"].mean().reset_index()
        fig_kt = px.line(kpi_trend, x="quarter", y="kpi_score", color="department",
                          markers=True,
                          labels={"kpi_score":"Avg KPI Score","quarter":"Quarter"},
                          color_discrete_sequence=px.colors.qualitative.Set2)
        fig_kt.update_layout(height=320, margin=dict(l=5,r=5,t=10,b=5),
                              yaxis_range=[50,100],
                              legend=dict(orientation="h",y=1.12),
                              plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_kt, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────
    with tab5:
        st.markdown("### 📈 Trend Analysis")

        st.markdown("#### Revenue Growth Rate (MoM %)")
        monthly_rev = won.groupby("month")["revenue"].sum().reset_index().sort_values("month")
        monthly_rev["mom_growth"] = monthly_rev["revenue"].pct_change() * 100
        monthly_rev["label"]      = monthly_rev["month"].apply(lambda m: pd.to_datetime(m).strftime("%b %Y"))
        monthly_rev["color_flag"] = monthly_rev["mom_growth"].apply(lambda x: "positive" if x >= 0 else "negative")

        fig_mom = px.bar(monthly_rev.dropna(), x="label", y="mom_growth",
                          color="color_flag",
                          color_discrete_map={"positive":"#10b981","negative":"#ef4444"},
                          labels={"mom_growth":"MoM Growth %","label":"Month"},
                          text=monthly_rev.dropna()["mom_growth"].round(1))
        fig_mom.update_traces(textposition="outside")
        fig_mom.update_layout(height=340, margin=dict(l=5,r=5,t=10,b=5),
                               showlegend=False, xaxis_tickangle=-30,
                               yaxis_title="Growth %",
                               plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        fig_mom.add_hline(y=0, line_color="#374151", line_width=1)
        st.plotly_chart(fig_mom, use_container_width=True)

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### Customer Acquisition Trend")
            cust_trend = won.groupby("month")["customer_id"].nunique().reset_index()
            cust_trend["label"] = cust_trend["month"].apply(lambda m: pd.to_datetime(m).strftime("%b %Y"))
            cust_trend["rolling3"] = cust_trend["customer_id"].rolling(3).mean()
            fig_ct = go.Figure()
            fig_ct.add_trace(go.Bar(x=cust_trend["label"], y=cust_trend["customer_id"],
                                     name="Monthly", marker_color="rgba(99,102,241,0.45)"))
            fig_ct.add_trace(go.Scatter(x=cust_trend["label"], y=cust_trend["rolling3"],
                                         name="3M Avg", mode="lines",
                                         line=dict(color="#f59e0b",width=2,dash="dash")))
            fig_ct.update_layout(height=300, margin=dict(l=5,r=5,t=10,b=5),
                                  xaxis_tickangle=-30, legend=dict(orientation="h",y=1.12),
                                  plot_bgcolor="#fafafa", paper_bgcolor="#fff")
            st.plotly_chart(fig_ct, use_container_width=True)

        with col_t2:
            st.markdown("#### Win Rate Trend")
            monthly_wr = sales.groupby("month").apply(
                lambda x: pd.Series({
                    "win_rate": (x["status"]=="Closed Won").sum() / len(x) * 100
                })
            ).reset_index()
            monthly_wr["label"] = monthly_wr["month"].apply(lambda m: pd.to_datetime(m).strftime("%b %Y"))
            fig_wr = px.area(monthly_wr, x="label", y="win_rate",
                              line_shape="spline",
                              color_discrete_sequence=["#10b981"],
                              labels={"win_rate":"Win Rate %","label":"Month"})
            fig_wr.update_layout(height=300, margin=dict(l=5,r=5,t=10,b=5),
                                  xaxis_tickangle=-30,
                                  yaxis_range=[0,100],
                                  plot_bgcolor="#fafafa", paper_bgcolor="#fff")
            st.plotly_chart(fig_wr, use_container_width=True)
