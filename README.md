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
6. **Docker.** `docker-compose.yml` runs Postgres, a small database UI (pgweb), and the API. The API image is built from the `Dockerfile`.

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

Open `http://127.0.0.1:8000/`. Log in with `ADMIN_USER` and `ADMIN_PASSWORD` from `.env`.

To refresh the hour and rebuild the tables, from the project folder with the virtualenv on:

```bash
source .venv/bin/activate
python ingest/download.py
python ingest/load.py
docker compose exec -T postgres psql -U ghdata -d ghdata -c "TRUNCATE raw_data;"
```

Run the truncate **before** `load.py` if you want the database to contain only the new hour. Then rebuild the models:

```bash
docker compose exec -T postgres psql -U ghdata -d ghdata < sql/stg_events.sql
docker compose exec -T postgres psql -U ghdata -d ghdata < sql/actors.sql
docker compose exec -T postgres psql -U ghdata -d ghdata < sql/repos.sql
docker compose exec -T postgres psql -U ghdata -d ghdata < sql/indexes.sql
```

Postgres on your Mac is port **5434**. Inside Docker the API uses host `postgres` and port **5432**. Do not commit `.env` or `data/`.

## Still to do

- Run download, load, and the SQL rebuild automatically when the API container starts, instead of running those commands by hand.
- Deploy the Docker image to a public host and load the hour into that host's database. A new hosted database starts empty.
- Keep the README matched to the app when those two are done.
