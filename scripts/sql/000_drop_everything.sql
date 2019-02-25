DROP DATABASE IF EXISTS chemister;

DROP TYPE IF EXISTS transaction_status;
DROP TYPE IF EXISTS event_type;
DROP TYPE IF EXISTS fund_type;

DROP TABLE IF EXISTS config CASCADE;
DROP TABLE IF EXISTS "transaction" CASCADE;
DROP TABLE IF EXISTS "resource" CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS fund CASCADE;
DROP TABLE IF EXISTS rate CASCADE;
DROP TABLE IF EXISTS "event" CASCADE;

DROP ROLE IF EXISTS "che";
