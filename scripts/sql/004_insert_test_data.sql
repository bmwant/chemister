INSERT INTO resource(id, "name", url)
VALUES(1, 'test resource', 'http://google.com');


INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (1, 26.01, 101, 'USD', '+380987771101', TRUE, 'in', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (2, 26.02, 102, 'USD', '+380987771102', TRUE, 'in', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (3, 26.03, 103, 'USD', '+380987771103', TRUE, 'in', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (4, 26.04, 104, 'USD', '+380987771104', TRUE, 'in', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (5, 26.05, 105, 'USD', '+380987771105', TRUE, 'in', 1);

INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (11, 26.11, 111, 'USD', '+380987771111', TRUE, 'out', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (12, 26.12, 112, 'USD', '+380987771112', TRUE, 'out', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (13, 26.13, 113, 'USD', '+380987771113', TRUE, 'out', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (14, 26.14, 114, 'USD', '+380987771114', TRUE, 'out', 1);
INSERT INTO bid(id, rate, amount, currency, phone, dry_run, bid_type, resource_id)
VALUES (15, 26.15, 115, 'USD', '+380987771115', TRUE, 'out', 1);

-- insert transactions
INSERT INTO transaction(id, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(1, 100, 'USD', 26.14, 26.22, '2019-02-16 00:00:00', 1);
INSERT INTO transaction(id, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(2, 200, 'USD', 26.14, 26.22, '2019-02-16 00:00:00', 1);
INSERT INTO transaction(id, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(3, 300, 'USD', 26.24, 26.32, '2019-02-16 00:00:00', 1);
INSERT INTO transaction(id, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(4, 150, 'USD', 26.24, 26.32, '2019-02-15 00:00:00', 1);

INSERT INTO "user"(id, "name", email, password)
VALUES (2, 'test', 'test@gmail.com', '591390304a1217a65e5206f943740eaaa8b528e96a5c8bc3a40884d36922ebe0');


ALTER SEQUENCE resource_id_seq RESTART WITH 2;
ALTER SEQUENCE bid_id_seq RESTART WITH 20;
ALTER SEQUENCE user_id_seq RESTART WITH 3;
ALTER SEQUENCE transaction_id_seq RESTART WITH 5;
