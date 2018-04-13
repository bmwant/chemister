SET SCHEMA 'public';


CREATE TYPE bid_status AS ENUM (
  'new', 'notified', 'called', 'rejected', 'inactive', 'closed'
);


CREATE TABLE IF NOT EXISTS config(
  id            SERIAL          NOT NULL,
  created       TIMESTAMP       NOT NULL,
  value         JSON            NOT NULL
);


CREATE TABLE IF NOT EXISTS bid(
  id            SERIAL          NOT NULL,
  rate          REAL            NOT NULL,
  amount        REAL            NOT NULL,
  currency      VARCHAR            NOT NULL,
  phone         VARCHAR         NOT NULL,
  created       TIMESTAMP       NOT NULL,
  dry_run       BOOLEAN         NOT NULL,
  resource_id   INT             NOT NULL,

  FOREIGN KEY (resource_id) REFERENCES resource (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS resource(
  id            SERIAL          NOT NULL,
  name          VARCHAR         NOT NULL,
  url           VARCHAR         NOT NULL,

  PRIMARY KEY (id)
);
