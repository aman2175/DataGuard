# DataGuard

A small app that shows public GitHub activity for one hour.

You log in, then you can load the busiest repositories and ask three questions: `top repos`, `top actors`, and `how many events`. The data comes from [GitHub Archive](https://www.gharchive.org/), which publishes one gzip file of events per hour. No GitHub API key is required.

This is not a chat product. The question box only accepts those three phrases and runs a SQL query that is already written in the API.

## What is built

1. **Download.** `ingest/download.py` takes the previous finished UTC hour, deletes older `.json.gz` files in `data/raw`, and downloads that hour.
2. **Load.** `ingest/load.py` reads that file and inserts events into Postgres table `raw_data`. The same event is not inserted twice.
3. **Model.** SQL builds the tables the API reads:
   - `sql/stg_events.sql` flattens each event into actor and repo columns
   - `sql/actors.sql` counts events per person
   - `sql/repos.sql` counts events per repository
   - `sql/indexes.sql` speeds up those lookups
   - `sql/quality_checks.sql` checks row counts and null ids
4. **API.** FastAPI in `api/main.py` serves the page and the data. `POST /login` checks the admin user in `.env` and returns a token that expires in 15 minutes. The data routes require that token.
5. **Page.** `api/static/index.html` shows a login screen first. After login it shows the repo table and the question box.
6. **Automatic reload.** `ingest/run_etl.py` runs when the API container starts, before the website. It downloads the previous finished UTC hour, empties `raw_data`, loads that file, then rebuilds `stg_events`, `actors`, `repos`, and the indexes. The page reads those rebuilt tables.
7. **Docker.** `docker-compose.yml` runs Postgres, a small database UI (pgweb), and the API. The API image is built from the `Dockerfile`. The download inside Docker stays in the container. It does not replace `data/raw` on your Mac.

## Architecture

The browser never talks to Postgres. It talks to FastAPI. FastAPI talks to Postgres.

```text
GitHub Archive file
        |
        v
ingest/download.py          save previous UTC hour as .json.gz
        |
        v
ingest/load.py              insert events into raw_data
        |
        v
sql/stg_events.sql          one row per event, with actor and repo columns
        |
        v
sql/actors.sql              count per person
sql/repos.sql               count per repository
        |
        v
api/main.py                 login, /repos/top, /ask
        |
        v
api/static/index.html       login screen, then the table and questions
```

`ingest/run_etl.py` is the runner. When the API container starts, the Dockerfile runs that file and only then starts Uvicorn. The runner uses `subprocess` to start `download.py` and `load.py` as separate programs and waits until each one exits. It then runs the SQL files itself through `psycopg2`.

Docker runs three services: Postgres, pgweb, and the API. The API container has its own disk. A file downloaded there does not replace `data/raw` on the Mac. Inside Docker, the database host name is `postgres`. On the Mac, the same database is `localhost` port `5434`.

## What this project uses

**ELT.** Extract is the download. Load is inserting the raw JSON. Transform is the SQL that builds `stg_events`, `actors`, and `repos`. Transform runs after the load, which is why a new file does not change the page until those SQL files run.

**`timedelta`.** GitHub Archive publishes an hour only after that hour is finished. The download takes the current UTC time and subtracts one hour so it asks for the newest file that exists.

**`subprocess`.** `run_etl.py` does not copy the download and load functions into itself. `subprocess.check_call` runs those Python files and waits. If one fails, the next step does not run.

**Pydantic.** Classes such as `LoginIn` and `RepoOut` describe the JSON. FastAPI checks that the keys and types match. `LoginIn` checks the body coming in. `response_model` checks the JSON going back out. Pydantic does not look at the database.

**JWT.** `POST /login` checks the admin name and password from `.env` once. It returns a signed token that expires in 15 minutes. Later requests send `Authorization: Bearer <token>`. The data routes check that token. They do not ask for the password again.

**The page.** `fetch` calls an API path such as `/login` or `/repos/top`. `JSON.stringify` turns a JavaScript value into the JSON text that is sent. `r.json()` turns the reply text back into a JavaScript value. The login screen stores the token, hides itself, and then shows the table and the question box.

## What is not part of this project

**dbt** is not needed here. The models are normal SQL files. dbt would be a later way to run those same models with tests. It does not add a feature the page is missing.

**Kafka** is not needed here. The source is a file you download once per hour, not a live stream.

**A real AI chat** is not built. The `/ask` route looks the question up in a small list. It does not call a language model.

**Programming language popularity** is not in the data. The hour file gives event type, actor, and repository name. It does not say whether a repo is Python or JavaScript.

## Run it locally

Docker Desktop must be running.

```bash
docker compose up -d --build
```

The first start takes several minutes. The container downloads the hour, loads it, and rebuilds the tables before the site accepts requests. Later starts do that again, so the tables follow the previous UTC hour.

Open `http://127.0.0.1:8000/`. Log in with `ADMIN_USER` and `ADMIN_PASSWORD` from `.env`, then click **Load repos**.

Postgres on your Mac is port **5434**. Inside Docker the API uses host `postgres` and port **5432**. Do not commit `.env` or `data/`.

## Still to do

Deploy the Docker image to a public host. A new hosted database starts empty until `run_etl.py` loads an hour into it. The local app is otherwise complete.
