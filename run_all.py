"""Runs the whole analysis pipeline in order.   Usage:  python run_all.py"""

import os
import runpy

STEPS = ["generate_data", "clean_data", "run_sql_analysis", "make_charts", "export_powerbi"]
HERE = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    for step in STEPS:
        print(f"\n######## {step} ########")
        runpy.run_path(os.path.join(HERE, "scripts", f"{step}.py"), run_name="__main__")
    print("\nDone. Open reports/dashboard_preview.png, or load data/processed/churn_powerbi.xlsx in Power BI.")
