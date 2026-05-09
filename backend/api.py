from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# ✅ CORS (برای اتصال React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/dashboard")
def get_dashboard():

     # 🔹 1. خواندن task data
    tasks_df = pd.read_excel("../data/raw/betavanx_mvp_v1.xlsx")

    # 🔹 2. خواندن گزارش کار
    reports_df = pd.read_excel("../data/raw/work_report.xlsx")
    
    # 🔹 3. خواندن گزارش هزینه
    cost_df = pd.read_excel("../data/raw/cost_report.xlsx")

    # 🔹 3. merge
    df = tasks_df.merge(
        reports_df,
        left_on="id",
        right_on="task_id",
        how="left"
    )
    df = df.merge(
        cost_df,
        left_on="id",
        right_on="task_id",
        how="left"
    )
    print(df.columns)
    # 🔹 2. ساخت دیتا تستی شبیه چیزی که قبلاً داشتی
    df["progress_percent"] = (
        df["executed_qty"] / df["baseline_qty"]
    ) * 100

    # 🔹 planned progress
    df["planned_progress"] = 50

    df["planned_cost"] = df["budget"]

    # 🔹 3. محاسبه expected cost
    df["expected_cost"] = df["planned_cost"] * (df["progress_percent"] / 100)
    # 🔹 CPI
    df["cpi"] = df["expected_cost"] / df["actual_cost"]

    # 🔹 SPI
    df["spi"] = df["progress_percent"] / df["planned_progress"]

    # 🔹 Decision Score
    df["final_score"] = (
        (df["cpi"] * 40) +
        (df["spi"] * 40) +
        (df["progress_percent"] * 0.2)
    )
    print(df[[
        "progress_percent",
        "cpi",
        "spi",
        "final_score"
    ]])
    # 🔹 Risk Score
    df["risk_score"] = 100 - df["final_score"]

    # 🔹 5. alert
    def get_alert(score):

        if score < 60:
            return "🔴 Critical"

        elif score < 80:
            return "🟡 Warning"

        else:
            return "🟢 Good"

    def get_risk_level(risk):

        if risk > 60:
            return "🔴 High Risk"

        elif risk > 30:
            return "🟡 Medium Risk"

        else:
            return "🟢 Low Risk"

    df["alert"] = df["final_score"].apply(get_alert)

    df["risk_level"] = df["risk_score"].apply(get_risk_level)

    # 🔹 6. انتخاب ستون‌ها
    result = df.rename(columns={"id": "task_id"})[
    [
        "task_id",
        "progress_percent",
        "planned_progress",
        "final_score",
        "cpi",
        "spi",
        "alert",
        "risk_score",
        "risk_level",
    ]
]

    # 🔹 7. تبدیل به JSON
    return result.to_dict(orient="records")