import scrapy
import time
from bs4 import BeautifulSoup
import re
from scrapy_splash import SplashRequest
from scrapy.utils.response import open_in_browser
from selenium.webdriver.support.ui import WebDriverWait
import lxml
from scrapy_selenium import SeleniumRequest
import selenium

import urllib
from selenium import webdriver
from .facebook import facebook_process
center_script = """
document.getElementById('social-comments').scrollIntoView({
            behavior: 'auto',
            block: 'center',
            inline: 'center'
        });
"""
script = """
function sleep(ms) {
  ms = ms*1000
  var start = new Date().getTime(), expire = start + ms;
  while (new Date().getTime() < expire) { }
  return;
}

num_scrolls = 10
scroll_delay = 10
page_divisions = 10

for (i = 1; i <= num_scrolls; i++) {
    for (j = 1; j <= page_divisions; j++) {
        window.scrollTo(0, document.body.scrollHeight * j/page_divisions);
        sleep(scroll_delay/page_divisions);
    }
}
for (i = 1; i <= num_scrolls; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    sleep(scroll_delay);
}
"""


class TerraSpider(scrapy.Spider):
    name = "terra"
    allowed_domains = ['www.terra.com.br']
    # start_urls = ['https://www.terra.com.br/noticias/ciencia/espaco/']
    start_urls = [
        'https://www.terra.com.br/noticias/ciencia/espaco/maior-robo-da-historia-da-nasa-posa-com-sucesso-em-marte,d0b96292e692eeb34f549f20afbe358e79kr2qqh.html'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SeleniumRequest(url=url, callback=self.parse_target)

    def parse(self, response):
        driver = response.request.meta['driver']

        for i in range(0, 15):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight*0.8);")
            time.sleep(0.5)
        time.sleep(2.5)
        tree = lxml.html.fromstring(driver.page_source)
        target_urls = tree.xpath(
            '//a[@class="main-url text" or @class="text"]/@href')
        self.log(f"Collected {len(target_urls)} URLs")
        for target_url in target_urls:
            if target_url == r"https://www.terra.com.br/noticias/ciencia/espaco/maior-robo-da-historia-da-nasa-posa-com-sucesso-em-marte,d0b96292e692eeb34f549f20afbe358e79kr2qqh.html":
                yield SeleniumRequest(url=target_url,
                                      callback=self.parse_target)

    def parse_target(self, response):
        driver = response.request.meta['driver']

        num_scrolls = 3
        scroll_delay = 1
        page_divisions = 10
        for i in range(1, num_scrolls + 1):
            for j in range(1, page_divisions + 1):
                driver.execute_script(
                    f"window.scrollTo(0,document.body.scrollHeight * {j}/{page_divisions})"
                )
                time.sleep(scroll_delay / page_divisions)
        for _ in range(4):
            driver.execute_script(center_script)
            time.sleep(4)

        time.sleep(3)
        content = driver.execute_script(
            "return document.getElementsByTagName('html')[0].innerHTML")
        # print(driver.execute_script("document.getElementById('social-comments').getElementsByTagName('iframe')[0].contentWindow.document.body.innerHTML"))
        tree = lxml.html.fromstring(content)
        title = None
        subtitle = None
        autor = None
        date = None
        content = None
        comments = None

        comments = tree.xpath("//div[@class='_2pi8']//span[@class='_5mdd']")
        driver.switch_to.frame(driver.find_element_by_css_selector("#social-comments iframe"))
        facebook_process(driver)
        comments = lxml.html.fromstring(driver.page_source)

        comments = comments.xpath("*[@class='_3-8y _5nz1 clearfix']//*[class='_5mdd']")

        yield {
            'title': title,
            'subtitle': subtitle,
            'autor': autor,
            'date': date,
            'text': content,
            'comments': comments
        }
