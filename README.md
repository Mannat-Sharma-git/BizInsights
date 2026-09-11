# SME Business Performance & Decision Intelligence System

A modern, AI-powered business intelligence platform for Small and Medium Enterprises, built with **Streamlit** and **Google Gemini 2.5 Flash**.

---

## 🚀 Features

| Module | Description |
|---|---|
| 📊 Executive Dashboard | KPI cards, revenue trends, expense breakdown, target vs actual charts, gauges |
| 🛒 Sales Management | Deal tracking, product/rep performance, funnel analysis, discount impact |
| 🤝 CRM | Customer profiles, health scores, segment/industry analysis, acquisition trends |
| 💸 Expense & Profitability | P&L waterfall, budget utilisation, product profitability, monthly trends |
| 👥 Employee Performance | KPI heatmap, radar charts, department analysis, target tracking |
| 🎯 Target Management | Revenue/expense/GP/customer acquisition vs targets |
| 📑 Reports & Analytics | Executive summary, quarterly P&L, MoM trends, HR analytics |
| 🤖 AI Business Insights | Gemini 2.5 Flash — full review, revenue/cost/customer/HR analysis + Q&A |

---

## 🛠️ Setup & Installation

### 1. Install Dependencies

```bash
cd SME_Business_Intelligence
pip install -r requirements.txt
```

### 2. Run the Application

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🔑 Demo Credentials

| Role | Username | Password | Access |
|---|---|---|---|
| Administrator | `admin` | `admin123` | Full access to all modules |
| Manager | `manager` | `manager123` | All modules except settings |
| Employee | `employee` | `emp123` | Dashboard, Sales, CRM only |

---

## 🤖 AI Setup (Gemini 2.5 Flash)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a free API key
3. In the app, navigate to **🤖 AI Insights** → paste your key → **Save**
4. Choose an analysis module or ask any business question

---

## 📁 Project Structure

```
SME_Business_Intelligence/
├── app.py                      # Main entry point
├── requirements.txt
├── .streamlit/
│   └── config.toml             # Theme & server config
└── modules/
    ├── data_engine.py          # Sample data generator
    ├── auth.py                 # Authentication & RBAC
    ├── dashboard.py            # Executive dashboard
    ├── sales.py                # Sales management
    ├── crm.py                  # Customer CRM
    ├── expenses.py             # Expense & profitability
    ├── employees.py            # Employee performance
    ├── targets.py              # Business targets
    ├── reports.py              # Reports & analytics
    └── ai_insights.py          # Gemini AI insights
```

---

## 📊 Sample Data

The system generates **18 months** of realistic business data:
- **~190 sales transactions** across 10 products, 15 customers, 5 reps
- **~1,800 expense records** across 10 categories
- **72 employee performance records** across 12 employees / 6 quarters
- **18 months of target data** with revenue, GP, customer & expense targets

---

## 🌐 Deployment

### Streamlit Community Cloud
1. Push to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → set main file as `SME_Business_Intelligence/app.py`
4. Deploy

### Local Network
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
