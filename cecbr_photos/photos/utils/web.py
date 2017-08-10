import os
import time
import logging
import environ
from urllib.parse import quote

from bs4 import BeautifulSoup
from selenium import webdriver

# Load operating system environment variables and then prepare to use them
env = environ.Env()

#CAMP BASE URLS
LOGON_URL = "https://blueridge.campintouch.com/v2/login/login.aspx"
SEASON_URL = "https://blueridge.campintouch.com/ui/photo/Albums"
ALBUM_URL = "https://blueridge.campintouch.com/ui/photo/Thumbnails"

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Page(object):
    def __init__(self, username, pwd, *args, **kwargs):

        self._l_page = kwargs.pop("logon_url", LOGON_URL)
        self._username = username
        self._pwd = pwd
        self._redirect = kwargs.pop("redirect", None)
        self._initalized = False
        self._logged_in = False
        self._wd = None
        self._driver_path = kwargs.pop('driver_path', None)

    @property
    def l_page(self):
        return self._l_page

    @l_page.setter
    def l_page(self, l_page):
        self._l_page = l_page

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        self._username = username

    @property
    def pwd(self):
        return self._pwd

    @pwd.setter
    def pwd(self, pwd):
        self._pwd = pwd

    @property
    def redirect(self):
        return self._redirect

    @redirect.setter
    def redirect(self, redirect):
        self._redirect = redirect

    @property
    def initialized(self):
        return self._initalized

    @property
    def logged_in(self):
        return self._logged_in

    def driver(self, check_initialized=True):
        if check_initialized:
            if not self._initalized:
                self.initialize()
            if not self._logged_in:
                self.log_in()

        return self._wd

    def initialize(self):

        if self._driver_path is None:
            base_dir = os.path.dirname(os.path.realpath(__file__))
            dname = 'phantomjs.exe'
            driver = os.path.join(base_dir, dname)
        else:
            driver = self._driver_path

        self._wd = webdriver.PhantomJS(driver)
        self._initalized = True

    def log_in(self):

        logon_url = self._l_page

        if self._redirect is not None:
            logon_url = '?'.join([logon_url, quote(self._redirect, safe='=')])

        if not self._initalized:
            self.initialize()

        logger.info("Attempting to log in to {}".format(logon_url))

        l_page = self._wd.get(logon_url)

        # now handle the form
        user_tb = self._wd.find_element_by_name('txtEmail')
        user_tb.clear()
        user_tb.send_keys(self._username)
        pw_tb = self._wd.find_element_by_name('txtPassword')
        pw_tb.clear()
        pw_tb.send_keys(self._pwd)
        # submit
        submit_bttn = self._wd.find_element_by_id('btnLogin')
        submit_bttn.click()
        time.sleep(10)
        self._logged_in = True

    def close(self):
        if self._wd is not None:
            self._wd.close()
        self._logged_in = False
        self._initalized = False

    def retrieve_page(self, page_url):
        logger.info("Retrieving page %s" % page_url)
        if not self._logged_in:
            self.log_in()
        self._wd.get(page_url)
        return self._wd

    def retrieve_page_html(self, page_url):
        return self.retrieve_page(page_url).page_source


