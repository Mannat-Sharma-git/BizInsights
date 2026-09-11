"""
SME Business Performance & Decision Intelligence System
Main Application Entry Point
"""

import streamlit as st
import pandas as pd

# ── Page Configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NovaTech | Business Intelligence",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "SME Business Performance & Decision Intelligence System\nPowered by Streamlit & Google Gemini 2.5 Flash",
    }
)

# ── Module Imports ─────────────────────────────────────────────────────────────
from modules.auth        import require_auth, logout, get_current_user, has_access
from modules.data_engine import load_all_data
from modules.dashboard   import show_dashboard
from modules.sales       import show_sales
from modules.crm         import show_crm
from modules.expenses    import show_expenses
from modules.employees   import show_employees
from modules.targets     import show_targets
from modules.reports     import show_reports
from modules.ai_insights import show_ai_insights


# ── Custom Styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Sidebar header */
[data-testid="stSidebarNav"] { display: none; }
.sidebar-logo {
    font-size: 1.3rem;
    font-weight: 700;
    color: #1e3a5f;
    padding: 0.5rem 0 0.25rem;
    border-bottom: 2px solid #e5e7eb;
    margin-bottom: 0.5rem;
}
/* Metric delta colours */
[data-testid="stMetricDelta"] { font-size: 0.85rem; }
/* DataFrame enhancements */
[data-testid="stDataFrame"] { border-radius: 8px; }
/* Expander styling */
.streamlit-expanderHeader { font-weight: 600; }
/* General padding */
.block-container { padding-top: 1rem; padding-bottom: 1rem; }
/* Hide Streamlit footer */
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Authentication Gate ────────────────────────────────────────────────────────
require_auth()

# ── Data Loading (cached) ──────────────────────────────────────────────────────
@st.cache_data(show_spinner="⚙️ Loading business data...", ttl=3600)
def get_data():
    return load_all_data()


data = get_data()
user = get_current_user()

# ── Navigation Items ───────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("dashboard",   "📊 Dashboard",         "Executive Overview"),
    ("sales",       "🛒 Sales",              "Sales Management"),
    ("crm",         "🤝 CRM",               "Customer Relations"),
    ("expenses",    "💸 Expenses",           "Cost & Profitability"),
    ("employees",   "👥 Employees",          "Performance & KPIs"),
    ("targets",     "🎯 Targets",            "Business Targets"),
    ("reports",     "📑 Reports",            "Analytics & Reports"),
    ("ai_insights", "🤖 AI Insights",        "AI Business Intelligence"),
]

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">🏢 NovaTech Solutions</div>
    <div style="font-size:0.78rem;color:#6b7280;margin-bottom:0.75rem">Business Intelligence Platform</div>
    """, unsafe_allow_html=True)

    # User info
    role_colors = {"Administrator": "#ef4444", "Manager": "#f59e0b", "Employee": "#10b981"}
    role_color  = role_colors.get(user["role"], "#6b7280")
    st.markdown(f"""
    <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;margin-bottom:12px">
        <div style="font-weight:600;font-size:0.95rem">{user['avatar']} {user['name']}</div>
        <div style="font-size:0.78rem;color:{role_color};font-weight:600;margin-top:2px">{user['role']}</div>
        <div style="font-size:0.73rem;color:#9ca3af;margin-top:2px">{user['email']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown("**Navigation**")
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"

    for page_id, label, description in NAV_ITEMS:
        if not has_access(page_id):
            continue
        is_active = st.session_state["current_page"] == page_id
        btn_type  = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{page_id}", use_container_width=True, type=btn_type):
            st.session_state["current_page"] = page_id
            st.rerun()

    st.markdown("---")

    # Quick KPI sidebar
    kpis = data["kpis"]
    st.markdown("**Quick Metrics**")
    st.markdown(f"💰 Revenue: **{kpis['total_revenue']/1e6:.2f}M**")
    st.markdown(f"📈 GP Margin: **{kpis['gp_margin']}%**")
    st.markdown(f"🤝 Customers: **{kpis['active_customers']}**")
    st.markdown(f"🎯 Win Rate: **{kpis['win_rate']}%**")
    st.markdown(f"📦 Avg Deal: **₹{kpis['avg_deal_size']/1000:.0f}K**")

    st.markdown("---")

    # Logout
    if st.button("🚪 Logout", use_container_width=True):
        logout()

    st.caption("v1.0.0 | © 2025 NovaTech Solutions")


# ── Main Content Router ────────────────────────────────────────────────────────
page = st.session_state.get("current_page", "dashboard")

if not has_access(page):
    st.error("🔒 You don't have permission to access this module.")
    st.info("Please contact your Administrator to request access.")
    st.stop()

if page == "dashboard":
    show_dashboard(data)

elif page == "sales":
    show_sales(data)

elif page == "crm":
    show_crm(data)

elif page == "expenses":
    show_expenses(data)

elif page == "employees":
    show_employees(data)

elif page == "targets":
    show_targets(data)

elif page == "reports":
    show_reports(data)

elif page == "ai_insights":
    show_ai_insights(data)
