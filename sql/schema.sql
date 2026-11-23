-- Telecom Customer Churn - MySQL table for the cleaned data
-- Load data/processed/customers_clean.csv into this table (MySQL Workbench:
-- right-click table > Table Data Import Wizard), then run analysis_queries.sql.

CREATE DATABASE IF NOT EXISTS telecom_churn;
USE telecom_churn;

CREATE TABLE IF NOT EXISTS customers (
    customerID          VARCHAR(20)   PRIMARY KEY,
    gender              VARCHAR(10),
    SeniorCitizen       VARCHAR(3),
    Partner             VARCHAR(3),
    Dependents          VARCHAR(3),
    tenure              INT,
    PhoneService        VARCHAR(3),
    MultipleLines       VARCHAR(20),
    InternetService     VARCHAR(20),
    OnlineSecurity      VARCHAR(25),
    OnlineBackup        VARCHAR(25),
    DeviceProtection    VARCHAR(25),
    TechSupport         VARCHAR(25),
    StreamingTV         VARCHAR(25),
    StreamingMovies     VARCHAR(25),
    Contract            VARCHAR(20),
    PaperlessBilling    VARCHAR(3),
    PaymentMethod       VARCHAR(30),
    MonthlyCharges      DECIMAL(8,2),
    TotalCharges        DECIMAL(10,2),
    Churn               VARCHAR(3),
    ChurnFlag           TINYINT,
    TenureGroup         VARCHAR(15),
    ChargeBand          VARCHAR(20),
    AddOnServices       INT,
    HasSupportAddOns    VARCHAR(3),
    AutoPay             VARCHAR(3),
    MonthlyRevenueLost  DECIMAL(8,2),
    INDEX idx_contract (Contract),
    INDEX idx_churn (ChurnFlag)
);
