import os
from fastapi import FastAPI
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel

load_dotenv()

app=FastAPI()

def connect_to_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

class RepoOut(BaseModel):
    repo_name: str
    event_count: int
class ActorOut(BaseModel):
    actor_login: str
    event_count: int

@app.get("/repos/top",response_model =list[RepoOut] )
def top_repos(limit: int=10):
    conn=connect_to_db()
    try:
        with conn.cursor() as csr:
            csr.execute(
                """
                SELECT  repo_name,event_count
                FROM repos
                ORDER BY event_count DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows=csr.fetchall()
            return [{"repo_name":name, "event_count":n} for name,n in rows]
    finally:
        conn.close()

@app.get("/actors/top", response_model =list[ActorOut])
def top_actors( limit: int=10):
    conn=connect_to_db()
    try:
        with conn.cursor() as csr:
            csr.execute(
                """
                SELECT actor_login, event_count
                FROM actors
                ORDER BY event_count DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows=csr.fetchall()
            return [{"actor_login": log, "event_count":n} for log , n in rows]

    finally:
        conn.close()

