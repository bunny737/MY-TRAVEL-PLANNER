-- Runs once on first cluster init (fresh pgdata volume only).
-- The app connects as a NON-superuser so a misconfigured connection can never run DDL
-- outside migrations or read other databases. CREATEDB is needed so Django can create
-- the test database. (Unlike the PG-MANAGEMENT project there is no RLS here: this is a
-- single-tenant site with an owner-only admin.)
CREATE ROLE app_user LOGIN PASSWORD 'app_password' NOSUPERUSER CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE travel_platform TO app_user;
\connect travel_platform
GRANT ALL ON SCHEMA public TO app_user;
