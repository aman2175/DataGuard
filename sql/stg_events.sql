DROP TABLE IF EXISTS stg_events;
CREATE TABLE stg_events AS
    SELECT event_id,
    event_type,
    created_at,
    payload -> 'actor' ->> 'login' AS actor_login,
    (payload -> 'actor' ->> 'id')::bigint AS actor_id,
    payload -> 'repo' ->> 'name' AS repo_name,
    (payload -> 'repo' ->> 'id')::bigint AS repo_id
    FROM raw_data;

