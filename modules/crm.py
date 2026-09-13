"""
Customer Relationship Management Module
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


def show_crm(data: dict):
    customers = data["customers"].copy()
    sales     = data["sales"]
    won       = sales[sales["status"] == "Closed Won"]

    st.markdown("# 🤝 Customer Relationship Management")
    st.markdown("*360° view of your customers — engagement, value, and health.*")
    st.markdown("---")

    # ── Summary KPIs ──────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Customers",    str(len(customers)))
    k2.metric("Active Customers",   str(len(customers[customers["status"]=="Active"])))
    k3.metric("At-Risk Customers",  str(len(customers[customers["status"]=="At Risk"])))
    k4.metric("Total Customer Revenue", fmt_currency(customers["total_revenue"].sum()))
    k5.metric("Avg Health Score",   f"{customers['health_score'].mean():.1f} / 100")

    st.markdown("---")

    # ── Segment & Industry Charts ─────────────────────────────────────
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Customers by Segment")
        seg = customers.groupby("segment")["id"].count().reset_index()
        seg.columns = ["Segment","Count"]
        fig = px.pie(seg, names="Segment", values="Count",
                     color_discrete_sequence=px.colors.qualitative.Set2, hole=0.4)
        fig.update_layout(height=270, margin=dict(l=5,r=5,t=5,b=5))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Revenue by Segment")
        seg_rev = customers.groupby("segment")["total_revenue"].sum().reset_index()
        fig2 = px.bar(seg_rev, x="segment", y="total_revenue",
                      color="segment", color_discrete_sequence=px.colors.qualitative.Set1,
                      labels={"total_revenue":"Revenue (₹)","segment":"Segment"})
        fig2.update_layout(height=270, margin=dict(l=5,r=5,t=5,b=5),
                            showlegend=False, yaxis_tickformat=",.0f",
                            plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.markdown("#### Revenue by Industry")
        ind_rev = customers.groupby("industry")["total_revenue"].sum().reset_index().sort_values("total_revenue")
        fig3 = px.bar(ind_rev, y="industry", x="total_revenue", orientation="h",
                      color="total_revenue", color_continuous_scale="Teal",
                      labels={"total_revenue":"Revenue (₹)","industry":""})
        fig3.update_layout(height=270, margin=dict(l=5,r=5,t=5,b=5),
                            coloraxis_showscale=False, xaxis_tickformat=",.0f",
                            plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig3, use_container_width=True)

    # ── Customer Health Matrix ────────────────────────────────────────
    st.markdown("#### 🗺️ Customer Value vs Health Matrix")
    fig_m = px.scatter(
        customers,
        x="health_score", y="total_revenue",
        size="total_orders", color="segment",
        hover_name="name",
        hover_data={"industry": True, "city": True, "total_orders": True, "avg_order_value": True},
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={"health_score":"Health Score","total_revenue":"Total Revenue (₹)","total_orders":"Orders"},
        size_max=35,
    )
    fig_m.update_layout(height=380, margin=dict(l=5,r=5,t=10,b=5),
                         yaxis_tickformat=",.0f",
                         plot_bgcolor="#fafafa", paper_bgcolor="#fff")
    # Add quadrant lines
    mid_health = customers["health_score"].median()
    mid_rev    = customers["total_revenue"].median()
    fig_m.add_hline(y=mid_rev,    line_dash="dash", line_color="gray", opacity=0.5)
    fig_m.add_vline(x=mid_health, line_dash="dash", line_color="gray", opacity=0.5)
    st.plotly_chart(fig_m, use_container_width=True)

    # ── Purchase Frequency ────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 📅 Monthly New Customers Acquired")
        monthly_cust = won.groupby("month_label")["customer_id"].nunique().reset_index()
        month_order  = sorted(won["month"].unique())
        label_order  = [won[won["month"]==m]["month_label"].iloc[0] for m in month_order]
        monthly_cust["month_label"] = pd.Categorical(monthly_cust["month_label"],
                                                       categories=label_order, ordered=True)
        monthly_cust = monthly_cust.sort_values("month_label")
        fig_mc = px.line(monthly_cust, x="month_label", y="customer_id",
                          markers=True, line_shape="spline",
                          labels={"customer_id":"Active Customers","month_label":"Month"},
                          color_discrete_sequence=["#6366f1"])
        fig_mc.update_layout(height=280, margin=dict(l=5,r=5,t=5,b=5),
                              xaxis_tickangle=-30, plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_mc, use_container_width=True)

    with col_b:
        st.markdown("#### 🌆 Customers by City")
        city_count = customers.groupby("city")["id"].count().reset_index()
        city_count.columns = ["City","Count"]
        fig_city = px.bar(city_count.sort_values("Count"), y="City", x="Count",
                          orientation="h", color="Count",
                          color_continuous_scale="Purples",
                          labels={"Count":"No. of Customers","City":""})
        fig_city.update_layout(height=280, margin=dict(l=5,r=5,t=5,b=5),
                                coloraxis_showscale=False,
                                plot_bgcolor="#fafafa", paper_bgcolor="#fff")
        st.plotly_chart(fig_city, use_container_width=True)

    # ── Customer Profile Cards ────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 👤 Customer Profiles")
    search = st.text_input("🔍 Search customer by name or industry", "")
    status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive", "At Risk"])

    cust_disp = customers.copy()
    if search:
        cust_disp = cust_disp[
            cust_disp["name"].str.contains(search, case=False) |
            cust_disp["industry"].str.contains(search, case=False)
        ]
    if status_filter != "All":
        cust_disp = cust_disp[cust_disp["status"] == status_filter]

    for _, row in cust_disp.iterrows():
        status_emoji = {"Active":"🟢","Inactive":"🔴","At Risk":"🟡"}.get(row["status"],"⚪")
        with st.expander(f"{status_emoji} {row['name']} — {row['industry']} | {row['segment']}"):
            r1, r2, r3 = st.columns(3)
            r1.markdown(f"**📍 City:** {row['city']}")
            r1.markdown(f"**📞 Contact:** {row.get('contact','N/A')}")
            r1.markdown(f"**📧 Email:** {row.get('email','N/A')}")
            r2.markdown(f"**💰 Total Revenue:** {fmt_currency(row['total_revenue'])}")
            r2.markdown(f"**🛒 Total Orders:** {row['total_orders']}")
            r2.markdown(f"**📦 Avg Order Value:** {fmt_currency(row['avg_order_value'])}")
            r3.markdown(f"**💚 Health Score:** {row['health_score']:.1f} / 100")
            r3.markdown(f"**📊 Status:** {row['status']}")
            lp = row.get("last_purchase")
            r3.markdown(f"**📅 Last Purchase:** {lp.strftime('%d %b %Y') if pd.notna(lp) else 'N/A'}")

            # Health bar
            score = row["health_score"]
            color = "#10b981" if score >= 70 else ("#f59e0b" if score >= 45 else "#ef4444")
            st.markdown(
                f"""<div style="background:#e5e7eb;border-radius:4px;height:10px;margin:4px 0">
                <div style="background:{color};width:{score}%;height:100%;border-radius:4px"></div>
                </div>""",
                unsafe_allow_html=True
            )

    # ── Data Table ────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 Full Customer List")
    tbl = customers[["id","name","segment","industry","city","status",
                      "total_revenue","total_orders","avg_order_value","health_score"]].copy()
    tbl.columns = ["ID","Customer","Segment","Industry","City","Status",
                   "Revenue","Orders","Avg Order","Health"]
    st.dataframe(tbl.sort_values("Revenue", ascending=False),
                 hide_index=True, use_container_width=True,
                 column_config={
                     "Revenue":   st.column_config.NumberColumn(format="₹%.2f"),
                     "Avg Order": st.column_config.NumberColumn(format="₹%.2f"),
                     "Health":    st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100),
                 })
    if has_permission("can_export"):
        csv = tbl.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Export to CSV", csv, "customers.csv", "text/csv")