class CampMinderPhotoFinder(object):
    def __init__(self, cmp, url, *args, **kwargs):
        self._cmp = cmp
        self._url = url
        # handle optional stuff
        self._array_search_string = kwargs.pop('array_search_string', 'AlbumArray')
        self._front_clean_chars = kwargs.pop('front_clean_chars', 1)
        self._main_dict_key = kwargs.pop('main_dict_key', 'AlbumID')

    @property
    def cmp(self):
        return self._cmp

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def array_search_string(self):
        return self._array_search_string

    @array_search_string.setter
    def array_search_string(self, array_search_string):
        self._array_search_string = array_search_string

    @property
    def font_clean_chars(self):
        return self._front_clean_chars

    @font_clean_chars.setter
    def font_clean_chars(self, fcc):
        self._front_clean_chars = fcc

    @property
    def main_dict_key(self):
        return self._main_dict_key

    @main_dict_key.setter
    def main_dict_key(self, mdk):
        self._main_dict_key = mdk

    def prettify(self, string):
        pass

    def parse(self):

        if not self._cmp.logged_in:
            self._cmp.log_in()

        dicts = {}
        page_html = self._cmp.retrieve_page_html(self._url)

        # use beautiful soup for parsing
        soup = BeautifulSoup(page_html, 'html.parser')
        scripts = soup.find_all(script_with_no_src)
        for script in scripts:
            if self._array_search_string in script.text:
                dicts = self.read_pretified_to_dict(self.build_album_array_string(script.text))

        return dicts

    def split_token(self, token):
        split_pos = token.find(":")
        if split_pos == -1:
            raise ValueError("%s is not a valid key.value token" % token)
        key = token[0:split_pos].replace('{', '').replace('"', '')
        value = token[split_pos + 1:].replace('\\', '')
        return (key, value)

    def read_pretified_to_dict(self, pretty_string):
        dicts = {}
        for row in pretty_string.split('\n'):
            if len(row) != 1:
                local_dict = {}
                decoded = row.replace('\\', '')
                cleaned = decoded[self._front_clean_chars:(len(decoded) - 1)]
                tokens = cleaned.split(',')
                for token in tokens:
                    try:
                        (key, value) = self.split_token(token)
                        local_dict[key] = value
                    except ValueError:
                        logger.debug("token %s does not parse correctly" % token)
                dicts[local_dict[self._main_dict_key]] = local_dict
        return dicts

    def build_album_array_string(self, string):
        logger.info("Attepmting to extract javascript album")
        start_album_array = string.find(self.array_search_string)
        if start_album_array == -1:
            raise ValueError("String does not contain {}".format(self._array_search_string))
        start_album_array += len(self._array_search_string)
        # find the opening '['
        pos = string.find('[', start_album_array)
        if pos == -1:
            raise ValueError("Not a valid camp minder album string")
        bracket_count = 1
        char_list = ['[']
        pos += 1
        while bracket_count != 0 or pos == len(string):
            c = string[pos]
            if c == '[':
                bracket_count += 1
            elif c == ']':
                bracket_count -= 1
            char_list.append(c)
            pos += 1
        return self.prettify(''.join(char_list))


class IndexAlbumParser(CampMinderPhotoFinder):
    def __init__(self, cmp, url, *args, **kwargs):
        super().__init__(cmp, url, *args, **kwargs)

    def prettify(self, string):
        pos = 0
        pretty_array = []
        while pos < len(string):
            c = string[pos]
            pretty_array.append(c)
            if c == '}':
                pretty_array.append('\n')
            pos += 1
            if pos == 1:
                pretty_array.append('\n,')
        return ''.join(pretty_array)


class FavoriteAlbumParser(CampMinderPhotoFinder):
    def __init__(self, cmp, url, *args, **kwargs):
        super().__init__(cmp, url, *args, **kwargs)
        self._array_search_string = kwargs.get('array_search_string', 'CurrentAlbum')
        self._front_clean_chars = kwargs.get('front_clean_chars', 2)
        self._main_dict_key = kwargs.get('main_dict_key', 'PhotoID')

    def prettify(self, string):
        pos = 0
        pretty_array = []
        brck_count = 0
        while pos < len(string):
            c = string[pos]
            pretty_array.append(c)
            if c == '{':
                brck_count += 1
            if c == '}':
                brck_count -= 1
                if brck_count == 0:
                    pretty_array.append('\n')
            pos += 1
            if pos == 1:
                pretty_array.append('\n,')
        return ''.join(pretty_array)


def script_with_no_src(tag):
    return tag.name == 'script' and not tag.has_attr('src')

def unquote(string):
    if string.startswith('"') and string.endswith('"'):
        string = string[1:-1]
    return string
