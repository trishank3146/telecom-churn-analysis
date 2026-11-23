"""
Generates the raw telecom customer dataset (7,043 customers).

The columns follow the public "IBM Telco Customer Churn" sample schema, so the
analysis scripts work unchanged on that real dataset too (download it from
Kaggle and save it as data/raw/telco_customer_churn.csv).

Churn is simulated from realistic drivers: contract type, tenure, internet
service, payment method, support add-ons, senior status and monthly charges.
Like the original file, TotalCharges is blank for brand-new customers
(tenure = 0), which the cleaning step has to handle.

Usage:  python scripts/generate_data.py
"""

import os

import numpy as np
import pandas as pd

N_CUSTOMERS = 7043
SEED = 7
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "telco_customer_churn.csv")


def generate(n: int = N_CUSTOMERS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    def pick(options, probs, size=n):
        return rng.choice(options, size=size, p=probs)

    df = pd.DataFrame({
        "customerID": [f"{rng.integers(1000, 9999)}-{''.join(rng.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 5))}"
                       for _ in range(n)],
        "gender": pick(["Male", "Female"], [0.505, 0.495]),
        "SeniorCitizen": pick([0, 1], [0.84, 0.16]),
        "Partner": pick(["Yes", "No"], [0.48, 0.52]),
    })
    df["Dependents"] = np.where(df["Partner"] == "Yes", pick(["Yes", "No"], [0.52, 0.48]),
                                pick(["Yes", "No"], [0.10, 0.90]))

    df["Contract"] = pick(["Month-to-month", "One year", "Two year"], [0.55, 0.21, 0.24])
    # Longer contracts go with longer tenure
    base_tenure = {"Month-to-month": 18, "One year": 42, "Two year": 57}
    df["tenure"] = [int(np.clip(rng.normal(base_tenure[c], 17), 1, 72)) for c in df["Contract"]]
    df.loc[rng.choice(n, 11, replace=False), "tenure"] = 0       # 11 brand-new customers

    df["PhoneService"] = pick(["Yes", "No"], [0.90, 0.10])
    df["MultipleLines"] = np.where(df["PhoneService"] == "No", "No phone service",
                                   pick(["Yes", "No"], [0.47, 0.53]))
    df["InternetService"] = pick(["Fiber optic", "DSL", "No"], [0.44, 0.34, 0.22])

    addons = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
              "StreamingTV", "StreamingMovies"]
    addon_rate = {"OnlineSecurity": 0.37, "OnlineBackup": 0.44, "DeviceProtection": 0.44,
                  "TechSupport": 0.37, "StreamingTV": 0.49, "StreamingMovies": 0.50}
    for col in addons:
        df[col] = np.where(df["InternetService"] == "No", "No internet service",
                           pick(["Yes", "No"], [addon_rate[col], 1 - addon_rate[col]]))

    df["PaperlessBilling"] = pick(["Yes", "No"], [0.59, 0.41])
    df["PaymentMethod"] = pick(
        ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
        [0.34, 0.23, 0.22, 0.21])

    # Monthly charges built from the services each customer has
    charges = np.full(n, 18.0)
    charges += np.where(df["PhoneService"] == "Yes", 2.0, 0)
    charges += np.where(df["MultipleLines"] == "Yes", 5.0, 0)
    charges += df["InternetService"].map({"Fiber optic": 50.0, "DSL": 27.0, "No": 0.0}).to_numpy()
    for col, price in zip(addons, [5, 5, 5, 5, 10, 10]):
        charges += np.where(df[col] == "Yes", price, 0)
    charges += rng.normal(0, 2.5, n)
    df["MonthlyCharges"] = np.round(np.clip(charges, 18.25, 118.75), 2)

    total = df["MonthlyCharges"] * df["tenure"] * rng.uniform(0.96, 1.04, n)
    df["TotalCharges"] = [f"{t:.2f}" if ten > 0 else " " for t, ten in zip(total, df["tenure"])]

    # ---- churn probability from realistic drivers (log-odds) ----
    z = np.full(n, -2.95)
    z += df["Contract"].map({"Month-to-month": 1.25, "One year": -0.35, "Two year": -1.6}).to_numpy()
    z += np.where(df["tenure"] <= 6, 0.9, np.where(df["tenure"] <= 12, 0.45,
                  np.where(df["tenure"] >= 48, -0.6, 0)))
    z += df["InternetService"].map({"Fiber optic": 0.75, "DSL": -0.1, "No": -0.9}).to_numpy()
    z += np.where(df["PaymentMethod"] == "Electronic check", 0.7, 0)
    z += np.where(df["TechSupport"] == "No", 0.65, 0)
    z += np.where(df["OnlineSecurity"] == "No", 0.5, 0)
    z += np.where(df["SeniorCitizen"] == 1, 0.3, 0)
    z += np.where(df["PaperlessBilling"] == "Yes", 0.2, 0)
    z += np.where(df["Dependents"] == "Yes", -0.2, 0)
    z += (df["MonthlyCharges"].to_numpy() - 65) / 100
    probability = 1 / (1 + np.exp(-z))
    df["Churn"] = np.where(rng.random(n) < probability, "Yes", "No")

    columns = ["customerID", "gender", "SeniorCitizen", "Partner", "Dependents", "tenure",
               "PhoneService", "MultipleLines", "InternetService", *addons, "Contract",
               "PaperlessBilling", "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"]
    return df[columns]


def main():
    df = generate()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df):,} customers to {os.path.normpath(OUT_PATH)}")
    print(f"Churn rate: {(df['Churn'] == 'Yes').mean():.1%}")


if __name__ == "__main__":
    main()
