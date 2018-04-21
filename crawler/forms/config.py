import trafaret as t


config_trafaret = t.Dict(
    MIN_BID_AMOUNT=t.Float,
    MAX_BID_AMOUNT=t.Float,
    DRY_RUN=t.StrBool,
    CLOSED_BIDS_FACTOR=t.Float,
    TIME_DAY_ENDS=t.String,
    TIME_DAY_STARTS=t.String,
    REFRESH_PERIOD_MINUTES=t.Int,
)
