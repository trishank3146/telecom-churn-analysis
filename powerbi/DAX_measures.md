# Power BI DAX measures

Create these in the **customers** table (Modeling → New measure). The names match the dashboard guide.

```DAX
Total Customers = COUNTROWS ( customers )

Churned Customers = SUM ( customers[ChurnFlag] )

Active Customers = [Total Customers] - [Churned Customers]

Churn Rate % = DIVIDE ( [Churned Customers], [Total Customers], 0 )

Total Monthly Revenue = SUM ( customers[MonthlyCharges] )

Monthly Revenue Lost = SUM ( customers[MonthlyRevenueLost] )

Revenue Lost % = DIVIDE ( [Monthly Revenue Lost], [Total Monthly Revenue], 0 )

Annual Revenue Lost = [Monthly Revenue Lost] * 12

Avg Tenure (Months) = AVERAGE ( customers[tenure] )

Avg Monthly Charges = AVERAGE ( customers[MonthlyCharges] )

-- Churn rate of month-to-month customers, regardless of the contract slicer
Month-to-Month Churn % =
CALCULATE ( [Churn Rate %], customers[Contract] = "Month-to-month" )

-- How much higher than the company average is the current selection?
Churn vs Average (pp) =
[Churn Rate %] - CALCULATE ( [Churn Rate %], ALL ( customers ) )
```

In the **active_customer_risk** table:

```DAX
High Risk Customers =
CALCULATE ( COUNTROWS ( active_customer_risk ), active_customer_risk[RiskLevel] = "High" )

Revenue at Risk (High Risk) =
CALCULATE ( SUM ( active_customer_risk[MonthlyCharges] ), active_customer_risk[RiskLevel] = "High" )

Avg Risk Score = AVERAGE ( active_customer_risk[ChurnRiskScore] )
```

**Formatting:** set `Churn Rate %`, `Revenue Lost %` and `Month-to-Month Churn %` to **Percentage, 1 decimal**, and the revenue measures to **Currency ($), 0 decimals**.

**Sort order:** `TenureGroup` already sorts correctly (0-12, 13-24, 25-48, 49-72). `ChargeBand` would sort alphabetically (High, Low, Medium, Premium), so add this calculated column and use **Column tools → Sort by column → ChargeBandOrder**:

```DAX
ChargeBandOrder =
SWITCH ( customers[ChargeBand],
    "Low (<35)", 1, "Medium (35-70)", 2, "High (70-90)", 3, "Premium (90+)", 4 )
```
