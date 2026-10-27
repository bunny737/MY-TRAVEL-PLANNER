-- The travel site's own role and database on PGLive's Cloud SQL instance (docs/deployment.md §3).
-- Run once as `postgres`, connected to the `postgres` database through the Cloud SQL Auth Proxy. Idempotent.
--
--   cloud-sql-proxy pglive-prod:asia-south1:pglive-pg-prod --port 6543
--   psql "host=127.0.0.1 port=6543 user=postgres dbname=postgres" \
--     -v travel_password="$TRAVEL_DB_PASSWORD" -f deploy/cloudsql/create-travel-db.sql
--
-- A plain role, NOT `gcloud sql users create`: Cloud SQL adds users created that way to cloudsqlsuperuser.
-- CONNECTION LIMIT 12 keeps this site inside its share of the instance's ~50 connections (db-g1-small), so it can
-- never starve PGLive. Nothing here changes instance settings or any other database.
\set ON_ERROR_STOP on

SELECT 'CREATE ROLE travel_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION CONNECTION LIMIT 12'
WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'travel_app')\gexec
ALTER ROLE travel_app LOGIN NOCREATEDB NOCREATEROLE CONNECTION LIMIT 12 PASSWORD :'travel_password';

-- Cloud SQL's postgres is not a real superuser: it must be a member of travel_app to create a database owned by it.
GRANT travel_app TO postgres;

SELECT 'CREATE DATABASE travel_platform OWNER travel_app'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'travel_platform')\gexec
ALTER DATABASE travel_platform OWNER TO travel_app;
REVOKE ALL ON DATABASE travel_platform FROM PUBLIC;
GRANT CONNECT, TEMPORARY ON DATABASE travel_platform TO travel_app;

-- Show the result (no passwords): expect travel_app, f, f, f, 12.
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole, rolconnlimit FROM pg_roles WHERE rolname = 'travel_app';
