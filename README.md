# github-data-platform

Stage 1 only: download one hour of [GitHub Archive](https://www.gharchive.org/) data, load it into Postgres, query it.

```bash
cp .env.example .env
docker compose up -d
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ingest/download.py
python ingest/load.py
docker compose exec postgres psql -U ghdata -d ghdata -c "SELECT COUNT(*) FROM raw_data;"
```

Do not commit `data/` or `.env`.
