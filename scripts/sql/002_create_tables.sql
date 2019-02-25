SET SCHEMA 'public';


CREATE TYPE transaction_status AS ENUM (
  'wait_buy', 'hanging', 'wait_sale', 'completed'
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
  resource_id   INT             NOT NULL,

  FOREIGN KEY (resource_id) REFERENCES resource (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS "user"(
  id            SERIAL          NOT NULL,
  name          VARCHAR         NOT NULL,
  email         VARCHAR         NOT NULL,
  password      VARCHAR         NOT NULL,
  telegram      VARCHAR,
  permissions   JSON,

  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS "transaction"(
  id            SERIAL              NOT NULL,
  bank          VARCHAR             NOT NULL,
  amount        NUMERIC             NOT NULL,
  currency      currency            NOT NULL,
  rate_buy      NUMERIC             NOT NULL,
  rate_sale     NUMERIC             NOT NULL,
  rate_close    NUMERIC,
  date_opened   TIMESTAMP           NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  date_closed   TIMESTAMP,
  status        transaction_status  NOT NULL    DEFAULT 'wait_buy',
  user_id       INT                 NOT NULL,

  FOREIGN KEY (user_id) REFERENCES "user" (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS fund(
  id            SERIAL          NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  bank          VARCHAR         NOT NULL    DEFAULT 'default',
  amount        NUMERIC         NOT NULL    DEFAULT 0,
  currency      currency        NOT NULL,
--   value          JSON         NOT NULL,
  user_id       INT             NOT NULL,

  FOREIGN KEY (user_id) REFERENCES "user" (id),
  PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS rate(
  id            SERIAL          NOT NULL,
  date          TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  bank          VARCHAR         NOT NULL,
  currency      currency        NOT NULL,
  rate_buy      NUMERIC         NOT NULL,
  rate_sale     NUMERIC         NOT NULL,

-- bank_id   INT             NOT NULL,

-- say resource id for example
-- FOREIGN KEY (bank_id) REFERENCES "bank" (id),
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

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO che;
