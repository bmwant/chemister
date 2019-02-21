SET SCHEMA 'public';


CREATE TYPE bid_status AS ENUM (
  'new', 'notified', 'called', 'rejected', 'inactive', 'closed'
);

CREATE TYPE bid_type AS ENUM (
  'in', 'out'
);

CREATE TYPE currency AS ENUM (
  'UAH', 'USD'
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
  currency      currency        NOT NULL,
  phone         VARCHAR         NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
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
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),

  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS "user"(
  id            SERIAL          NOT NULL,
  name          VARCHAR         NOT NULL,
  email         VARCHAR         NOT NULL,
  password      VARCHAR         NOT NULL,
  permissions   JSON,

  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS transaction(
  id            SERIAL          NOT NULL,
  amount        NUMERIC         NOT NULL,
  currency      currency        NOT NULL,
  rate_buy      NUMERIC         NOT NULL,
  rate_sale     NUMERIC         NOT NULL,
  rate_close    NUMERIC,
  date_opened   TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  date_closed   TIMESTAMP,
  user_id       INT             NOT NULL,

  FOREIGN KEY (user_id) REFERENCES "user" (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS fund(
  id            SERIAL          NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  amount        NUMERIC         NOT NULL    DEFAULT 0,
  currency      currency        NOT NULL,
--   value          JSON         NOT NULL,
  user_id   INT             NOT NULL,

  FOREIGN KEY (user_id) REFERENCES "user" (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS config(
  id            SERIAL          NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  value         JSON            NOT NULL,
  user_id       INT             NOT NULL,

  FOREIGN KEY (user_id) REFERENCES "user" (id),
  PRIMARY KEY (id)
);
