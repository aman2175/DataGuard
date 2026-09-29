import os
from pathlib import Path 
import psycopg2 # for database connection
import subprocess # for running commands
from dotenv import load_dotenv # for loading environment variables

load_dotenv()# load the environment variables from the .env file

SQL_FILES = [
    "sql/stg_events.sql",
    "sql/actors.sql",
    "sql/indexes.sql",
    "sql/repos.sql",
]

def run_sql(path):
    conn=psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        text= Path(path).read_text()
        with conn.cursor() as con:
            for i in text.split(";"):
                i=i.strip()
                if i:
                    con.execute(i)
        conn.commit()
    finally:
        conn.close()

def main():
    subprocess.check_call(["python", "ingest/download.py"])
    conn=psycopg2.connect(os.environ["DATABASE_URL"])
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE raw_data")
        conn.commit()
    finally:
        conn.close()
    subprocess.check_call(["python", "ingest/load.py"])
    for i in SQL_FILES:
        run_sql(i)
if __name__ ==  "__main__":
    main()    