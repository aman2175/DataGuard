CREATE INDEX IF NOT EXISTS stg_events_actor_id_idx ON stg_events (actor_id);
CREATE INDEX IF NOT EXISTS stg_events_repo_id_idx ON stg_events (repo_id);
CREATE INDEX IF NOT EXISTS stg_events_event_type_idx ON stg_events (event_type);
CREATE INDEX IF NOT EXISTS stg_events_created_at_idx ON stg_events (created_at);