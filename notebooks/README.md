### Run notebook
```bash
$ jupyter notebook
```

Archive is available starting `01.12.2014`

```bash
$ python download_rates.py --year=2017
```

Process is not very efficient and for the whole year it takes ~1 hour to
download data due to rate limiting which is about 

Fetch latest missing rates for current year
```bash
$ python fetch_latest.py
```

### Missing data

* `24.08.2017` - has only NBU value. Data was averaged for `23.08` and `25.08`
* `RUB` currency is stored only 2 digits after a point, so values might 
be inaccurate
