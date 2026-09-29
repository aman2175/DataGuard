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
