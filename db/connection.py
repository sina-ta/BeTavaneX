from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres:Mahshid88@127.0.0.1:5433/betavanx_db"

engine = create_engine(DATABASE_URL)

connection = engine.connect()

print("✅ Connected to PostgreSQL")