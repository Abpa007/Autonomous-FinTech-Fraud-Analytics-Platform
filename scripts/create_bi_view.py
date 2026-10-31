import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

print("📊 Creating Power BI analytical view in PostgreSQL...")
engine = create_engine(DB_URL)

with open("sql/bi_views.sql", "r") as f:
    sql_view = f.read()

with engine.begin() as conn:
    conn.execute(text(sql_view))

print("✅ Analytical view `vw_fraud_analytics` created successfully!")