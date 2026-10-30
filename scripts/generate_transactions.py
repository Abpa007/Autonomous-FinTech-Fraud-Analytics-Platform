import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker for realistic data generation
fake = Faker()
Faker.seed(42)
np.random.seed(42)

NUM_USERS = 10000
NUM_MERCHANTS = 500
NUM_TRANSACTIONS = 1000000

print("🚀 Step 1: Generating Dim Users & Dim Merchants...")

# 1. Generate Dimension Users
user_ids = [f"USR_{10000 + i}" for i in range(NUM_USERS)]
countries = ["US", "CA", "UK", "IN", "DE", "FR", "AU", "SG"]
account_types = ["Standard", "Premium", "VIP", "Corporate"]

users_data = {
    "user_id": user_ids,
    "user_name": [fake.name() for _ in range(NUM_USERS)],
    "email": [fake.email() for _ in range(NUM_USERS)],
    "home_country": np.random.choice(countries, NUM_USERS, p=[0.5, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05]),
    "account_type": np.random.choice(account_types, NUM_USERS, p=[0.7, 0.18, 0.02, 0.10]),
    "credit_score": np.random.randint(300, 850, size=NUM_USERS),
    "created_at": [fake.date_between(start_date='-3y', end_date='-1y') for _ in range(NUM_USERS)]
}
df_users = pd.DataFrame(users_data)

# 2. Generate Dimension Merchants
merchant_categories = ["Retail", "Travel", "Gaming", "Crypto Exchange", "Electronics", "Dining", "Wire Transfer", "E-Commerce"]
merchants_data = {
    "merchant_id": [f"MER_{5000 + i}" for i in range(NUM_MERCHANTS)],
    "merchant_name": [fake.company() for _ in range(NUM_MERCHANTS)],
    "category": np.random.choice(merchant_categories, NUM_MERCHANTS, p=[0.25, 0.1, 0.1, 0.05, 0.15, 0.15, 0.05, 0.15]),
    "risk_rating": np.random.choice(["Low", "Medium", "High", "Critical"], NUM_MERCHANTS, p=[0.6, 0.25, 0.1, 0.05])
}
df_merchants = pd.DataFrame(merchants_data)

print("🚀 Step 2: Generating 1,000,000 High-Velocity Transactions...")

# 3. Generate Fact Transactions
start_date = datetime.now() - timedelta(days=90)

random_users = np.random.choice(user_ids, NUM_TRANSACTIONS)
random_merchants = np.random.choice(df_merchants["merchant_id"], NUM_TRANSACTIONS)
amounts = np.round(np.random.exponential(scale=85, size=NUM_TRANSACTIONS) + 5, 2)

# Random timestamps spread across 90 days
timestamps = [start_date + timedelta(seconds=int(s)) for s in np.random.randint(0, 90*24*3600, NUM_TRANSACTIONS)]

device_types = np.random.choice(["Mobile_iOS", "Mobile_Android", "Web_Chrome", "Web_Safari", "API_Bot"], NUM_TRANSACTIONS, p=[0.4, 0.35, 0.15, 0.08, 0.02])
tx_countries = np.random.choice(countries, NUM_TRANSACTIONS, p=[0.5, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.05])

df_tx = pd.DataFrame({
    "transaction_id": [f"TXN_{1000000 + i}" for i in range(NUM_TRANSACTIONS)],
    "user_id": random_users,
    "merchant_id": random_merchants,
    "amount": amounts,
    "timestamp": timestamps,
    "device_type": device_types,
    "location_country": tx_countries,
    "is_fraud": 0  # Default non-fraud
})

# Sort chronologically
df_tx.sort_values(by="timestamp", inplace=True)
df_tx.reset_index(drop=True, inplace=True)

print("🚀 Step 3: Injecting Advanced Synthetic Fraud Topologies...")

# Inject Fraud Pattern 1: High Velocity Spikes & Extreme Amount Outliers
fraud_indices_1 = np.random.choice(df_tx.index, size=int(NUM_TRANSACTIONS * 0.015), replace=False)
df_tx.loc[fraud_indices_1, "amount"] = np.random.uniform(2500, 15000, size=len(fraud_indices_1))
df_tx.loc[fraud_indices_1, "is_fraud"] = 1

# Inject Fraud Pattern 2: API Bot / Crypto High-Risk Merchant Exploits
crypto_merchants = df_merchants[df_merchants["category"].isin(["Crypto Exchange", "Wire Transfer"])]["merchant_id"]
fraud_indices_2 = df_tx[(df_tx["device_type"] == "API_Bot") & (df_tx["merchant_id"].isin(crypto_merchants))].index
df_tx.loc[fraud_indices_2, "is_fraud"] = 1

# Export files
os.makedirs("data", exist_ok=True)
df_users.to_csv("data/dim_users.csv", index=False)
df_merchants.to_csv("data/dim_merchants.csv", index=False)
df_tx.to_csv("data/fact_transactions.csv", index=False)

print("✅ Phase 1 Complete! Data generated successfully in 'data/' folder:")
print(f"   - Users: {len(df_users)} rows")
print(f"   - Merchants: {len(df_merchants)} rows")
print(f"   - Transactions: {len(df_tx)} rows (Total Fraud Cases: {df_tx['is_fraud'].sum()})")