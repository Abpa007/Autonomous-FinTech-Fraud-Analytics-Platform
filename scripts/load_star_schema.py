import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "fintech_fraud_db")

def create_database():
    print("🐘 Connecting to PostgreSQL server...")
    conn = psycopg2.connect(user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
    exists = cursor.fetchone()
    if not exists:
        print(f"📦 Creating database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
    else:
        print(f"📦 Database '{DB_NAME}' already exists.")
        
    cursor.close()
    conn.close()

def execute_sql_schema(engine):
    print("🛠️ Executing Star Schema DDL (`sql/schema.sql`)...")
    with open("sql/schema.sql", "r") as f:
        sql_ddl = f.read()
    
    # Use engine.begin() and wrap SQL in text() for SQLAlchemy 2.0 compatibility
    with engine.begin() as connection:
        connection.execute(text(sql_ddl))
    print("✅ Tables and indexes created successfully!")

def load_data(engine):
    print("📥 Ingesting `dim_users`...")
    df_users = pd.read_csv("data/dim_users.csv")
    df_users.to_sql("public_dim_users", engine, if_exists="append", index=False)

    print("📥 Ingesting `dim_merchants`...")
    df_merchants = pd.read_csv("data/dim_merchants.csv")
    df_merchants.to_sql("public_dim_merchants", engine, if_exists="append", index=False)

    print("📥 Ingesting 1,000,000 records into `fact_transactions` (Batch mode)...")
    chunksize = 100000
    for chunk in pd.read_csv("data/fact_transactions.csv", chunksize=chunksize):
        chunk.to_sql("public_fact_transactions", engine, if_exists="append", index=False)
        print(f"   --> Ingested chunk of {len(chunk)} rows")

if __name__ == "__main__":
    create_database()
    
    # SQLAlchemy connection string explicitly using psycopg2 driver
    db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)
    
    execute_sql_schema(engine)
    load_data(engine)
    
    print("\n🎉 Phase 2 Complete! 1 Million rows loaded into PostgreSQL Star Schema successfully!")