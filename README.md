## chemister

Che Mister.

For implementations details and design notes go straight to 
[Architecture](resources/ARCHITECTURE.md)

### Features
* Easily configurable via YAML files
* Nice UI via web application
* Very extensible: add any fetcher/browser driver/parser, customize
parser engines, choose cache backend for any taste
* Convenient process of adding new resource
* Coverage with unittests and functional tests

### Prerequisites
Make sure you have next items installed:
* [pipenv](https://docs.pipenv.org/)
* [Redis](https://redis.io/)
* [Chrome](https://www.google.com/chrome/) + 
[chromedriver](https://chromedriver.storage.googleapis.com/index.html)

### Run Postgresql within docker container

```bash
$ docker volume create chemister-data
$ docker run --name local-postgres -v chemister-data:/var/lib/postgresql/data \
--network host -d postgres
$ docker run -it -v $(pwd):/opt --rm --link local-postgres:postgres postgres \
/opt/scripts/run_sql.sh
```

### Installation
```bash
$ git clone https://github.com/bmwant/chemister.git
$ pipenv install
$ npm install
$ pipenv shell
$ python runserver.py
```
or using CLI scripts
```bash
$ python cli.py monitor
$ redis-cli
> get [resource name]
# e.g. > get "Sky Bet"
```
You may need to 
```bash
$ export PYTHONPATH=`pwd`
```
in case you encounter some import errors.

### Test
```bash
$ pytest -sv tests
```

### Checking data within database
```
$ psql -U che -d chemister -h 172.17.0.2

=> \dt
=> select * from bid;
=> \q
```

