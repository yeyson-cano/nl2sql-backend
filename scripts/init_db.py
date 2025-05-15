import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def init_db():
    db_params = {
        'dbname': os.getenv("POSTGRES_DB"),
        'user': os.getenv("POSTGRES_USER"),
        'password': os.getenv("POSTGRES_PASSWORD"),
        'host': os.getenv("POSTGRES_HOST", "localhost"),
        'port': os.getenv("POSTGRES_PORT", "5432")
    }

    with psycopg2.connect(**db_params) as conn:
        with conn.cursor() as cur:
            with open("scripts/create_schema.sql", "r") as f:
                cur.execute(f.read())
            print("Schema created.")

            # Insertar algunos datos de prueba
            cur.executemany(
                "INSERT INTO employees (name, department, salary) VALUES (%s, %s, %s);",
                [
                    ("Alice", "HR", 50000),
                    ("Bob", "Engineering", 80000),
                    ("Charlie", "Sales", 60000),
                ]
            )
            print("Data inserted.")
        conn.commit()

if __name__ == "__main__":
    init_db()
