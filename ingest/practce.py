import os
from dotenv import load_dotenv
import gzip
import json
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()
RAW_FILE=Path("data/raw/2026-08-01-15.json.gz")
def load_data(path: Path):
    with gzip.open(path, "rb", encoding="utf-8") as f:
        for i in f:
            event=json.load(i)
            yield(
                event["id"],
                event["type"],
                event["crrated_at"],
                json.dumps(event)
            )

BATCH_SIZE=1000
def load_to_database(path:Path)-> None:
    CREATE_TABLE="""
    CREATE TABLE IF NOT EXISTS raw_data
    (event_id TEXT PRIMARY KEY,
    event_type TEXT,
    created_at TIMESTAMPTZ,
    payload JSONB NOTNULL
    );
    """
    INSERT_DATA="""
    INSERT INTI raw_data(event_id, event_type, created_at, payload)
    VALUES %S
    ON CONFLICT (event_id) DO NOTHING;
    """
    conn=psycopg2.connect(os.environ["DATABASE_URL"])
   try:
    with conn.cursor() as csr:
        csr.execute(CREATE_TABLE)
        batch=[]
        for i in load_data(path):
            batch.append(i)
            if len(batch)>=BATCH_SIZE:
                execute_values(crs, INSERT_DATA, batch)
                batch=[]
            if batch:
                execute_values(csr, INSERT_DATA, batch)
        conn.commit()
    finally:
        conn.close()
