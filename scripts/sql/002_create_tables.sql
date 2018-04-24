SET SCHEMA 'public';


CREATE TYPE bid_status AS ENUM (
  'new', 'notified', 'called', 'rejected', 'inactive', 'closed'
);

CREATE TYPE bid_type AS ENUM (
  'in', 'out'
);


CREATE TABLE IF NOT EXISTS config(
  id            SERIAL          NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_DATE,
  value         JSON            NOT NULL

--   user_id  INT NOT NULL
--   FOREIGN KEY (user_id) REFERENCES user (id),
);


CREATE TABLE IF NOT EXISTS resource(
  id            SERIAL          NOT NULL,
  name          VARCHAR         NOT NULL,
  url           VARCHAR         NOT NULL,

  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS bid(
  -- todo: unique together on signature
  id            SERIAL          NOT NULL,
  rate          NUMERIC         NOT NULL,
  amount        NUMERIC         NOT NULL,
  currency      VARCHAR         NOT NULL,
  phone         VARCHAR         NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_DATE,
  dry_run       BOOLEAN         NOT NULL,
  in_use        BOOLEAN         NOT NULL    DEFAULT TRUE,
  status        bid_status      NOT NULL    DEFAULT 'new',
  bid_type      bid_type        NOT NULL,
  resource_id   INT             NOT NULL,

  FOREIGN KEY (resource_id) REFERENCES resource (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS phone(
  id            SERIAL          NOT NULL,
  phone         VARCHAR         NOT NULL,
  reason        VARCHAR         NOT NULL,

  PRIMARY KEY (id)
)


-- CREATE TABLE IF NOT EXISTS "user"(
--   id            SERIAL          NOT NULL,
--   name          VARCHAR         NOT NULL,
--   email          VARCHAR         NOT NULL,
--   password          VARCHAR         NOT NULL,
--   permissions   JSON,
--
--   PRIMARY KEY (id)
-- );
