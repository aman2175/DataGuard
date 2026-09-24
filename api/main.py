import os
from fastapi import FastAPI, HTTPException, Depends
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials# beared --> look for authorization , Depends --> run this function before the next one
from datetime import datetime, timedelta, timezone
import jwt

load_dotenv()

app=FastAPI()
bearer = HTTPBearer()#bearer --> is a test to check is its type is bearer? , if it passes , then it will return the credentials t

def connect_to_db():
    return psycopg2.connect(os.environ["DATABASE_URL"])

class RepoOut(BaseModel):
    repo_name: str
    event_count: int

class ActorOut(BaseModel):
    actor_login: str
    event_count: int

class LoginIn(BaseModel):
    username: str
    password: str

class AskIn(BaseModel):
    question: str
KNOWN = {
    "top repos": "SELECT repo_name, event_count FROM repos ORDER BY event_count DESC LIMIT 10",
    "top actors": "SELECT actor_login, event_count FROM actors ORDER BY event_count DESC LIMIT 10",
    "how many events": "SELECT COUNT(*) AS n FROM stg_events",
}

@app.post("/ask")
def ask(body: AskIn, user: str=Depends(get_current_user)):
    conn=connect_to_db()
    q=body.question.strip().lower()
    sql=KNOWN.get(q)
    if sql is None:
        raise HTTPException(status_code=400, detail="INVALID QUESTION")
    try:
        with conn.cursor() as crs:
            crs.execute(sql)

            return 


    try:


    finally:
        conn.close()


# bearer is a test to check the type of of schema in the header and returns 2 things credentials and scheme type
def get_current_user(cred: HTTPAuthorizationCredentials=Depends(bearer)):
    try: 
        payload=jwt.decode(
            cred.credentials,
            os.environ["JWT_SECRET"],
            algorithms=["HS256"],
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="INVALD TOKEN OR TOKEN IS EXPIRED!")
    return payload["sub"]

@app.get("/repos/top",response_model =list[RepoOut] )
def top_repos(limit: int=10, user: str=Depends(get_current_user)):
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
def top_actors(limit: int=10, user: str=Depends(get_current_user)):
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

@app.get("/actors/{login}", response_model=ActorOut)
def get_actor(login: str, user: str=Depends(get_current_user)):
    conn=connect_to_db()
    try:
        with conn.cursor() as csr:
            csr.execute("""
            SELECT actor_login, event_count
            FROM actors
            WHERE actor_login=%s
            """,
            (login,),

            )
            row=csr.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="actor not found")
            name, n =row
            return {"actor_login": name , "event_count": n}

    finally:
        conn.close()

@app.get("/repos/{name:path}", response_model=RepoOut)
def get_repo(name: str, user=Depends(get_current_user)):
    conn=connect_to_db()
    try:
        with conn.cursor() as csr:
            csr.execute("""
            SELECT repo_name, event_count
            FROM repos
            WHERE repo_name=%s
            """,
            (name,),
        )
            row=csr.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="repo not found")
        name, n= row
        return {"repo_name": name, "event_count": n}
    finally:
        conn.close()

"""
Whole path
They send username + password (body).
You compare to .env.
Wrong → 401.
Right → stamp a pass that says who + expiry → return it. ------>>>>>>>>>
"""
@app.post("/login")
def login(body:LoginIn):
    user=os.environ["ADMIN_USER"]
    password=os.environ["ADMIN_PASSWORD"]
    if body.username!=user or body.password!=password:
        raise HTTPException(status_code=401, detail="INVALID USERNAME OR PASSWORD!!!!!!!!!1")
    token=jwt.encode(
        {
        "sub":body.username,
        "exp":datetime.now(timezone.utc) + timedelta(minutes=15),
        },
    os.environ["JWT_SECRET"],
    algorithm="HS256",
    )
    return {"token":token}

@app.get("/")
def home():
    return FileResponse("api/static/index.html")

    