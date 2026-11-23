"""
Checks the data cleaning, SQL analysis and risk model.
Run from the project folder:  python -m pytest -v
"""

import os
import sqlite3
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from clean_data import RAW, clean, score_risk  # noqa: E402
from run_sql_analysis import SQL_FILE, load_queries  # noqa: E402


@pytest.fixture(scope="module")
def raw():
    return pd.read_csv(RAW)


@pytest.fixture(scope="module")
def cleaned(raw):
    return clean(raw)


@pytest.fixture(scope="module")
def db(cleaned):
    conn = sqlite3.connect(":memory:")
    cleaned.to_sql("customers", conn, index=False)
    yield conn
    conn.close()


def test_raw_dataset_shape(raw):
    assert len(raw) >= 7000
    assert raw["customerID"].is_unique
    assert set(raw["Churn"].unique()) == {"Yes", "No"}


def test_total_charges_cleaned(raw, cleaned):
    blanks = (raw["TotalCharges"].astype(str).str.strip() == "").sum()
    assert blanks > 0                                   # the raw file really has blanks
    assert cleaned["TotalCharges"].dtype == float
    assert cleaned["TotalCharges"].isna().sum() == 0
    assert (cleaned.loc[cleaned["tenure"] == 0, "TotalCharges"] == 0).all()


def test_derived_columns(cleaned):
    assert set(cleaned["SeniorCitizen"].unique()) <= {"Yes", "No"}
    assert cleaned["ChurnFlag"].sum() == (cleaned["Churn"] == "Yes").sum()
    assert cleaned["TenureGroup"].isna().sum() == 0
    assert cleaned["ChargeBand"].isna().sum() == 0
    # Revenue lost only counts customers who churned
    assert (cleaned.loc[cleaned["ChurnFlag"] == 0, "MonthlyRevenueLost"] == 0).all()
    churned = cleaned[cleaned["ChurnFlag"] == 1]
    assert (churned["MonthlyRevenueLost"] == churned["MonthlyCharges"]).all()


def test_all_sql_queries_run(db):
    queries = load_queries(SQL_FILE)
    assert len(queries) == 11
    for name, sql in queries.items():
        result = pd.read_sql_query(sql, db)
        assert len(result) > 0, f"{name} returned no rows"


def test_sql_churn_rate_matches_pandas(db, cleaned):
    kpis = pd.read_sql_query(load_queries(SQL_FILE)["overall_kpis"], db).iloc[0]
    assert kpis["total_customers"] == len(cleaned)
    assert kpis["churn_rate_pct"] == pytest.approx(cleaned["ChurnFlag"].mean() * 100, abs=0.01)


def test_contract_is_a_churn_driver(db):
    by_contract = pd.read_sql_query(load_queries(SQL_FILE)["churn_by_contract"], db)
    rates = dict(zip(by_contract["Contract"], by_contract["churn_rate_pct"]))
    assert rates["Month-to-month"] > rates["One year"] > rates["Two year"]


def test_high_risk_segments_ranked(db):
    segments = pd.read_sql_query(load_queries(SQL_FILE)["high_risk_segments"], db)
    assert (segments["customers"] >= 50).all()
    assert segments["churn_rate_pct"].is_monotonic_decreasing


def test_risk_model(cleaned):
    active, metrics = score_risk(cleaned)
    assert len(active) == (cleaned["ChurnFlag"] == 0).sum()      # only active customers are scored
    assert active["ChurnRiskScore"].between(0, 1).all()
    assert set(active["RiskLevel"].astype(str).unique()) <= {"Low", "Medium", "High"}
    auc = float(metrics.split("ROC-AUC: ")[1].split()[0])
    assert auc > 0.75
