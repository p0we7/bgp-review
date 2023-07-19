# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import scrapy
from scrapy_splash import SplashRequest, SlotPolicy

import re
import os

lua_script = """
function main(splash)
  --splash:set_user_agent(splash.args.ua)
  assert(splash:go(splash.args.url))

  -- requires Splash 2.3
  while not splash:select('#search') and not splash:select('#whois') do
    splash:wait(2)
  end
   return {
    html = splash:html(),
    cookies = splash:get_cookies(),
  }
end
"""

class BaseSpider(scrapy.Spider):

    lua_script = """
    function main(splash)
    --splash:set_user_agent(splash.args.ua)
    assert(splash:go(splash.args.url))

    -- requires Splash 2.3
    while not splash:select('#search') and not splash:select('#whois') do
        splash:wait(2)
    end
    return {
        html = splash:html(),
        cookies = splash:get_cookies(),
    }
    end
    """


    def format_cookies_for_request(self, response):
        return { cookie.get('name'): cookie.get('value') for cookie in response.data['cookies'] }


    def store_cookies_to_file(self, response=None, operate='read'):
        if operate == 'read':
            try:
                with open('cookies.txt', 'r') as f:
                        cookiejar = f.read()
                        p = re.compile(r'<Cookie (.*?) for .*?>')
                        cookies = re.findall(p, cookiejar)
                        cookies = (cookie.split('=', 1) for cookie in cookies)
                        cookies = dict(cookies)
                return cookies
            except FileNotFoundError:
                return []
            

        if operate == 'write':
            cookie_jar = response.cookiejar
            with open('cookies.txt', 'w') as f:
                for cookie in cookie_jar:
                    f.write(str(cookie) + '\n')


    def _save_resopnse_to_html(self, response):
        """
        code for debug
        saving crawler html file
        """

        if 'search' in response.url:
            file_name = 'SEARCH_detail.html'
        else:
            file_name = 'ASN_detail.html'

        file_name = './data/' + file_name

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'w') as f:
            f.write(response.body.decode('utf-8'))

