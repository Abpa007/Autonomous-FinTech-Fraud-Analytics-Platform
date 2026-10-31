import os
import joblib
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "fintech_fraud_db")
DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("🤖 Initializing Autonomous AI Forensic Squad...")

class FraudForensicSquad:
    def __init__(self):
        self.engine = create_engine(DB_URL)
        # Load trained ML models
        try:
            self.xgb_model = joblib.load("models/xgboost_fraud_model.pkl")
            self.iso_model = joblib.load("models/isolation_forest_model.pkl")
            print("✅ ML Models loaded successfully into AI Forensic Squad.")
        except Exception as e:
            print(f"⚠️ Warning: Could not load model binaries ({e}). Train models via Phase 3 first.")

    def sql_analyst_agent(self, transaction_id: str):
        """Agent 1: Pulls raw transaction telemetry from PostgreSQL Star Schema"""
        print(f"\n🔍 [Agent 1: SQL Analyst] Querying database for transaction {transaction_id}...")
        query = text("""
            SELECT 
                t.transaction_id,
                t.amount,
                t.timestamp,
                t.device_type,
                t.location_country,
                u.user_id,
                u.user_name,
                u.home_country,
                u.account_type,
                u.credit_score,
                m.merchant_id,
                m.merchant_name,
                m.category,
                m.risk_rating
            FROM public_fact_transactions t
            JOIN public_dim_users u ON t.user_id = u.user_id
            JOIN public_dim_merchants m ON t.merchant_id = m.merchant_id
            WHERE t.transaction_id = :tx_id;
        """)
        
        with self.engine.connect() as conn:
            result = conn.execute(query, {"tx_id": transaction_id}).fetchone()
            
        if not result:
            return None
            
        # Convert row to dictionary
        tx_data = dict(result._mapping)
        print(f"   --> Found transaction! User: {tx_data['user_name']} | Amount: ${tx_data['amount']} | Merchant: {tx_data['merchant_name']}")
        return tx_data

    def ml_risk_investigator_agent(self, tx_data: dict):
        """Agent 2: Evaluates transaction vector through XGBoost and Isolation Forest"""
        print("🧠 [Agent 2: ML Risk Investigator] Analyzing feature vector through anomaly detection models...")
        
        risk_map = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        device_codes = {"Mobile_iOS": 0, "Mobile_Android": 1, "Web_Chrome": 2, "Web_Safari": 3, "API_Bot": 4}
        
        # Explicitly cast to float and int to avoid pandas object dtypes
        amount = float(tx_data["amount"])
        credit_score = int(tx_data["credit_score"])
        risk_encoded = int(risk_map.get(tx_data["risk_rating"], 1))
        device_encoded = int(device_codes.get(tx_data["device_type"], 0))
        
        features = pd.DataFrame([[amount, credit_score, risk_encoded, device_encoded]], 
                                columns=["amount", "credit_score", "risk_rating_encoded", "device_encoded"])
        
        # Predict probability
        fraud_proba = float(self.xgb_model.predict_proba(features)[0][1])
        anomaly_score = float(self.iso_model.decision_function(features)[0])
        is_anomaly = anomaly_score < 0
        
        print(f"   --> XGBoost Fraud Probability: {fraud_proba * 100:.2f}%")
        print(f"   --> Isolation Forest Anomaly Status: {'OUTLIER DETECTED' if is_anomaly else 'Normal'}")
        
        return {
            "fraud_probability": fraud_proba,
            "anomaly_score": anomaly_score,
            "is_anomaly": is_anomaly
        }

    def executive_reporter_agent(self, tx_data: dict, risk_analysis: dict):
        """Agent 3: Generates automated forensic audit report"""
        print("📝 [Agent 3: Executive Reporter] Compiling forensic audit report...")
        
        proba = risk_analysis["fraud_probability"]
        risk_tier = "CRITICAL RISK" if proba > 0.75 else "MEDIUM RISK" if proba > 0.3 else "LOW RISK"
        action = "IMMEDIATE ACCOUNT FREEZE & MANUAL REVIEW" if proba > 0.75 else "STANDARD MONITORING"
        
        report = f"""
==================================================
        AI FORENSIC AUDIT & FRAUD REPORT
==================================================
TRANSACTION ID : {tx_data['transaction_id']}
TIMESTAMP      : {tx_data['timestamp']}
--------------------------------------------------
CUSTOMER INFO  : {tx_data['user_name']} (ID: {tx_data['user_id']})
ACCOUNT TYPE   : {tx_data['account_type']} | Credit Score: {tx_data['credit_score']}
LOCATION       : Home ({tx_data['home_country']}) vs Tx ({tx_data['location_country']})
--------------------------------------------------
MERCHANT INFO  : {tx_data['merchant_name']} ({tx_data['category']})
MERCHANT RISK  : {tx_data['risk_rating']} Risk Rating
TRANSACTION    : ${tx_data['amount']} via {tx_data['device_type']}
--------------------------------------------------
ML ASSESSMENT  :
- Fraud Probability Score : {proba * 100:.2f}%
- Isolation Forest Status : {'Anomaly Outlier' if risk_analysis['is_anomaly'] else 'Normal Pattern'}
- Risk Classification     : {risk_tier}
--------------------------------------------------
RECOMMENDED ACTION: {action}
==================================================
        """
        return report

    def investigate_transaction(self, transaction_id: str):
        tx_data = self.sql_analyst_agent(transaction_id)
        if not tx_data:
            return f"Transaction {transaction_id} not found in database."
        
        risk_analysis = self.ml_risk_investigator_agent(tx_data)
        audit_report = self.executive_reporter_agent(tx_data, risk_analysis)
        return audit_report

if __name__ == "__main__":
    squad = FraudForensicSquad()
    
    query = text("SELECT transaction_id FROM public_fact_transactions WHERE is_fraud = 1 LIMIT 1;")
    with squad.engine.connect() as conn:
        sample_tx = conn.execute(query).scalar()
        
    if sample_tx:
        print(f"\n🚀 Running Autonomous Forensic Investigation on Flagged Transaction: {sample_tx}")
        report = squad.investigate_transaction(sample_tx)
        print(report)
    else:
        print("No flagged transactions found to investigate.")