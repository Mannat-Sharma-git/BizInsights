"""
AI Business Insight Module — powered by Google Gemini 2.5 Flash
"""

import streamlit as st
import pandas as pd
import json
import google.generativeai as genai
from datetime import datetime


def fmt_currency(val):
    if val >= 1_000_000:
        return f"₹{val/1_000_000:.2f}M"
    elif val >= 1_000:
        return f"₹{val/1_000:.1f}K"
    return f"₹{val:,.0f}"


def build_business_context(data: dict) -> str:
    """Compile a rich, structured business snapshot for the LLM."""
    kpis    = data["kpis"]
    sales   = data["sales"]
    exp     = data["expenses"]
    cust    = data["customers"]
    targets = data["targets"]
    emp     = data["emp_perf"]

    won = sales[sales["status"] == "Closed Won"]
    approved_exp = exp[exp["status"] == "Approved"]

    # Monthly trend (last 6)
    monthly_rev = won.groupby("month")["revenue"].sum().sort_index().tail(6)
    monthly_exp = approved_exp.groupby("month")["amount"].sum().sort_index().tail(6)
    monthly_gp  = won.groupby("month")["gross_profit"].sum().sort_index().tail(6)

    # Category breakdown
    cat_rev = won.groupby("category")["revenue"].sum().to_dict()
    exp_cat = approved_exp.groupby("category")["amount"].sum().sort_values(ascending=False).head(5).to_dict()

    # Sales rep performance
    rep_perf = won.groupby("sales_rep").agg(
        revenue=("revenue","sum"), deals=("sale_id","count")
    ).to_dict(orient="index")

    # Employee KPI summary
    emp_summary = emp.groupby("department")["kpi_score"].mean().round(1).to_dict()

    # Targets latest
    latest_tgt = targets.tail(3).to_dict(orient="records")

    # Customer insights
    at_risk_custs = cust[cust["status"]=="At Risk"]["name"].tolist()
    top_custs     = cust.sort_values("total_revenue", ascending=False).head(5)[["name","total_revenue"]].to_dict(orient="records")

    context = f"""
COMPANY: {data['company']}
REPORTING PERIOD: January 2024 – June 2025 (18 months of data)

=== KEY PERFORMANCE INDICATORS (Last 6 months) ===
- Total Revenue: {fmt_currency(kpis['total_revenue'])}
- Revenue Growth (vs prior 6M): {kpis['revenue_growth']:+.1f}%
- Gross Profit: {fmt_currency(kpis['gross_profit'])}
- GP Growth: {kpis['gp_growth']:+.1f}%
- GP Margin: {kpis['gp_margin']}% (Target: 55%)
- Total Expenses: {fmt_currency(kpis['total_expenses'])}
- Expense Growth: {kpis['expense_growth']:+.1f}%
- Net Profit: {fmt_currency(kpis['net_profit'])}
- Net Profit Margin: {kpis['net_profit_margin']}%
- Active Customers: {kpis['active_customers']} of {kpis['total_customers']}
- Average Deal Size: {fmt_currency(kpis['avg_deal_size'])}
- Win Rate: {kpis['win_rate']}%
- Latest Month Revenue Achievement: {kpis['latest_achievement']}%

=== MONTHLY REVENUE TREND (Last 6 Months) ===
{monthly_rev.to_string()}

=== MONTHLY GROSS PROFIT TREND ===
{monthly_gp.to_string()}

=== MONTHLY EXPENSE TREND ===
{monthly_exp.to_string()}

=== REVENUE BY CATEGORY ===
{json.dumps(cat_rev, indent=2)}

=== TOP 5 EXPENSE CATEGORIES ===
{json.dumps(exp_cat, indent=2)}

=== SALES REPRESENTATIVE PERFORMANCE ===
{json.dumps(rep_perf, indent=2)}

=== EMPLOYEE KPI BY DEPARTMENT ===
{json.dumps(emp_summary, indent=2)}

=== CUSTOMER INSIGHTS ===
Top 5 Customers by Revenue:
{json.dumps([{"name":c["name"], "revenue": fmt_currency(c["total_revenue"])} for c in top_custs], indent=2)}
At-Risk Customers: {', '.join(at_risk_custs) if at_risk_custs else 'None identified'}

=== RECENT TARGET ACHIEVEMENT (Last 3 Months) ===
{json.dumps([{
    "month": t["month_label"],
    "rev_target": fmt_currency(t["rev_target"]),
    "rev_actual": fmt_currency(t["rev_actual"]),
    "achievement": f"{t['rev_achievement']:.1f}%",
    "gp_margin_target": f"{t['gp_margin_target']}%",
    "gp_margin_actual": f"{t['gp_margin_actual']}%",
} for t in latest_tgt], indent=2)}
"""
    return context.strip()


