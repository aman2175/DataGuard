DROP TABLE IF EXISTS actors;

CREATE TABLE actors AS
SELECT 
actor_id, 
MIN(actor_login) AS actor_login,
COUNT(*) AS event_count
FROM stg_events
GROUP BY ACTOR_ID;

ALTER TABLE actors ADD PRIMARY KEY (actor_id);