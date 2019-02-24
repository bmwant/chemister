-- insert resources (banks)
INSERT INTO resource(id, "name", url)
VALUES(1, 'test resource', 'http://google.com');

-- insert transactions
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(1, 'privatbank', 100, 'USD', 26.80, 27.20, '2019-02-06 00:00:00', 1);
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(2, 'privatbank', 100, 'USD', 27.05, 27.35, '2019-02-16 00:00:00', 1);
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(3, 'privatbank', 100, 'USD', 27.05, 27.35, '2019-02-17 00:00:00', 1);
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(4, 'privatbank', 100, 'USD', 27.05, 27.35, '2019-02-18 00:00:00', 1);
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(5, 'privatbank', 100, 'USD', 26.95, 27.25, '2019-02-19 00:00:00', 1);
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(6, 'privatbank', 100, 'USD', 26.95, 27.25, '2019-02-20 00:00:00', 1);
INSERT INTO transaction(id, bank, amount, currency, rate_buy, rate_sale, date_opened, user_id)
VALUES(7, 'privatbank', 100, 'USD', 26.90, 27.20, '2019-02-21 00:00:00', 1);

-- insert users
INSERT INTO "user"(id, "name", email, password)
VALUES (2, 'test', 'test@gmail.com', '591390304a1217a65e5206f943740eaaa8b528e96a5c8bc3a40884d36922ebe0');


ALTER SEQUENCE resource_id_seq RESTART WITH 2;
ALTER SEQUENCE bid_id_seq RESTART WITH 20;
ALTER SEQUENCE user_id_seq RESTART WITH 3;
ALTER SEQUENCE transaction_id_seq RESTART WITH 7;
