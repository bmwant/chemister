from notebooks.helpers import DATE_FMT


class Transaction(object):
    def __init__(self, amount, rate_buy, rate_sale, date, verbose=True):
        self.amount = amount  # amount of currency we bought
        self.rate_buy = rate_buy  # rate when trading
        # selling rate when trading to calculate future profit
        self.rate_sale = rate_sale
        self.date = date
        self._sold = False
        self.verbose = verbose

    def log(self, message):
        if self.verbose:
            print(message)

    def sale(self, rate_buy_closing, dry_run=False):
        if self.sold is True:
            raise RuntimeError('You cannot sell one transaction twice')

        # amount of money we get when selling a transaction
        amount = self.amount * rate_buy_closing
        if not dry_run:
            profit = amount - self.initial_price  # what we gain
            self.log(
                'Selling {amount:.2f} ({rate_sale:.2f}) '
                'at {rate_buy_closing:.2f}; '
                'total: {total:.2f}; profit: {profit:.2f}'.format(
                    amount=self.amount,
                    rate_sale=self.rate_sale,
                    rate_buy_closing=rate_buy_closing,
                    total=amount,
                    profit=profit,
                )
            )
            self._sold = True
        return amount

    @property
    def initial_price(self):
        # Initial price when we are buying from bank
        return self.amount * self.rate_sale

    @property
    def sold(self):
        return self._sold

    def __str__(self):
        return '{}: {:.2f} at {:.2f} = {:.2f}'.format(
            self.date.strftime(DATE_FMT),
            self.amount,
            self.rate_sale,
            self.initial_price,
        )


class DailyData(object):
    def __init__(self, day: int, rate_buy: float, rate_sale: float):
        self.step = day
        self.rate_buy = rate_buy
        self.rate_sale = rate_sale

    def __str__(self):
        return '{day}: {buy:.2f}/{sale:.2f}'.format(
            day=self.step,
            buy=self.rate_buy,
            sale=self.rate_sale,
        )
