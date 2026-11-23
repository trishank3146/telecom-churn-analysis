-- =====================================================================
-- Telecom Customer Churn - SQL analysis
-- Works in MySQL 8 and SQLite (scripts/run_sql_analysis.py runs them all
-- and saves each result to results/<name>.csv).
-- Each query starts with a "-- name:" line.
-- =====================================================================

-- name: overall_kpis
-- Headline numbers for the dashboard KPI cards
SELECT
    COUNT(*)                                        AS total_customers,
    SUM(ChurnFlag)                                  AS churned_customers,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct,
    ROUND(SUM(MonthlyCharges), 2)                   AS total_monthly_revenue,
    ROUND(SUM(MonthlyRevenueLost), 2)               AS monthly_revenue_lost,
    ROUND(100.0 * SUM(MonthlyRevenueLost) / SUM(MonthlyCharges), 2) AS revenue_lost_pct,
    ROUND(AVG(tenure), 1)                           AS avg_tenure_months
FROM customers;

-- name: churn_by_contract
-- Contract type is usually the strongest churn driver
SELECT
    Contract,
    COUNT(*)                                        AS customers,
    SUM(ChurnFlag)                                  AS churned,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                   AS avg_monthly_charges
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- name: churn_by_tenure_group
SELECT
    TenureGroup,
    COUNT(*)                                        AS customers,
    SUM(ChurnFlag)                                  AS churned,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct
FROM customers
GROUP BY TenureGroup
ORDER BY MIN(tenure);

-- name: churn_by_internet_service
SELECT
    InternetService,
    COUNT(*)                                        AS customers,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct,
    ROUND(AVG(MonthlyCharges), 2)                   AS avg_monthly_charges
FROM customers
GROUP BY InternetService
ORDER BY churn_rate_pct DESC;

-- name: churn_by_payment_method
SELECT
    PaymentMethod,
    COUNT(*)                                        AS customers,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct
FROM customers
GROUP BY PaymentMethod
ORDER BY churn_rate_pct DESC;

-- name: churn_by_charge_band
-- Monthly charges vs churn
SELECT
    ChargeBand,
    COUNT(*)                                        AS customers,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct,
    ROUND(SUM(MonthlyRevenueLost), 2)               AS monthly_revenue_lost
FROM customers
GROUP BY ChargeBand
ORDER BY MIN(MonthlyCharges);

-- name: support_addons_impact
-- Do Tech Support / Online Security add-ons reduce churn? (internet customers only)
SELECT
    HasSupportAddOns,
    COUNT(*)                                        AS customers,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct
FROM customers
WHERE InternetService <> 'No'
GROUP BY HasSupportAddOns;

-- name: senior_citizen_churn
SELECT
    SeniorCitizen,
    COUNT(*)                                        AS customers,
    ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2)     AS churn_rate_pct
FROM customers
GROUP BY SeniorCitizen;

-- name: revenue_at_risk_by_contract
-- Where is the lost monthly revenue coming from?
SELECT
    Contract,
    ROUND(SUM(MonthlyRevenueLost), 2)               AS monthly_revenue_lost,
    ROUND(100.0 * SUM(MonthlyRevenueLost)
          / (SELECT SUM(MonthlyRevenueLost) FROM customers), 2) AS share_of_total_loss_pct
FROM customers
GROUP BY Contract
ORDER BY monthly_revenue_lost DESC;

-- name: high_risk_segments
-- Segments (contract x internet x tenure) with at least 50 customers,
-- ranked by churn rate with a window function
SELECT *
FROM (
    SELECT
        Contract,
        InternetService,
        TenureGroup,
        COUNT(*)                                    AS customers,
        ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2) AS churn_rate_pct,
        ROUND(SUM(MonthlyRevenueLost), 2)           AS monthly_revenue_lost,
        RANK() OVER (ORDER BY 1.0 * SUM(ChurnFlag) / COUNT(*) DESC) AS risk_rank
    FROM customers
    GROUP BY Contract, InternetService, TenureGroup
    HAVING COUNT(*) >= 50
) ranked
WHERE risk_rank <= 10
ORDER BY risk_rank;

-- name: churn_vs_stayed_profile
-- Average profile of customers who left vs stayed
SELECT
    Churn,
    COUNT(*)                                        AS customers,
    ROUND(AVG(tenure), 1)                           AS avg_tenure_months,
    ROUND(AVG(MonthlyCharges), 2)                   AS avg_monthly_charges,
    ROUND(AVG(AddOnServices), 2)                    AS avg_add_on_services,
    ROUND(100.0 * SUM(CASE WHEN Contract = 'Month-to-month' THEN 1 ELSE 0 END) / COUNT(*), 1)
                                                    AS month_to_month_pct
FROM customers
GROUP BY Churn;
