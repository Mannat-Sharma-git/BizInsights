"""
Authentication & Role-Based Access Control
"""

import streamlit as st

USERS = {
    "admin": {
        "password":   "admin123",
        "name":       "Admin User",
        "role":       "Administrator",
        "email":      "admin@novatech.com",
        "avatar":     "👤",
        "access":     ["dashboard", "sales", "crm", "expenses", "employees", "targets", "reports", "ai_insights", "settings"],
    },
    "manager": {
        "password":   "manager123",
        "name":       "Rahul Sharma",
        "role":       "Manager",
        "email":      "rahul.sharma@novatech.com",
        "avatar":     "👔",
        "access":     ["dashboard", "sales", "crm", "expenses", "employees", "targets", "reports", "ai_insights"],
    },
    "employee": {
        "password":   "emp123",
        "name":       "Priya Mehta",
        "role":       "Employee",
        "email":      "priya.mehta@novatech.com",
        "avatar":     "🧑‍💼",
        "access":     ["dashboard", "sales", "crm"],
    },
}

ROLE_PERMISSIONS = {
    "Administrator": {
        "can_export":       True,
        "can_edit":         True,
        "can_delete":       True,
        "can_view_salary":  True,
        "can_manage_users": True,
        "can_view_all_reports": True,
    },
    "Manager": {
        "can_export":       True,
        "can_edit":         True,
        "can_delete":       False,
        "can_view_salary":  True,
        "can_manage_users": False,
        "can_view_all_reports": True,
    },
    "Employee": {
        "can_export":       False,
        "can_edit":         False,
        "can_delete":       False,
        "can_view_salary":  False,
        "can_manage_users": False,
        "can_view_all_reports": False,
    },
}


def show_login_page():
    """Render the login screen."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🏢 NovaTech Solutions")
        st.markdown("### Business Performance & Decision Intelligence")
        st.markdown("---")
        st.markdown("#### 🔐 Sign In")

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            if username in USERS and USERS[username]["password"] == password:
                user = USERS[username]
                st.session_state["authenticated"] = True
                st.session_state["user"]           = user
                st.session_state["username"]       = username
                st.session_state["role"]           = user["role"]
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")

        st.markdown("---")
        st.markdown("**Demo Credentials:**")
        demo_data = {
            "Role": ["Administrator", "Manager", "Employee"],
            "Username": ["admin", "manager", "employee"],
            "Password": ["admin123", "manager123", "emp123"],
        }
        import pandas as pd
        st.dataframe(pd.DataFrame(demo_data), hide_index=True, use_container_width=True)

        st.caption("⚠️ Demo system — use sample credentials above")


def logout():
    """Clear session state."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def get_current_user() -> dict:
    return st.session_state.get("user", {})


def has_permission(permission: str) -> bool:
    role = st.session_state.get("role", "Employee")
    return ROLE_PERMISSIONS.get(role, {}).get(permission, False)


def has_access(module: str) -> bool:
    user = get_current_user()
    return module in user.get("access", [])


def require_auth():
    """Gate: redirect to login if not authenticated."""
    if not st.session_state.get("authenticated", False):
        show_login_page()
        st.stop()
