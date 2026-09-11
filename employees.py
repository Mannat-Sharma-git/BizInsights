"""
Employee Performance & KPI Tracking Module
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from modules.auth import has_permission


def show_employees(data: dict):
    emp_perf  = data["emp_perf"].copy()
    employees = data["employees"].copy()

    st.markdown("# 👥 Employee Performance & KPI Tracking")
    st.markdown("*Monitor workforce performance, track KPIs, and identify top contributors.*")
    st.markdown("---")

    # ── Filters ───────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns(3)
    quarters = sorted(emp_perf["quarter"].unique(), key=lambda x: (x.split()[1], x.split()[0]))
    with col_f1:
        sel_quarters = st.multiselect("Quarter(s)", quarters, default=quarters[-2:], key="emp_qtrs")
    with col_f2:
        dept_list = emp_perf["department"].unique().tolist()
        sel_depts = st.multiselect("Department(s)", dept_list, default=dept_list, key="emp_depts")
    with col_f3:
        emp_list = sorted(emp_perf["name"].unique().tolist())
        sel_emps = st.multiselect("Employee(s)", emp_list, default=emp_list, key="emp_names")

    filt = emp_perf[
        (emp_perf["quarter"].isin(sel_quarters if sel_quarters else quarters)) &
        (emp_perf["department"].isin(sel_depts if sel_depts else dept_list)) &
        (emp_perf["name"].isin(sel_emps if sel_emps else emp_list))
    ]

    # ── Summary KPIs ──────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Avg KPI Score",     f"{filt['kpi_score'].mean():.1f} / 100")
    k2.metric("Avg Rating",        f"{filt['rating'].mean():.2f} / 5.0")
    k3.metric("Avg Attendance",    f"{filt['attendance_pct'].mean():.1f}%")
    k4.metric("Task Completion",
              f"{(filt['tasks_complete'].sum()/filt['tasks_target'].sum()*100):.1f}%")
    k5.metric("Total Training Hrs", f"{filt['training_hrs'].sum():,}")

    st.markdown("---")

    # ── KPI Heatmap ───────────────────────────────────────────────────
    st.markdown("#### 🗓️ KPI Score Heatmap — Employee × Quarter")
    pivot = filt.pivot_table(index="name", columns="quarter", values="kpi_score", aggfunc="mean")

    if not pivot.empty:
        fig_hm = px.imshow(
            pivot,
            color_continuous_scale="RdYlGn",
            zmin=50, zmax=100,
            aspect="auto",
            labels=dict(x="Quarter", y="Employee", color="KPI Score"),
            text_auto=".1f",
        )
        fig_hm.update_layout(height=380, margin=dict(l=5,r=5,t=10,b=10),
                              coloraxis_showscale=True)
        st.plotly_chart(fig_hm, use_container_width=True)

    # ── Performance Charts ────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏆 Top Performers by KPI Score")
        top_perf = filt.groupby("name").agg(
            avg_kpi=("kpi_score","mean"),
            avg_rating=("rating","mean"),
            dept=("department","first"),
        ).reset_index().sort_values("avg_kpi", ascending=False).head(10)
        fig_tp = px.bar(top_perf, x="avg_kpi", y="name", orientation="h",
                        color="dept",
                        color_discrete_sequence=px.colors.qualitative.Set2,
                        labels={"avg_kpi":"Avg KPI Score","name":"","dept":"Dept"},
                        text=top_perf["avg_kpi"].round(1))
        fig_tp.update_traces(textposition="outside")
        fig_tp.update_layout(height=320, margin=dict(l=5,r=5,t=10,b=5),
                              xaxis_range=[0,105], showlegend=True,
                              legend=dict(orientation="h",y=1.12,font=dict(size=10)),
                              plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_tp, use_container_width=True)

    with col2:
        st.markdown("#### 📊 Department Average KPI")
        dept_kpi = filt.groupby("department").agg(
            avg_kpi=("kpi_score","mean"),
            avg_rating=("rating","mean"),
            count=("name","nunique"),
        ).reset_index()
        fig_dk = px.bar(dept_kpi, x="department", y="avg_kpi",
                        color="avg_rating",
                        color_continuous_scale="Blues",
                        text=dept_kpi["avg_kpi"].round(1),
                        labels={"avg_kpi":"Avg KPI Score","department":"Dept","avg_rating":"Avg Rating"})
        fig_dk.update_traces(textposition="outside")
        fig_dk.update_layout(height=320, margin=dict(l=5,r=5,t=10,b=5),
                              yaxis_range=[0,105],
                              plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_dk, use_container_width=True)

    # ── Sales Target vs Actual (Sales Dept only) ──────────────────────
    sales_emp = filt[filt["department"] == "Sales"]
    if not sales_emp.empty:
        st.markdown("#### 🎯 Sales Target vs Actual — Sales Team")
        sa = sales_emp.groupby(["name","quarter"]).agg(
            target=("sales_target","sum"),
            actual=("sales_revenue","sum")
        ).reset_index()
        sa["achievement"] = (sa["actual"] / sa["target"] * 100).clip(0, 150).round(1)

        fig_sa = px.bar(sa, x="quarter", y=["target","actual"],
                        facet_col="name", barmode="group",
                        color_discrete_map={"target":"rgba(99,102,241,0.5)","actual":"rgba(16,185,129,0.85)"},
                        labels={"value":"Revenue (₹)","variable":""},
                        facet_col_wrap=3)
        fig_sa.update_layout(height=340, margin=dict(l=5,r=5,t=30,b=5),
                              yaxis_tickformat=",.0f",
                              plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_sa, use_container_width=True)

    # ── Radar Chart ───────────────────────────────────────────────────
    st.markdown("#### 🕸️ Employee Multi-Dimensional Performance Radar")
    sel_emp_radar = st.selectbox("Select Employee", filt["name"].unique().tolist(), key="radar_emp")
    emp_data = filt[filt["name"] == sel_emp_radar]

    if not emp_data.empty:
        metrics = {
            "KPI Score":       emp_data["kpi_score"].mean() / 100 * 100,
            "Rating":          emp_data["rating"].mean() / 5 * 100,
            "Attendance":      emp_data["attendance_pct"].mean(),
            "Task Completion": (emp_data["tasks_complete"].sum() / emp_data["tasks_target"].sum() * 100),
            "Training":        min(emp_data["training_hrs"].sum() / 40 * 100, 100),
        }

        categories = list(metrics.keys())
        values     = list(metrics.values())
        values_closed = values + [values[0]]
        categories_closed = categories + [categories[0]]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed, theta=categories_closed,
            fill="toself", fillcolor="rgba(99,102,241,0.15)",
            line=dict(color="#6366f1", width=2.5),
            name=sel_emp_radar
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 105])),
            height=360, margin=dict(l=20,r=20,t=30,b=20),
            showlegend=False,
            paper_bgcolor="#fff",
        )
        col_r, col_t = st.columns([2, 1])
        with col_r:
            st.plotly_chart(fig_radar, use_container_width=True)
        with col_t:
            st.markdown(f"**{sel_emp_radar}**")
            for k, v in metrics.items():
                bar_color = "#10b981" if v >= 75 else ("#f59e0b" if v >= 50 else "#ef4444")
                st.markdown(
                    f"**{k}:** {v:.1f}%"
                    f"""<div style="background:#e5e7eb;border-radius:4px;height:8px;margin:2px 0 8px">
                    <div style="background:{bar_color};width:{min(v,100):.0f}%;height:100%;border-radius:4px"></div>
                    </div>""",
                    unsafe_allow_html=True
                )

    # ── Full Table ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Performance Records")
    show_cols = ["name","department","quarter","kpi_score","rating","attendance_pct",
                 "tasks_complete","tasks_target","training_hrs","leaves_taken"]
    display = filt[show_cols].copy()
    display.columns = ["Employee","Dept","Quarter","KPI Score","Rating","Attendance%",
                        "Tasks Done","Tasks Target","Training Hrs","Leaves"]
    st.dataframe(display.sort_values(["Quarter","KPI Score"], ascending=[False,False]),
                 hide_index=True, use_container_width=True,
                 column_config={
                     "KPI Score":   st.column_config.NumberColumn(format="%.1f"),
                     "Rating":      st.column_config.NumberColumn(format="%.1f ⭐"),
                     "Attendance%": st.column_config.NumberColumn(format="%.1f%%"),
                 })
    if has_permission("can_export"):
        csv = display.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export Performance Data", csv, "employee_performance.csv", "text/csv")
