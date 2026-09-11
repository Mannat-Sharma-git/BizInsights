"""
Data Engine — generates and manages all realistic sample business data
for the SME Business Performance & Decision Intelligence System.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ──────────────────────────────────────────────
# Seed for reproducibility
# ──────────────────────────────────────────────
np.random.seed(42)
random.seed(42)

COMPANY_NAME = "NovaTech Solutions Pvt. Ltd."
CURRENT_DATE = datetime(2025, 6, 30)
START_DATE   = datetime(2024, 1, 1)

# ──────────────────────────────────────────────
# Reference lists
# ──────────────────────────────────────────────
PRODUCTS = [
    {"name": "Enterprise CRM Suite",     "category": "Software",  "price": 12500},
    {"name": "Cloud Hosting Pro",        "category": "Services",  "price": 4800},
    {"name": "Data Analytics Platform",  "category": "Software",  "price": 18000},
    {"name": "IT Security Package",      "category": "Software",  "price": 9500},
    {"name": "DevOps Toolkit",           "category": "Software",  "price": 7200},
    {"name": "Managed Support (Annual)", "category": "Services",  "price": 3600},
    {"name": "Training Workshop",        "category": "Training",  "price": 2500},
    {"name": "Custom API Integration",   "category": "Services",  "price": 14000},
    {"name": "Mobile App Development",   "category": "Services",  "price": 22000},
    {"name": "Business Intelligence Pro","category": "Software",  "price": 16000},
]

CUSTOMERS = [
    {"id": "C001", "name": "Apex Manufacturing Ltd.",    "industry": "Manufacturing", "city": "Mumbai",    "segment": "Enterprise"},
    {"id": "C002", "name": "GreenField Agro Corp.",      "industry": "Agriculture",   "city": "Pune",      "segment": "Mid-Market"},
    {"id": "C003", "name": "Stellar Retail Group",       "industry": "Retail",        "city": "Delhi",     "segment": "Enterprise"},
    {"id": "C004", "name": "BlueSky Logistics",          "industry": "Logistics",     "city": "Chennai",   "segment": "Mid-Market"},
    {"id": "C005", "name": "Innovate FinTech",           "industry": "Finance",       "city": "Bangalore", "segment": "Enterprise"},
    {"id": "C006", "name": "Horizon Healthcare",         "industry": "Healthcare",    "city": "Hyderabad", "segment": "Mid-Market"},
    {"id": "C007", "name": "TechEdge Startups",          "industry": "Technology",    "city": "Bangalore", "segment": "SME"},
    {"id": "C008", "name": "Prime Construction Co.",     "industry": "Construction",  "city": "Kolkata",   "segment": "Mid-Market"},
    {"id": "C009", "name": "NextGen Education Hub",      "industry": "Education",     "city": "Jaipur",    "segment": "SME"},
    {"id": "C010", "name": "Sigma Pharma Ltd.",          "industry": "Pharma",        "city": "Ahmedabad", "segment": "Enterprise"},
    {"id": "C011", "name": "EcoGreen Energy",            "industry": "Energy",        "city": "Surat",     "segment": "Mid-Market"},
    {"id": "C012", "name": "DigitalWave Media",          "industry": "Media",         "city": "Mumbai",    "segment": "SME"},
    {"id": "C013", "name": "FastTrack E-Commerce",       "industry": "E-Commerce",    "city": "Delhi",     "segment": "Mid-Market"},
    {"id": "C014", "name": "PeakPerform Sports",         "industry": "Retail",        "city": "Chennai",   "segment": "SME"},
    {"id": "C015", "name": "AuraLux Hotels & Resorts",   "industry": "Hospitality",   "city": "Goa",       "segment": "Mid-Market"},
]

EMPLOYEES = [
    {"id": "E001", "name": "Rahul Sharma",    "role": "Sales Manager",       "dept": "Sales",     "email": "rahul.sharma@novatech.com",    "salary": 95000},
    {"id": "E002", "name": "Priya Mehta",     "role": "Sr. Sales Executive", "dept": "Sales",     "email": "priya.mehta@novatech.com",     "salary": 72000},
    {"id": "E003", "name": "Arjun Patel",     "role": "Sales Executive",     "dept": "Sales",     "email": "arjun.patel@novatech.com",     "salary": 58000},
    {"id": "E004", "name": "Sneha Kapoor",    "role": "Sales Executive",     "dept": "Sales",     "email": "sneha.kapoor@novatech.com",    "salary": 58000},
    {"id": "E005", "name": "Vikram Singh",    "role": "Account Manager",     "dept": "Sales",     "email": "vikram.singh@novatech.com",    "salary": 68000},
    {"id": "E006", "name": "Neha Joshi",      "role": "Marketing Manager",   "dept": "Marketing", "email": "neha.joshi@novatech.com",      "salary": 88000},
    {"id": "E007", "name": "Amit Verma",      "role": "Digital Marketer",    "dept": "Marketing", "email": "amit.verma@novatech.com",      "salary": 62000},
    {"id": "E008", "name": "Kavya Reddy",     "role": "HR Manager",          "dept": "HR",        "email": "kavya.reddy@novatech.com",     "salary": 82000},
    {"id": "E009", "name": "Suresh Nair",     "role": "Senior Developer",    "dept": "Tech",      "email": "suresh.nair@novatech.com",     "salary": 98000},
    {"id": "E010", "name": "Divya Iyer",      "role": "Project Manager",     "dept": "Tech",      "email": "divya.iyer@novatech.com",      "salary": 92000},
    {"id": "E011", "name": "Rohan Gupta",     "role": "Finance Manager",     "dept": "Finance",   "email": "rohan.gupta@novatech.com",     "salary": 90000},
    {"id": "E012", "name": "Ankita Mishra",   "role": "Financial Analyst",   "dept": "Finance",   "email": "ankita.mishra@novatech.com",   "salary": 70000},
]

EXPENSE_CATEGORIES = [
    "Salaries & Benefits", "Office Rent", "Marketing & Advertising",
    "Software & Subscriptions", "Travel & Accommodation", "Utilities",
    "Hardware & Equipment", "Professional Services", "Training & Development",
    "Miscellaneous"
]

# ──────────────────────────────────────────────
# Sales Data
# ──────────────────────────────────────────────
def generate_sales_data() -> pd.DataFrame:
    records = []
    sale_id = 1
    sales_reps = [e for e in EMPLOYEES if e["dept"] == "Sales"]

    for month_offset in range(18):
        base_date = START_DATE + timedelta(days=month_offset * 30)
        # Slightly increasing trend with seasonality
        volume   = int(8 + month_offset * 0.4 + 2 * np.sin(month_offset * np.pi / 6))
        for _ in range(volume):
            product  = random.choice(PRODUCTS)
            customer = random.choice(CUSTOMERS)
            rep      = random.choice(sales_reps)
            qty      = random.randint(1, 5)
            discount = random.choice([0, 0, 0, 5, 10, 15])
            unit_price = product["price"] * (1 - discount / 100)
            revenue    = round(unit_price * qty, 2)
            cogs       = round(revenue * random.uniform(0.38, 0.52), 2)
            gross_profit = round(revenue - cogs, 2)
            sale_date  = base_date + timedelta(days=random.randint(0, 28))
            status     = random.choices(
                ["Closed Won", "Closed Won", "Closed Won", "Closed Lost", "In Progress"],
                weights=[50, 30, 10, 7, 3]
            )[0]

            records.append({
                "sale_id":       f"S{sale_id:04d}",
                "date":          sale_date,
                "month":         sale_date.strftime("%Y-%m"),
                "month_label":   sale_date.strftime("%b %Y"),
                "product":       product["name"],
                "category":      product["category"],
                "customer_id":   customer["id"],
                "customer_name": customer["name"],
                "industry":      customer["industry"],
                "segment":       customer["segment"],
                "sales_rep":     rep["name"],
                "rep_id":        rep["id"],
                "quantity":      qty,
                "unit_price":    round(unit_price, 2),
                "discount_pct":  discount,
                "revenue":       revenue,
                "cogs":          cogs,
                "gross_profit":  gross_profit,
                "gp_margin":     round(gross_profit / revenue * 100, 1) if revenue > 0 else 0,
                "status":        status,
            })
            sale_id += 1

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ──────────────────────────────────────────────
# Customer Data
# ──────────────────────────────────────────────
def generate_customer_data(sales_df: pd.DataFrame) -> pd.DataFrame:
    cust_base = pd.DataFrame(CUSTOMERS)
    cust_base["join_date"] = [
        START_DATE + timedelta(days=random.randint(-365, 0))
        for _ in range(len(CUSTOMERS))
    ]
    cust_base["status"]  = random.choices(["Active", "Active", "Active", "Inactive", "At Risk"],
                                           k=len(CUSTOMERS))
    cust_base["contact"] = [f"+91 98{random.randint(1000000,9999999)}" for _ in range(len(CUSTOMERS))]
    cust_base["email"]   = [
        f"{c['name'].split()[0].lower()}@{c['name'].split()[-1].lower()}.com"
        for c in CUSTOMERS
    ]

    # Aggregate from sales
    won = sales_df[sales_df["status"] == "Closed Won"]
    agg = (
        won.groupby("customer_id")
        .agg(
            total_revenue=("revenue", "sum"),
            total_orders=("sale_id", "count"),
            last_purchase=("date", "max"),
            avg_order_value=("revenue", "mean"),
        )
        .reset_index()
    )
    cust_base = cust_base.merge(agg, left_on="id", right_on="customer_id", how="left")
    cust_base["total_revenue"]    = cust_base["total_revenue"].fillna(0).round(2)
    cust_base["total_orders"]     = cust_base["total_orders"].fillna(0).astype(int)
    cust_base["avg_order_value"]  = cust_base["avg_order_value"].fillna(0).round(2)
    cust_base["last_purchase"]    = pd.to_datetime(cust_base["last_purchase"])

    # Customer health score (0-100)
    max_rev = cust_base["total_revenue"].max() or 1
    cust_base["health_score"] = (
        (cust_base["total_revenue"] / max_rev * 50) +
        (np.clip(cust_base["total_orders"] / 10, 0, 1) * 30) +
        np.random.uniform(5, 20, len(cust_base))
    ).clip(0, 100).round(1)

    return cust_base


# ──────────────────────────────────────────────
# Expense Data
# ──────────────────────────────────────────────
def generate_expense_data() -> pd.DataFrame:
    records = []
    exp_id  = 1

    monthly_budgets = {
        "Salaries & Benefits":       85000,
        "Office Rent":               12000,
        "Marketing & Advertising":    8500,
        "Software & Subscriptions":   4500,
        "Travel & Accommodation":     3500,
        "Utilities":                  2200,
        "Hardware & Equipment":       5500,
        "Professional Services":      4000,
        "Training & Development":     2500,
        "Miscellaneous":              1800,
    }

    for month_offset in range(18):
        base_date = START_DATE + timedelta(days=month_offset * 30)
        for category, budget in monthly_budgets.items():
            # 2-6 entries per category per month
            n_entries = random.randint(2, 6)
            variance  = random.uniform(-0.12, 0.18)
            total_amt = budget * (1 + variance)
            amounts   = np.random.dirichlet(np.ones(n_entries)) * total_amt

            for amt in amounts:
                exp_date = base_date + timedelta(days=random.randint(0, 28))
                records.append({
                    "expense_id":  f"EX{exp_id:04d}",
                    "date":        exp_date,
                    "month":       exp_date.strftime("%Y-%m"),
                    "month_label": exp_date.strftime("%b %Y"),
                    "category":    category,
                    "amount":      round(amt, 2),
                    "approved_by": random.choice(["Rohan Gupta", "Kavya Reddy", "Rahul Sharma"]),
                    "status":      random.choices(["Approved", "Approved", "Pending", "Rejected"],
                                                   weights=[70, 15, 10, 5])[0],
                    "budget":      budget,
                })
                exp_id += 1

    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


# ──────────────────────────────────────────────
# Employee Performance Data
# ──────────────────────────────────────────────
def generate_employee_performance(sales_df: pd.DataFrame) -> pd.DataFrame:
    records = []

    quarters = [
        ("Q1 2024", "2024-01", "2024-03"),
        ("Q2 2024", "2024-04", "2024-06"),
        ("Q3 2024", "2024-07", "2024-09"),
        ("Q4 2024", "2024-10", "2024-12"),
        ("Q1 2025", "2025-01", "2025-03"),
        ("Q2 2025", "2025-04", "2025-06"),
    ]

    for emp in EMPLOYEES:
        for quarter, q_start, q_end in quarters:
            # Sales reps: derive from sales data
            if emp["dept"] == "Sales":
                mask  = (
                    (sales_df["rep_id"] == emp["id"]) &
                    (sales_df["month"] >= q_start) &
                    (sales_df["month"] <= q_end) &
                    (sales_df["status"] == "Closed Won")
                )
                q_rev = sales_df[mask]["revenue"].sum()
                target_rev = emp["salary"] * random.uniform(4, 7)
            else:
                q_rev = 0
                target_rev = 0

            rating  = round(random.uniform(2.8, 5.0), 1)
            tasks_target   = random.randint(15, 30)
            tasks_complete = min(tasks_target, int(tasks_target * random.uniform(0.70, 1.10)))
            attendance     = round(random.uniform(88, 100), 1)
            kpi_score      = round(
                (rating / 5 * 40) +
                (min(tasks_complete / tasks_target, 1) * 35) +
                ((attendance / 100) * 25),
                1
            )

            records.append({
                "emp_id":          emp["id"],
                "name":            emp["name"],
                "role":            emp["role"],
                "department":      emp["dept"],
                "quarter":         quarter,
                "q_start":         q_start,
                "q_end":           q_end,
                "sales_revenue":   round(q_rev, 2),
                "sales_target":    round(target_rev, 2),
                "rating":          rating,
                "tasks_target":    tasks_target,
                "tasks_complete":  tasks_complete,
                "attendance_pct":  attendance,
                "kpi_score":       kpi_score,
                "training_hrs":    random.randint(0, 20),
                "leaves_taken":    random.randint(0, 6),
            })

    return pd.DataFrame(records)


# ──────────────────────────────────────────────
# Business Targets Data
# ──────────────────────────────────────────────
def generate_targets_data(sales_df: pd.DataFrame, expense_df: pd.DataFrame) -> pd.DataFrame:
    records = []

    monthly_targets = {
        "2024-01": {"revenue": 150000,  "new_customers": 3,  "expense_limit": 200000, "gp_margin": 48},
        "2024-02": {"revenue": 160000,  "new_customers": 3,  "expense_limit": 205000, "gp_margin": 48},
        "2024-03": {"revenue": 170000,  "new_customers": 4,  "expense_limit": 210000, "gp_margin": 49},
        "2024-04": {"revenue": 180000,  "new_customers": 4,  "expense_limit": 210000, "gp_margin": 49},
        "2024-05": {"revenue": 190000,  "new_customers": 4,  "expense_limit": 215000, "gp_margin": 50},
        "2024-06": {"revenue": 200000,  "new_customers": 5,  "expense_limit": 215000, "gp_margin": 50},
        "2024-07": {"revenue": 210000,  "new_customers": 5,  "expense_limit": 220000, "gp_margin": 51},
        "2024-08": {"revenue": 220000,  "new_customers": 5,  "expense_limit": 225000, "gp_margin": 51},
        "2024-09": {"revenue": 230000,  "new_customers": 6,  "expense_limit": 225000, "gp_margin": 52},
        "2024-10": {"revenue": 240000,  "new_customers": 6,  "expense_limit": 230000, "gp_margin": 52},
        "2024-11": {"revenue": 250000,  "new_customers": 6,  "expense_limit": 235000, "gp_margin": 52},
        "2024-12": {"revenue": 260000,  "new_customers": 7,  "expense_limit": 240000, "gp_margin": 53},
        "2025-01": {"revenue": 270000,  "new_customers": 5,  "expense_limit": 245000, "gp_margin": 53},
        "2025-02": {"revenue": 280000,  "new_customers": 5,  "expense_limit": 250000, "gp_margin": 54},
        "2025-03": {"revenue": 290000,  "new_customers": 6,  "expense_limit": 255000, "gp_margin": 54},
        "2025-04": {"revenue": 300000,  "new_customers": 6,  "expense_limit": 260000, "gp_margin": 55},
        "2025-05": {"revenue": 310000,  "new_customers": 7,  "expense_limit": 265000, "gp_margin": 55},
        "2025-06": {"revenue": 320000,  "new_customers": 7,  "expense_limit": 270000, "gp_margin": 55},
    }

    won = sales_df[sales_df["status"] == "Closed Won"]
    monthly_rev  = won.groupby("month")["revenue"].sum()
    monthly_gp   = won.groupby("month")["gross_profit"].sum()
    monthly_exp  = expense_df[expense_df["status"] == "Approved"].groupby("month")["amount"].sum()
    monthly_cust = won.groupby("month")["customer_id"].nunique()

    for month, tgt in monthly_targets.items():
        act_rev  = monthly_rev.get(month, 0)
        act_exp  = monthly_exp.get(month, 0)
        act_cust = int(monthly_cust.get(month, 0))
        act_gp   = monthly_gp.get(month, 0)
        act_gpm  = round(act_gp / act_rev * 100, 1) if act_rev > 0 else 0

        records.append({
            "month":               month,
            "month_label":         datetime.strptime(month, "%Y-%m").strftime("%b %Y"),
            "rev_target":          tgt["revenue"],
            "rev_actual":          round(act_rev, 2),
            "rev_achievement":     round(act_rev / tgt["revenue"] * 100, 1) if tgt["revenue"] else 0,
            "exp_limit":           tgt["expense_limit"],
            "exp_actual":          round(act_exp, 2),
            "exp_variance":        round(act_exp - tgt["expense_limit"], 2),
            "new_cust_target":     tgt["new_customers"],
            "new_cust_actual":     act_cust,
            "gp_margin_target":    tgt["gp_margin"],
            "gp_margin_actual":    act_gpm,
        })

    return pd.DataFrame(records)


# ──────────────────────────────────────────────
# KPI Summary
# ──────────────────────────────────────────────
def compute_kpis(sales_df, expense_df, customer_df, targets_df) -> dict:
    won = sales_df[sales_df["status"] == "Closed Won"]

    # Current period = last 6 months available
    current_months = sorted(won["month"].unique())[-6:]
    prev_months    = sorted(won["month"].unique())[-12:-6]

    cur_rev  = won[won["month"].isin(current_months)]["revenue"].sum()
    prev_rev = won[won["month"].isin(prev_months)]["revenue"].sum()
    cur_gp   = won[won["month"].isin(current_months)]["gross_profit"].sum()
    prev_gp  = won[won["month"].isin(prev_months)]["gross_profit"].sum()

    cur_exp  = expense_df[(expense_df["month"].isin(current_months)) & (expense_df["status"] == "Approved")]["amount"].sum()
    prev_exp = expense_df[(expense_df["month"].isin(prev_months))   & (expense_df["status"] == "Approved")]["amount"].sum()

    active_customers = len(customer_df[customer_df["status"] == "Active"])
    total_customers  = len(customer_df)

    avg_deal   = won["revenue"].mean()
    win_rate   = len(won) / len(sales_df) * 100
    gp_margin  = cur_gp / cur_rev * 100 if cur_rev > 0 else 0
    net_profit = cur_rev - cur_exp
    npm        = net_profit / cur_rev * 100 if cur_rev > 0 else 0

    # Target achievement (latest month)
    latest = targets_df.iloc[-1]

    return {
        "total_revenue":       round(cur_rev, 0),
        "revenue_growth":      round((cur_rev - prev_rev) / prev_rev * 100, 1) if prev_rev else 0,
        "gross_profit":        round(cur_gp, 0),
        "gp_growth":           round((cur_gp - prev_gp) / prev_gp * 100, 1) if prev_gp else 0,
        "gp_margin":           round(gp_margin, 1),
        "total_expenses":      round(cur_exp, 0),
        "expense_growth":      round((cur_exp - prev_exp) / prev_exp * 100, 1) if prev_exp else 0,
        "net_profit":          round(net_profit, 0),
        "net_profit_margin":   round(npm, 1),
        "active_customers":    active_customers,
        "total_customers":     total_customers,
        "avg_deal_size":       round(avg_deal, 0),
        "win_rate":            round(win_rate, 1),
        "total_transactions":  len(won),
        "latest_rev_target":   latest["rev_target"],
        "latest_rev_actual":   latest["rev_actual"],
        "latest_achievement":  latest["rev_achievement"],
    }


# ──────────────────────────────────────────────
# Master loader (cached via st.cache_data)
# ──────────────────────────────────────────────
def load_all_data() -> dict:
    sales_df    = generate_sales_data()
    expense_df  = generate_expense_data()
    customer_df = generate_customer_data(sales_df)
    emp_perf_df = generate_employee_performance(sales_df)
    targets_df  = generate_targets_data(sales_df, expense_df)
    kpis        = compute_kpis(sales_df, expense_df, customer_df, targets_df)

    return {
        "sales":       sales_df,
        "expenses":    expense_df,
        "customers":   customer_df,
        "employees":   pd.DataFrame(EMPLOYEES),
        "emp_perf":    emp_perf_df,
        "targets":     targets_df,
        "kpis":        kpis,
        "products":    pd.DataFrame(PRODUCTS),
        "company":     COMPANY_NAME,
        "current_date": CURRENT_DATE,
    }
