-- History tables for the site-analytics skill (Supabase / Postgres). snapshot.py upserts into these.
-- goal_1..goal_4 follow the order of PLAUSIBLE_GOALS in your config.
CREATE TABLE IF NOT EXISTS site_analytics_daily (
  day          date NOT NULL,
  dimension    text NOT NULL,   -- entry_page | source | utm_campaign | utm_content
  value        text NOT NULL,
  visits       integer NOT NULL DEFAULT 0,
  visitors     integer NOT NULL DEFAULT 0,
  bounce_rate  numeric,
  avg_seconds  numeric,
  goal_1       integer NOT NULL DEFAULT 0,
  goal_2       integer NOT NULL DEFAULT 0,
  goal_3       integer NOT NULL DEFAULT 0,
  goal_4       integer NOT NULL DEFAULT 0,
  goals_total  integer NOT NULL DEFAULT 0,
  PRIMARY KEY (day, dimension, value)
);
CREATE TABLE IF NOT EXISTS clarity_daily (
  day            date NOT NULL,
  path           text NOT NULL,
  sessions       integer,
  scroll_depth   numeric,
  active_seconds numeric,
  rage_clicks    numeric,   -- % of sessions
  dead_clicks    numeric,   -- % of sessions
  quick_backs    numeric,   -- % of sessions
  PRIMARY KEY (day, path)
);
-- Supabase: keep the tables private (RLS on, no policies); snapshot.py uses the service-role key.
ALTER TABLE site_analytics_daily ENABLE ROW LEVEL SECURITY;
ALTER TABLE clarity_daily ENABLE ROW LEVEL SECURITY;
