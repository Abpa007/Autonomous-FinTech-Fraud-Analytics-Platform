import os
import joblib
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, roc_auc_score
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "fintech_fraud_db")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("🔌 Connecting to PostgreSQL to extract training features...")
engine = create_engine(DB_URL)

# Extract a representative sample or full dataset for training
query = """
    SELECT 
        t.transaction_id,
        t.amount,
        t.device_type,
        t.is_fraud,
        u.credit_score,
        m.risk_rating
    FROM public_fact_transactions t
    JOIN public_dim_users u ON t.user_id = u.user_id
    JOIN public_dim_merchants m ON t.merchant_id = m.merchant_id
    LIMIT 300000;
"""

df = pd.read_sql(query, engine)
print(f"📊 Extracted {len(df)} records for model training.")

# Feature Engineering
print("⚙️ Engineering behavioral and risk feature vectors...")
df["risk_rating_encoded"] = df["risk_rating"].map({"Low": 1, "Medium": 2, "High": 3, "Critical": 4})
df["device_encoded"] = df["device_type"].astype("category").cat.codes

# Features for Machine Learning
X = df[["amount", "credit_score", "risk_rating_encoded", "device_encoded"]]
y = df["is_fraud"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print("🌲 Training Isolation Forest (Unsupervised Anomaly Detection)...")
iso = IsolationForest(contamination=0.01, random_state=42)
iso.fit(X_train)

print("🚀 Training XGBoost Classifier (Supervised Fraud Scoring)...")
xgb = XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
xgb.fit(X_train, y_train)

# Evaluate
y_pred = xgb.predict(X_test)
y_proba = xgb.predict_proba(X_test)[:, 1]

print("\n📈 Model Evaluation Report:")
print(classification_report(y_test, y_pred))
print(f"🎯 ROC-AUC Score: {roc_auc_score(y_test, y_proba):.4f}")

# Save Model Binaries
os.makedirs("models", exist_ok=True)
joblib.dump(iso, "models/isolation_forest_model.pkl")
joblib.dump(xgb, "models/xgboost_fraud_model.pkl")
print("\n✅ Phase 3 Complete! Models successfully trained and saved to 'models/' folder.")