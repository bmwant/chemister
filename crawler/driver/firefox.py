from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import config
from crawler.driver import BaseDriver


class FirefoxDriver(BaseDriver):
    EXECUTABLE_PATH = config.GECKO_DRIVER_PATH

    def __init__(self):
        super().__init__()

        firefox_options = Options()
        firefox_options.add_argument('-headless')

        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference('permissions.default.stylesheet', 2)
        firefox_profile.set_preference('permissions.default.image', 2)
        firefox_profile.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')

        driver = webdriver.Firefox(
            executable_path=self.EXECUTABLE_PATH,
            firefox_options=firefox_options,
            log_path='/tmp/geckodriver.log',
            firefox_profile=firefox_profile,
        )
        driver.set_page_load_timeout(10)

        self._driver = driver
