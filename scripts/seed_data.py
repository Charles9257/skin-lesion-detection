import psycopg2
import os
from faker import Faker

fake = Faker()

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "skin_lesion_db"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "postgres"),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", 5432)
)
cur = conn.cursor()

for _ in range(10):
    cur.execute("INSERT INTO feedback (rating, comments) VALUES (%s, %s)",
                (fake.random_int(min=1, max=5), fake.sentence()))

conn.commit()
cur.close()
conn.close()
print("Seed data inserted ✅")
