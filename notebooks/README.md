### Run notebook

```bash
$ jupyter notebook
```

Archive is available starting `01.12.2014`.

Fetching data per each year

```bash
$ python download_rates.py --day-start=1 --month-start=12 --year=2014
$ python download_rates.py --year=2015
$ python download_rates.py --year=2016
$ python download_rates.py --year=2017
$ python download_rates.py --year=2018
$ python download_rates.py --day-end=2 --month-end=1 --year=2019
```

Process is not very efficient and for the whole year it takes ~1 hour to
download data due to rate limiting which is about `0.1` request/second.

Fetch latest missing rates for current year (continue previous partial download)

```bash
$ python fetch_latest.py
```

### Missing data

* `24.08.2017` - has only NBU value. Data was averaged for `23.08` and `25.08`
