-- Create a unified analytical view for Power BI and Executive Dashboards
DROP VIEW IF EXISTS vw_fraud_analytics;

CREATE VIEW vw_fraud_analytics AS
SELECT 
    t.transaction_id,
    t.amount,
    t.timestamp,
    DATE_TRUNC('day', t.timestamp) AS transaction_date,
    t.device_type,
    t.location_country,
    t.is_fraud,
    u.user_id,
    u.user_name,
    u.account_type,
    u.credit_score,
    m.merchant_id,
    m.merchant_name,
    m.category AS merchant_category,
    m.risk_rating AS merchant_risk_rating,
    CASE 
        WHEN t.is_fraud = 1 THEN 'Fraudulent'
        ELSE 'Legitimate'
    END AS fraud_status_label,
    CASE 
        WHEN t.amount > 5000 THEN 'High Value (> $5K)'
        WHEN t.amount > 1000 THEN 'Medium Value ($1K-$5K)'
        ELSE 'Standard Value (< $1K)'
    END AS amount_tier
FROM public_fact_transactions t
JOIN public_dim_users u ON t.user_id = u.user_id
JOIN public_dim_merchants m ON t.merchant_id = m.merchant_id;