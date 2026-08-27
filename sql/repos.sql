DROP TABLE IF EXISTS repos;

CREATE TABLE repos AS
SELECT repo_id,
MIN(repo_name) AS repo_name,
COUNT(*) AS event_count
FROM stg_events
GROUP BY repo_id;

ALTER TABLE repos ADD PRIMARY KEY (repo_id);
