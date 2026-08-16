# DataGuard

Multi-tenant data reliability and observability control plane.

DataGuard monitors data pipelines, datasets, and upstream systems for freshness failures, volume anomalies, schema drift, and data-quality violations — including silent failures where pipeline orchestrators report success but data is late, incomplete, or structurally broken.

It does not replicate production data. It collects operational metadata, execution signals, schema snapshots, statistical metrics, and check results, then drives incidents with evidence, severity scoring, downstream impact analysis via lineage, and team alerting.

---

## Problem

Large organizations run hundreds of pipelines across databases, warehouses, object storage, event streams, APIs, and orchestrators. When data breaks silently:

- Pipeline logs show **success**, but row counts dropped 90%.
- A column was renamed upstream; downstream models fail hours later.
- A daily table misses its SLA; finance dashboards show stale numbers.
- Nobody knows which dashboards, APIs, or ML models are affected.
- Nobody knows who owns the broken dataset or how severe the incident is.

Log monitoring catches crashes. DataGuard catches **data problems** — and maps their blast radius.

---

## Architecture

```
Control Plane (API)         Data Plane (Workers)
┌─────────────────┐        ┌──────────────────────────┐
│ Auth / RBAC     │        │ Check runners            │
│ Orgs / Envs     │        │ Metric collectors        │
│ Catalog / Rules │        │ Baseline / ML inference   │
│ Incidents       │        │ Alert delivery            │
│ Lineage reads   │        │ Model training (async)    │
└────────┬────────┘        └────────────┬─────────────┘
         │                              │
         ▼                              ▼
   PostgreSQL                    Customer sources
   (metadata, config,           (read-only queries,
    runs, metrics,               webhooks, events)
    incidents, models)
                                 Object storage
                                 (logs, artifacts,
                                  model files)
```

**Key principle:** the API stays fast and stateless; all heavy work (source queries, statistical checks, ML inference, alerting) runs asynchronously in workers.

---

## Detection Layers

DataGuard applies the simplest effective method first and escalates only when data justifies it.

| Layer | Method | Example |
|-------|--------|---------|
| 1 — Deterministic rules | Threshold / schema diff | Column removed, null % > limit, pipeline failed |
| 2 — Statistical baselines | Rolling median, MAD, IQR, robust z-score | Volume 80% below 30-day median |
| 3 — Time-series forecasting | LightGBM quantile regression | Seasonal weekday/weekend pattern, predicted range vs actual |
| 4 — Multivariate anomaly | Isolation Forest | Row count slightly low + runtime up + nulls up — together abnormal |
| 5 — Change-point detection | CUSUM, Page-Hinkley, ruptures | Permanent baseline shift after deployment |
| 6 — Distribution drift | KS test, PSI, Wasserstein, JS divergence | Column values shifted even though row count is normal |

Models are never the first line of defense. Rules and baselines must work before ML is introduced, and every ML output must include explainable evidence (feature importance, SHAP, expected-vs-actual range).

---

## Monitoring Capabilities

- **Freshness** — dataset not updated within its expected window
- **Volume** — row/event/file count anomalies vs historical baselines
- **Schema** — column additions, removals, type changes, nullable changes; classified as compatible, risky, or breaking
- **Data quality** — null %, duplicates, uniqueness, accepted values, ranges, patterns, referential integrity, custom SQL
- **Pipeline reliability** — success/failure/retry rates, runtime duration, error categories, dependency failures
- **Distribution** — min/max, mean/median, std dev, percentiles, cardinality, category frequencies
- **SLO tracking** — freshness deadlines, quality score thresholds, success rate targets, acknowledgement time

---

## Incident Management

When checks fail, DataGuard creates incidents with:

- Severity scoring (environment, downstream count, business criticality, recurrence, data sensitivity)
- Evidence (failed checks, metric diffs, schema changes, historical comparisons)
- Lineage-based impact analysis (affected dashboards, APIs, ML models, customer-facing systems)
- Lifecycle tracking (open → acknowledged → investigating → resolved → reopened)
- Deduplication and suppression during maintenance windows
- Alerting via Slack, email, webhooks, or incident-management integrations
- Similar-incident retrieval (embeddings + vector search) for faster resolution

---

## Tech Stack

| Layer | Technology | Role |
|-------|-----------|------|
| API | FastAPI | Control-plane HTTP service |
| Database | PostgreSQL 16 | Transactional metadata, config, incidents, model registry |
| Migrations | Alembic | Versioned schema changes |
| Validation | Pydantic v2 | Request/response schemas, settings |
| Workers | Celery / Dramatiq (planned) | Async check execution, alerting, training |
| Cache / locks | Redis (planned) | Rate limiting, distributed locks, hot metadata |
| Event ingestion | Kafka (when volume justifies) | High-throughput pipeline events |
| ML — forecasting | LightGBM | Quantile regression on time-series metrics |
| ML — anomaly | Isolation Forest | Multivariate anomaly scoring |
| ML — similarity | Sentence embeddings + pgvector | Incident similarity search |
| LLM | Optional (GPT / Ollama) | Incident summaries, investigation suggestions — never source of truth |
| Observability | OpenTelemetry, Prometheus | Traces, metrics, structured logs on DataGuard itself |
| Containers | Docker, Docker Compose | Local development, reproducible environments |
| CI/CD | GitHub Actions (planned) | Automated testing and deployment |
| Cloud | AWS (planned) | Production deployment |

---

## Multi-Tenancy and Security

- Organization + environment scoping on every record
- Role-based access control (RBAC) with API key and token authentication
- Encrypted connector credentials; read-only source access; least-privilege policies
- Tenant isolation enforced at query level (`WHERE organization_id = ?`)
- Audit logging for sensitive operations
- Rate limiting per tenant / API key
- Webhook signature verification
- Data retention and archiving controls

---

## Project Status

> **Phase: Foundation**

- [x] Dockerized PostgreSQL
- [x] Application configuration (pydantic-settings, .env)
- [x] Database connection layer (SQLAlchemy 2.0, session management)
- [ ] Tenant models (Organization, Environment)
- [ ] Alembic migrations
- [ ] Control-plane API (CRUD for orgs/environments)
- [ ] Authentication and RBAC
- [ ] Data source and dataset catalog
- [ ] Pipeline run event ingestion
- [ ] Check execution workers
- [ ] Freshness / volume / schema checks
- [ ] Incident creation and lifecycle
- [ ] Lineage and impact analysis
- [ ] Statistical baselines
- [ ] ML detection layers
- [ ] Alerting integrations
- [ ] Observability and CI/CD

---

## Local Development

### Prerequisites

- Python 3.12+
- Docker and Docker Compose

### Setup

```bash
git clone https://github.com/<your-username>/DataGuard.git
cd DataGuard

cp .env.example .env
docker compose up -d          # PostgreSQL on port 5433

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

alembic upgrade head          # apply migrations (after migration step)
uvicorn app.main:app --reload --port 8000
```

### Verify

```bash
docker compose ps             # Postgres healthy
curl http://localhost:8000/health
```

---

## License

Private project — not open-sourced.
