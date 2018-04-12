import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException

from utils import get_logger
from crawler.fetcher import BaseFetcher
from crawler.driver.chrome import ChromeDriver


class BrowserFetcher(BaseFetcher):
    DEFAULT_DRIVER_CLS = ChromeDriver
    DEFAULT_WAIT_TIME = 2
    ACTIONS_DELAY_TIME = 2

    def __init__(self, base_url, *,
                 driver_cls=None, xpath=None, proxy=None):
        super().__init__(base_url, proxy=proxy)

        driver_cls = driver_cls or self.DEFAULT_DRIVER_CLS
        proxy_uri = self._get_proxy_uri(proxy, driver_cls)
        driver_wrapper = driver_cls(proxy_uri=proxy_uri)

        self.driver = driver_wrapper.driver
        self.proxy_uri = proxy_uri
        self.xpath = xpath
        self.logger = get_logger(self.__class__.__name__.lower())

    def _get_proxy_uri(self, proxy, driver_cls):
        """
        Proxy format may vary based on browser driver used. This helpers allows
        to figure out which format is correct.
        """
        proxy_uri = None
        if proxy and driver_cls == ChromeDriver:
            proxy_uri = proxy.chrome_uri
        elif proxy:
            proxy_uri = proxy.uri

        return proxy_uri

    async def request(self, url=None):
        if url is None:
            url = self.base_url

        self.logger.info(f'Requesting {url} with proxy: {self.proxy_uri}')
        with ThreadPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                executor, self._get, url, self.DEFAULT_WAIT_TIME)
        return await future

    def _get(self, url: str, wait: int=0) -> str:
        self.driver.delete_all_cookies()
        self.driver.get(url)
        # Wait for js on page to render
        time.sleep(wait)

        self._do_actions()
        # Crop page to particular region if needed
        if self.xpath is not None:
            return self.driver. \
                find_element_by_xpath(self.xpath). \
                get_attribute('outerHTML')

        return self.driver.page_source

    def _do_actions(self):
        """
        Make some actions on a page like clicking tabs or open
        collapsed elements.
        """
        expand_elements_text = (
            'Show More',
            'Show All',
        )
        for guess_text in expand_elements_text:
            try:
                # Add any logic for common elements here
                elem = self.driver.find_element_by_xpath(
                    f'//*[contains(text(), "{guess_text}")]')

                self._click_element(elem)
            except NoSuchElementException:
                pass
            else:
                break
        # Wait for page to process events
        time.sleep(self.ACTIONS_DELAY_TIME)

    def _click_element(self, elem):
        try:
            elem.click()
        except WebDriverException as e:
            pass
        else:
            return

        try:
            pos = elem.location_once_scrolled_into_view
            xpos = pos['x']
            ypos = pos['y']
            # Element should be available to click
            self.driver.execute_script(
                f'window.scrollBy({xpos}, {ypos})', '')
            elem.click()
        except WebDriverException as e:
            self.logger.critical(
                f'Received unexpected error: {e} '
                f'Ignoring it, but you may get corrupted/partial results.')

    def _close(self):
        self.driver.close()

    async def close(self):
        with ThreadPoolExecutor(max_workers=1) as executor:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, self._close)
            await future
