import scrapy 
from selenium.webdriver.support import expected_conditions as EC
import selenium
import time
from bs4 import BeautifulSoup
import re
from scrapy_splash import SplashRequest 
from scrapy.utils.response import open_in_browser
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import lxml
import urllib
import selenium
from .facebook import facebook_process


script = """
function main(splash)
        local num_scrolls = 10
        local scroll_delay = 1

        local scroll_to = splash:jsfunc("window.scrollTo")
        local get_body_height = splash:jsfunc(
            "function() {return document.body.scrollHeight;}"
        )
        assert(splash:go(splash.args.url))
        splash:wait(splash.args.wait)

        for _ = 1, num_scrolls do
            local height = get_body_height()
            for i = 1, 10 do
                scroll_to(0, height * i/10)
                splash:wait(scroll_delay/10)
            end
        end        

        return splash:html()
end
"""

class IGSpider(scrapy.Spider):
    name = "ig"
    allowed_domains=['ultimosegundo.ig.com.br']
    # start_urls =['https://ultimosegundo.ig.com.br/colunas/astronoticias/']
    start_urls =['https://ultimosegundo.ig.com.br/colunas/astronoticias/2019-10-25/estrelas-binarias-em-uma-rosquinha-cosmica.html']

    def start_requests(self): 
        for url in self.start_urls: 
            # yield SeleniumRequest(url=url, callback=self.parse)
            yield SeleniumRequest(url=url, callback=self.parse_target)


    def parse_target(self,response):
        driver = response.request.meta['driver']
        time.sleep(6)
        comments_element = driver.find_element_by_xpath("//h4[contains(text(), 'Comentários')]")
        for _ in range(7):
            driver.execute_script("arguments[0].scrollIntoView()",comments_element)
            time.sleep(1)
        # facebook
        driver.switch_to.frame(driver.find_element_by_css_selector(".fb-commets-content iframe"))
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID, 'facebook')))

        driver.switch_to.default_content()


        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find("h1", id="noticia-titulo-h1").string
        subtitle = soup.find("h2", id="noticia-olho").string
        autor = soup.find("strong", class_="complemento-credito").string
        autorlink = None
        readtime = None
        comments = None
        image = None
        date = soup.find("time", itemprop="datePublished").string
        #image = soup.find("div", class_="image").get('src')
        
        texts = soup.find("div", id="noticia").find_all("p")

        driver.switch_to.frame(driver.find_element_by_css_selector(".fb-commets-content iframe"))
        facebook_process(driver)

        comments = driver.page_source

        from scrapy.http.response.html import HtmlResponse
        ht = HtmlResponse(url=response.url, body=driver.page_source, encoding="utf-8", request=response.request)
        open_in_browser(ht)
        # comments = lxml.html.fromstring(driver.page_source)

        # comments = comments.xpath("*[@class='_3-8y _5nz1 clearfix']//*[class='_5mdd']")
        # comments = soup.find("div",id="comentarios").find_all("span",class_="_5mdd")
        content= ""
        for i in texts :
            if i.string != None:    
                content += i.text
                content += "\n"
        tags = None

        yield {'title':title,'subtitle':subtitle,'autor':autor,'date':date,'text':content,'comments':comments}
        
    def parse(self, response):
        driver = response.request.meta['driver']
        time.sleep(3)
        tree = lxml.html.fromstring(driver.page_source)
        urls = tree.xpath('//a/@href')

        pattern = re.compile(r'\?p=[0-9]+')

        urls = [i for i in urls if pattern.match(i)]
        target_urls = tree.xpath("//a[contains(@class, 'empilhaDesc')]/@href")

        for target_url in target_urls:
            yield SeleniumRequest(url=target_url, callback=self.parse_target)

        if len(urls) > 0:
            for url in urls:
                url = response.urljoin(url)
                yield SeleniumRequest(url=url, callback=self.parse)
