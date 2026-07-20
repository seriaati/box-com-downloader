# Box.com PDF Downloader
# Copyright (C) 2018 lfasmpao
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import platform
import re
import sys
import time

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


def url_checker(url):
    """
       This checks the url format
       :param url Unified Resource Locator
       :rtype: bool
       :return boolean
    """
    url_check_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)  # url check regex
    if re.match(url_check_regex, url) is not None:
        return "box.com" in url  # really?


class Scraper:
    def __init__(self, url, driver_location=None, use_x11=False, wait_time=None):
        """
        This starts a selenium session
        :param url box.com url
        :type url string
        :param driver_location chrome driver path
        :type driver_location string
        """

        chrome_options = Options()
        if use_x11:
            if platform.system() == "Linux":
                self.display = Display(visible=0, size=(800, 600))
                self.display.start()  # start new virtual display
        else:
            # hide chrome session
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1280x800")

        # capture network requests (incl. auth headers) via chrome's performance log
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        self.wait_load_time = wait_time
        self.use_x11 = use_x11
        self.driver_location = driver_location
        self.url = url
        if self.driver_location:
            self.driver_obj = webdriver.Chrome(service=Service(self.driver_location), options=chrome_options)
        else:
            # let Selenium Manager find/download a matching chromedriver
            self.driver_obj = webdriver.Chrome(options=chrome_options)

    def load_url(self):
        """
        This will load the url on the selenium driver
        """
        driver = self.driver_obj
        url = self.url
        driver.get(url)  # load selenium
        # TODO: This is a bad, maybe we should change this to selenium WebDriverWait
        time.sleep(self.wait_load_time)  # wait load time, implicit wait doesnt work well?

    def get_download_title(self):
        """
        This parses box.com title
        :rtype: string
        :return download title
        """
        driver = self.driver_obj
        title = str(driver.title).split("|")[0][:-1]
        return str(title.split(".")[:-1][0])  # split and remove extra white space

    def get_download_url(self):
        """
        This parses box.com url into PDF downloadable file
        :rtype tuple
        :returns (download_url, authorization header) else (None, None)
        """
        driver = self.driver_obj  # get driver
        download_url = None  # default or error
        auth_header = None
        # box.com now serves the file via an authenticated /api/2.0/files/<id>/content
        # request, so scrape url + Authorization header from chrome's performance log
        events = [json.loads(entry["message"])["message"] for entry in driver.get_log("performance")]
        request_ids = set()
        for message in events:
            if message["method"] != "Network.requestWillBeSent":
                continue
            request = message["params"]["request"]
            if ("/api/2.0/files/" in request["url"]) and ("/content" in request["url"]):
                download_url = request["url"]
                request_ids.add(message["params"]["requestId"])
                auth_header = request["headers"].get("Authorization", auth_header)
        # full headers (incl. Authorization) are often only on the ExtraInfo
        # event, which has no url and must be matched by requestId
        for message in events:
            if message["method"] != "Network.requestWillBeSentExtraInfo":
                continue
            if message["params"].get("requestId") not in request_ids:
                continue
            headers = message["params"]["headers"]
            auth_header = headers.get("Authorization") or headers.get("authorization") or auth_header
        return download_url, auth_header

    def clean(self):
        """
        This will close the current selenium session
        """
        self.driver_obj.quit()
        if self.use_x11 is True:
            self.display.stop()
