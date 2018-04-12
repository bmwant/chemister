from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from crawler.driver import BaseDriver


class ChromeDriver(BaseDriver):
    BINARY_PATH = '/usr/bin/google-chrome'
    EXECUTABLE_PATH = config.CHROME_DRIVER_PATH

    def __init__(self, *, proxy_uri=None):
        super().__init__()

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        if proxy_uri:
            chrome_options.add_argument(f'--proxy-server={proxy_uri}')

        chrome_options.binary_location = self.BINARY_PATH
        driver = webdriver.Chrome(
            executable_path=self.EXECUTABLE_PATH,
            chrome_options=chrome_options,
        )
        self._driver = driver