def get_ai_analysis(api_key: str, context: str, question: str, mode: str = "full") -> str:
    """Call Gemini 2.5 Flash with business context and return the response."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")

    system_prompt = """You are a senior business intelligence analyst and strategic advisor specialising in 
Small and Medium Enterprises (SMEs). Your role is to analyse business data, identify trends, spot risks 
and opportunities, and provide clear, actionable management recommendations.

Guidelines:
- Use structured, professional language suitable for senior management
- Be specific — cite actual numbers from the data provided
- Provide prioritised, actionable recommendations
- Identify both risks and opportunities
- Use bullet points and sections for clarity
- Keep responses focused and avoid generic advice
- Reference specific months, products, customers, or team members when relevant"""

    if mode == "full":
        user_message = f"""Based on the following business data snapshot, provide a comprehensive analysis:

{context}

Please provide:
1. **Executive Summary** — 3-4 key observations about business health
2. **Performance Highlights** — What is going well and why
3. **Critical Issues & Risks** — Problems requiring immediate attention (with severity: High/Medium/Low)
4. **Growth Opportunities** — Specific opportunities identified from the data
5. **Strategic Recommendations** — Top 5 prioritised, actionable recommendations with expected impact
6. **Watch List** — Items to monitor closely in the next period"""

    elif mode == "revenue":
        user_message = f"""Analyse the revenue performance using this business data:

{context}

Focus on:
1. Revenue trend analysis and growth trajectory
2. Best and worst performing categories/products
3. Sales team effectiveness
4. Revenue concentration risks (customer, product)
5. Specific revenue growth recommendations"""

    elif mode == "expenses":
        user_message = f"""Analyse the expense and profitability situation using this business data:

{context}

Focus on:
1. Cost structure analysis and efficiency
2. Budget variances and overruns
3. Profitability improvement opportunities
4. Cost optimisation recommendations
5. ROI assessment for major expense categories"""

    elif mode == "customers":
        user_message = f"""Analyse the customer portfolio and CRM situation using this business data:

{context}

Focus on:
1. Customer health and retention risks
2. Revenue concentration analysis
3. Customer acquisition trends
4. At-risk customer action plan
5. Customer lifetime value improvement strategies"""

    elif mode == "employees":
        user_message = f"""Analyse employee performance and workforce effectiveness using this business data:

{context}

Focus on:
1. Department and individual performance patterns
2. High performers and underperformers
3. Sales team effectiveness
4. HR risks and talent retention considerations
5. Performance improvement recommendations"""

    else:
        user_message = f"""You are analysing business data for {data.get('company', 'an SME')}.

Business Context:
{context}

User Question: {question}

