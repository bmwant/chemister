INSERT INTO "user"(id, "name", email, password)
VALUES (1, 'admin', 'admin@gmail.com', 'admin');

INSERT INTO config(id, "value", user_id)
VALUES (1, '{"MIN_BID_AMOUNT": 100, "MAX_BID_AMOUNT": 1000, "DRY_RUN": true, "CLOSED_BIDS_FACTOR": 1, "TIME_DAY_ENDS": "20:00", "TIME_DAY_STARTS": "06:00", "REFRESH_PERIOD_MINUTES": 5}', 1);

INSERT INTO fund(id, amount, user_id)
VALUES (1, 0, 1);

ALTER SEQUENCE user_id_seq RESTART WITH 2;
ALTER SEQUENCE config_id_seq RESTART WITH 2;
ALTER SEQUENCE fund_id_seq RESTART WITH 2;
