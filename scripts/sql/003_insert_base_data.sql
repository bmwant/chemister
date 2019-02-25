INSERT INTO "user"(id, "name", email, password)
VALUES (1, 'admin', 'admin@gmail.com', 'd087b9a83cac516233091ab276848e743962abfe534a91c84c6aa9bd50f2a8bb');

INSERT INTO config(id, "value", user_id)
VALUES (1, '{"MIN_BID_AMOUNT": 100, "MAX_BID_AMOUNT": 1000, "DRY_RUN": true, "CLOSED_BIDS_FACTOR": 1, "TIME_DAY_ENDS": "23:59", "TIME_DAY_STARTS": "00:01", "REFRESH_PERIOD_MINUTES": 5}', 1);

INSERT INTO fund(id, bank, amount, currency, user_id)
VALUES (1, 'default', 0, 'USD', 1);
INSERT INTO fund(id, amount, currency, user_id)
VALUES (2, 'default', 0, 'UAH', 1);

ALTER SEQUENCE user_id_seq RESTART WITH 2;
ALTER SEQUENCE config_id_seq RESTART WITH 2;
ALTER SEQUENCE fund_id_seq RESTART WITH 3;
