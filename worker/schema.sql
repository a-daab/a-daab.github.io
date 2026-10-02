-- Cloudflare D1 schema for the petition. Applications and wholesale inquiries are emailed and never stored.
-- Stored minimum (Spec §6.1): name, email, location, timestamp, consent flag. No IP addresses.
CREATE TABLE IF NOT EXISTS signatures (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  email       TEXT    NOT NULL,           -- as entered
  email_lc    TEXT    NOT NULL UNIQUE,    -- lower-cased; the dedupe key
  location    TEXT    NOT NULL,
  consent     INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT    NOT NULL            -- ISO-8601 UTC
);
CREATE INDEX IF NOT EXISTS idx_signatures_created ON signatures(created_at);
