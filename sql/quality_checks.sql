SELECT 'raw vs stg' AS check_name,
       (SELECT COUNT(*) FROM raw_data) AS raw_n,
       (SELECT COUNT(*) FROM stg_events) AS stg_n;

SELECT 'actors cover events' AS check_name,
       (SELECT COUNT(*) FROM stg_events) AS events_n,
       (SELECT SUM(event_count) FROM actors) AS actors_sum;

SELECT 'repos cover events' AS check_name,
       (SELECT COUNT(*) FROM stg_events) AS events_n,
       (SELECT SUM(event_count) FROM repos) AS repos_sum;

SELECT 'null ids' AS check_name,
       COUNT(*) FILTER (WHERE actor_id IS NULL) AS null_actor,
       COUNT(*) FILTER (WHERE repo_id IS NULL) AS null_repo
FROM stg_events;