import psycopg2
import pandas as pd
import os

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "skin_lesion_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432)
)

df = pd.read_sql("SELECT * FROM feedback", conn)
df.to_csv("exported_feedback.csv", index=False)
print("Feedback exported to exported_feedback.csv ✅")

conn.close()
