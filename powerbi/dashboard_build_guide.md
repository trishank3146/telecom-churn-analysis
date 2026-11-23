# Building the Power BI dashboard

**Data file:** `data/processed/churn_powerbi.xlsx` (2 sheets: `customers` and `active_customer_risk`).
The same data is also in the two CSV files in `data/processed/`.

> **Mac users:** Power BI Desktop runs on Windows only. Use a Windows PC (for example a college lab), a Windows virtual machine, or **Power BI Service** in the browser (app.powerbi.com → *New report* → upload the Excel file). The steps below are for Power BI Desktop.

## 1. Load the data

1. **Home → Get data → Excel workbook** → select `churn_powerbi.xlsx`.
2. Tick both sheets, `customers` and `active_customer_risk`, then click **Load**.
3. **Model view:** connect `customers[customerID]` → `active_customer_risk[customerID]` (one-to-one).
4. Create the measures in `DAX_measures.md`.

## 2. Page 1: "Churn Overview"

| Area | Visual | Fields |
|---|---|---|
| Top row | 4 × **Card** | `Total Customers`, `Churn Rate %`, `Monthly Revenue Lost`, `Avg Tenure (Months)` |
| Middle left | **Clustered column chart** | X: `Contract`, Y: `Churn Rate %` |
| Middle right | **Column chart** | X: `TenureGroup`, Y: `Churn Rate %` |
| Bottom left | **Donut chart** | Legend: `InternetService`, Values: `Churned Customers` |
| Bottom right | **Bar chart** | Y: `PaymentMethod`, X: `Churn Rate %` |
| Left side | **Slicers** | `Contract`, `InternetService`, `SeniorCitizen`, `gender` |

Tip: turn on **data labels** for every chart, and colour churn visuals red so the message is obvious.

## 3. Page 2: "Revenue at Risk & Segments"

| Area | Visual | Fields |
|---|---|---|
| Top row | 3 × **Card** | `Monthly Revenue Lost`, `Annual Revenue Lost`, `Revenue at Risk (High Risk)` |
| Left | **Stacked column chart** | X: `ChargeBand` (sorted by `ChargeBandOrder`), Y: `Monthly Revenue Lost` |
| Right | **Matrix** | Rows: `Contract`, `InternetService`; Columns: `TenureGroup`; Values: `Churn Rate %`. Use **conditional formatting → background colour** (white → red) to create a heat map of high-risk segments. |
| Bottom | **Table** | From `active_customer_risk`: `customerID`, `Contract`, `tenure`, `InternetService`, `MonthlyCharges`, `ChurnRiskScore`, `RiskLevel`. Filter `RiskLevel = High`, sort by `ChurnRiskScore` descending. This is the retention team's call list. |

## 4. Page 3: "Customer Profile" (optional)

- **Clustered column chart:** `HasSupportAddOns` vs `Churn Rate %` (filter `InternetService` ≠ "No")
- **Column chart:** `AddOnServices` vs `Churn Rate %`
- **Card:** `Churn vs Average (pp)`, which changes as slicers are used

## 5. Finish

- Add a title text box and the company/project name on each page.
- **File → Save as** `telecom_churn_dashboard.pbix` and commit it to this folder (`powerbi/`).
- Take a screenshot of each page for the README.
