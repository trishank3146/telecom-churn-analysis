"""
Step 5 - Export the cleaned data to one Excel file for Power BI.

Output: data/processed/churn_powerbi.xlsx  (sheets: customers, active_customer_risk)
Usage:  python scripts/export_powerbi.py
"""

import os

import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
PROCESSED = os.path.join(ROOT, "data", "processed")


def main():
    customers = pd.read_csv(os.path.join(PROCESSED, "customers_clean.csv"))
    risk = pd.read_csv(os.path.join(PROCESSED, "active_customer_risk.csv"))
    out = os.path.join(PROCESSED, "churn_powerbi.xlsx")
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        customers.to_excel(writer, sheet_name="customers", index=False)
        risk.to_excel(writer, sheet_name="active_customer_risk", index=False)
    print(f"Saved {os.path.normpath(out)}")


if __name__ == "__main__":
    main()
