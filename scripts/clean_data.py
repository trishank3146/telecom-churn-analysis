"""
Step 1 - Clean the raw data and add analysis columns.
Step 2 - Score every active customer's churn risk (Logistic Regression).

Input:   data/raw/telco_customer_churn.csv
Outputs: data/processed/customers_clean.csv      (all customers, used by SQL + Power BI)
         data/processed/active_customer_risk.csv (active customers with a risk score)
         results/model_metrics.txt

Usage:  python scripts/clean_data.py
"""

import os

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(ROOT, "data", "raw", "telco_customer_churn.csv")
PROCESSED = os.path.join(ROOT, "data", "processed")
RESULTS = os.path.join(ROOT, "results")

ADDONS = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
          "StreamingTV", "StreamingMovies"]


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    report = {"rows_in": len(df)}

    # 1. Remove exact duplicate customers
    df = df.drop_duplicates(subset="customerID")
    report["duplicates_removed"] = report["rows_in"] - len(df)

    # 2. TotalCharges is text with blanks for new customers -> numeric, blank = 0
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"].astype(str).str.strip(), errors="coerce")
    report["blank_total_charges_fixed"] = int(df["TotalCharges"].isna().sum())
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

    # 3. Consistent Yes/No values
    df["SeniorCitizen"] = df["SeniorCitizen"].map({1: "Yes", 0: "No"})
    df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)

    # 4. Analysis columns
    df["TenureGroup"] = pd.cut(df["tenure"], bins=[-1, 12, 24, 48, 72],
                               labels=["0-12 months", "13-24 months", "25-48 months", "49-72 months"])
    df["ChargeBand"] = pd.cut(df["MonthlyCharges"], bins=[0, 35, 70, 90, 200],
                              labels=["Low (<35)", "Medium (35-70)", "High (70-90)", "Premium (90+)"])
    df["AddOnServices"] = (df[ADDONS] == "Yes").sum(axis=1)
    df["HasSupportAddOns"] = np.where((df["TechSupport"] == "Yes") | (df["OnlineSecurity"] == "Yes"),
                                      "Yes", "No")
    df["AutoPay"] = np.where(df["PaymentMethod"].str.contains("automatic"), "Yes", "No")
    # Monthly revenue lost from customers who left
    df["MonthlyRevenueLost"] = np.where(df["ChurnFlag"] == 1, df["MonthlyCharges"], 0.0)

    report["rows_out"] = len(df)
    for key, value in report.items():
        print(f"  {key}: {value}")
    return df


FEATURES_CAT = ["Contract", "InternetService", "PaymentMethod", "PaperlessBilling", "TechSupport",
                "OnlineSecurity", "SeniorCitizen", "Partner", "Dependents", "MultipleLines"]
FEATURES_NUM = ["tenure", "MonthlyCharges", "AddOnServices"]


def score_risk(df: pd.DataFrame):
    """Train a churn model and score active customers. Returns (scored_active_df, metrics_text)."""
    x = df[FEATURES_CAT + FEATURES_NUM]
    y = df["ChurnFlag"]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42, stratify=y)

    model = Pipeline([
        ("prep", ColumnTransformer([
            ("cat", OneHotEncoder(handle_unknown="ignore"), FEATURES_CAT),
            ("num", StandardScaler(), FEATURES_NUM),
        ])),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    model.fit(x_train, y_train)

    proba = model.predict_proba(x_test)[:, 1]
    auc = roc_auc_score(y_test, proba)
    metrics = (f"Churn risk model: Logistic Regression (class_weight=balanced)\n"
               f"Train customers: {len(x_train)}  Test customers: {len(x_test)}\n"
               f"ROC-AUC: {auc:.3f}\n\n"
               + classification_report(y_test, (proba >= 0.5).astype(int),
                                       target_names=["Stayed", "Churned"]))

    active = df[df["ChurnFlag"] == 0].copy()
    active["ChurnRiskScore"] = np.round(model.predict_proba(active[FEATURES_CAT + FEATURES_NUM])[:, 1], 3)
    active["RiskLevel"] = pd.cut(active["ChurnRiskScore"], bins=[-0.01, 0.4, 0.7, 1.0],
                                 labels=["Low", "Medium", "High"])
    columns = ["customerID", "Contract", "tenure", "TenureGroup", "InternetService", "PaymentMethod",
               "TechSupport", "MonthlyCharges", "ChurnRiskScore", "RiskLevel"]
    active = active[columns].sort_values("ChurnRiskScore", ascending=False)
    return active, metrics


def main():
    print("Cleaning data...")
    df = clean(pd.read_csv(RAW))
    os.makedirs(PROCESSED, exist_ok=True)
    os.makedirs(RESULTS, exist_ok=True)
    df.to_csv(os.path.join(PROCESSED, "customers_clean.csv"), index=False)

    print("\nScoring churn risk for active customers...")
    active, metrics = score_risk(df)
    active.to_csv(os.path.join(PROCESSED, "active_customer_risk.csv"), index=False)
    with open(os.path.join(RESULTS, "model_metrics.txt"), "w") as f:
        f.write(metrics)
    print(metrics)
    high = active[active["RiskLevel"] == "High"]
    print(f"High-risk active customers: {len(high):,} "
          f"(${high['MonthlyCharges'].sum():,.0f} monthly revenue at risk)")


if __name__ == "__main__":
    main()
