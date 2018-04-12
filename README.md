## wcbot
World Cup 2018 Win Outright Comparison.

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

### Installation
```
$ git clone https://github.com/bmwant/wcbot.git
$ pipenv install
$ npm install
$ pipenv shell
$ python runserver.py
```
or using CLI scripts
```
$ python cli.py monitor
$ redis-cli
> get [resource name]
# e.g. > get "Sky Bet"
```
You may need to 
```
$ export PYTHONPATH=`pwd`
```
in case you encounter some import errors.

### Test
```
$ pytest -sv tests
```

### Extend
To add new resource follow these steps:
1. Edit `resources.yml` and add new resource
2. Add new parser to `crawler.parser` package
3. Yes, that's it!

