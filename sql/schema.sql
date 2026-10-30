-- Drop tables if they exist
DROP TABLE IF EXISTS public_fact_transactions;
DROP TABLE IF EXISTS public_dim_merchants;
DROP TABLE IF EXISTS public_dim_users;

-- 1. Create Dimension Users Table
CREATE TABLE public_dim_users (
    user_id VARCHAR(50) PRIMARY KEY,
    user_name VARCHAR(100),
    email VARCHAR(100),
    home_country VARCHAR(10),
    account_type VARCHAR(20),
    credit_score INT,
    created_at DATE
);

-- 2. Create Dimension Merchants Table
CREATE TABLE public_dim_merchants (
    merchant_id VARCHAR(50) PRIMARY KEY,
    merchant_name VARCHAR(100),
    category VARCHAR(50),
    risk_rating VARCHAR(20)
);

-- 3. Create Fact Transactions Table
CREATE TABLE public_fact_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES public_dim_users(user_id),
    merchant_id VARCHAR(50) REFERENCES public_dim_merchants(merchant_id),
    amount NUMERIC(12, 2),
    timestamp TIMESTAMP,
    device_type VARCHAR(30),
    location_country VARCHAR(10),
    is_fraud INT
);

-- High-performance indexes for analytical aggregations and agent SQL lookups
CREATE INDEX idx_tx_user ON public_fact_transactions(user_id);
CREATE INDEX idx_tx_merchant ON public_fact_transactions(merchant_id);
CREATE INDEX idx_tx_timestamp ON public_fact_transactions(timestamp);
CREATE INDEX idx_tx_fraud ON public_fact_transactions(is_fraud);