Provide a clear, specific, data-driven answer based on the business data above."""

    response = model.generate_content(
        [{"role": "user", "parts": [system_prompt + "\n\n" + user_message]}],
        generation_config={
            "temperature":     0.4,
            "top_p":           0.95,
            "max_output_tokens": 4096,
        }
    )
    return response.text


def show_ai_insights(data: dict):
    st.markdown("# 🤖 AI Business Intelligence")
    st.markdown("*Powered by Google Gemini 2.5 Flash — Intelligent insights from your business data.*")
    st.markdown("---")

    # ── API Key Configuration ─────────────────────────────────────────
    with st.expander("⚙️ Gemini API Configuration", expanded=not bool(st.session_state.get("gemini_key",""))):
        col_key, col_btn = st.columns([4, 1])
        with col_key:
            api_key_input = st.text_input(
                "Google Gemini API Key",
                value=st.session_state.get("gemini_key", ""),
                type="password",
                placeholder="Enter your Gemini API Key (AIza...)",
                help="Get your key at https://aistudio.google.com/app/apikey"
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Save Key", use_container_width=True):
                if api_key_input.strip():
                    st.session_state["gemini_key"] = api_key_input.strip()
                    st.success("API key saved!")
                    st.rerun()
                else:
                    st.error("Please enter a valid API key.")

    api_key = st.session_state.get("gemini_key", "")
    if not api_key:
        st.info("🔑 Please configure your Gemini API key above to enable AI insights.")
        st.markdown("**How to get an API key:**")
        st.markdown("1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)")
        st.markdown("2. Sign in with your Google account")
        st.markdown("3. Click **Create API Key** → copy and paste above")
        return

    st.success("✅ Gemini API key configured. AI analysis enabled.")

    # ── Business Context Preview ──────────────────────────────────────
    context = build_business_context(data)
    with st.expander("📋 Business Data Context (sent to AI)", expanded=False):
        st.code(context, language="text")

    st.markdown("---")

    # ── Analysis Type Selector ────────────────────────────────────────
    st.markdown("### 🧠 AI Analysis Modules")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Full Business Review",
        "💰 Revenue Analysis",
        "💸 Cost & Profitability",
        "🤝 Customer Intelligence",
        "👥 Workforce Analysis",
        "💬 Ask Anything",
    ])

    def run_analysis(tab_mode: str, button_label: str, cache_key: str):
        result_key = f"ai_result_{cache_key}"
        if st.button(f"🚀 {button_label}", key=f"btn_{cache_key}", use_container_width=True, type="primary"):
            with st.spinner("🤖 Gemini is analysing your business data..."):
                try:
                    result = get_ai_analysis(api_key, context, "", mode=tab_mode)
                    st.session_state[result_key] = result
                except Exception as e:
                    st.error(f"❌ Error calling Gemini API: {str(e)}")
                    return
        if result_key in st.session_state:
            st.markdown(st.session_state[result_key])
            if st.button(f"🔄 Regenerate", key=f"regen_{cache_key}"):
                if result_key in st.session_state:
                    del st.session_state[result_key]
                st.rerun()

    with tab1:
        st.markdown("**Comprehensive business review** — Executive summary, risks, opportunities, and top strategic recommendations based on all available data.")
        run_analysis("full", "Generate Full Business Review", "full")

    with tab2:
        st.markdown("**Revenue deep-dive** — Sales trends, category performance, team effectiveness, and revenue growth strategies.")
        run_analysis("revenue", "Analyse Revenue Performance", "revenue")

    with tab3:
        st.markdown("**Cost & profitability analysis** — Expense structure, budget variance, margin optimisation, and cost reduction opportunities.")
        run_analysis("expenses", "Analyse Costs & Profitability", "expenses")

    with tab4:
        st.markdown("**Customer intelligence** — Portfolio health, retention risks, acquisition trends, and customer value strategies.")
        run_analysis("customers", "Analyse Customer Portfolio", "customers")

    with tab5:
        st.markdown("**Workforce analysis** — Employee performance patterns, team effectiveness, KPI review, and HR recommendations.")
        run_analysis("employees", "Analyse Workforce Performance", "employees")

    with tab6:
        st.markdown("**Interactive Q&A** — Ask any specific business question and get a data-driven answer.")
        st.markdown("**Example questions:**")
        examples = [
            "Which product should we prioritise for Q3 2025 growth?",
            "What is causing the expense overrun and how can we fix it?",
            "Who are our most valuable customers and how do we retain them?",
            "What are the early warning signs of business decline in our data?",
            "How can we improve our sales win rate?",
        ]
        selected_example = st.selectbox("📝 Select an example question or type your own:", [""] + examples)

        user_question = st.text_area(
            "Your Question",
            value=selected_example,
            height=100,
            placeholder="Type your business question here...",
            key="ai_question"
        )

        if st.button("💬 Get AI Answer", type="primary", use_container_width=True, key="btn_qa"):
            if not user_question.strip():
                st.warning("Please enter a question first.")
            else:
                with st.spinner("🤖 Gemini is thinking..."):
                    try:
                        answer = get_ai_analysis(api_key, context, user_question, mode="qa")
                        st.session_state["ai_qa_result"] = answer
                        st.session_state["ai_qa_question"] = user_question
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

        if "ai_qa_result" in st.session_state:
            st.markdown("---")
            st.markdown(f"**Q: {st.session_state.get('ai_qa_question','')}**")
            st.markdown(st.session_state["ai_qa_result"])

    # ── AI Insight History ────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📜 Analysis History")
    history_keys = {
        "Full Business Review":    "ai_result_full",
        "Revenue Analysis":        "ai_result_revenue",
        "Cost & Profitability":    "ai_result_expenses",
        "Customer Intelligence":   "ai_result_customers",
        "Workforce Analysis":      "ai_result_employees",
    }
    generated = {k: v for k, v in history_keys.items() if v in st.session_state}
    if generated:
        for label, key in generated.items():
            with st.expander(f"📄 {label}"):
                st.markdown(st.session_state[key])
        # Clear all
        if st.button("🗑️ Clear All AI Results"):
            for key in list(history_keys.values()) + ["ai_qa_result","ai_qa_question"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    else:
        st.info("No AI analyses generated yet. Use the tabs above to run an analysis.")
