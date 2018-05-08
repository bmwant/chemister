DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'event_type') THEN
    CREATE TYPE event_type AS ENUM(
      'notified', 'called', 'default'
    );
  END IF;
END
$$;


CREATE TABLE IF NOT EXISTS "event"(
  id            SERIAL          NOT NULL,
  created       TIMESTAMP       NOT NULL    DEFAULT CURRENT_TIMESTAMP(2),
  description   VARCHAR         NOT NULL    DEFAULT '',
  event_type    event_type      NOT NULL    DEFAULT 'default',
  event_count   INT             NOT NULL    DEFAULT 1,
  user_id       INT             NOT NULL    DEFAULT 0,

  PRIMARY KEY (id)
);
