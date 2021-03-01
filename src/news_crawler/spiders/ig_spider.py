import scrapy 
from selenium.webdriver.support import expected_conditions as EC
from ..items import Publication, Person
import selenium
import json
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

from pyparsing import *


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
    # start_urls =['https://ultimosegundo.ig.com.br/colunas/astronoticias/2019-10-25/estrelas-binarias-em-uma-rosquinha-cosmica.html']
    start_urls =['https://ultimosegundo.ig.com.br/colunas/astronoticias/2019-07-02/eclipse-solar-2019.html']

    def start_requests(self): 
        self.expr = Literal('"comments"')+Literal(':')+nestedExpr('{','}')
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
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".fb-commets-content iframe")))
        driver.switch_to.frame(driver.find_element_by_css_selector(".fb-commets-content iframe"))
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID, 'facebook')))
        # WebDriverWait(driver,20).until(EC.presence_of_element_located((By.ID, 'facebook')))

        driver.switch_to.default_content()


        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find("h1", id="noticia-titulo-h1").string
        subtitle = soup.find("h2", id="noticia-olho").string
        author = soup.find("strong", class_="complemento-credito").string
        authorlink = None
        readtime = None
        comments = None
        image = None
        date = soup.find("time", itemprop="datePublished").string
        #image = soup.find("div", class_="image").get('src')
        
        texts = soup.find("div", id="noticia").find_all("p")

        driver.switch_to.frame(driver.find_element_by_css_selector(".fb-commets-content iframe"))
        facebook_process(driver)

        comments = driver.page_source

        # from scrapy.http.response.html import HtmlResponse
        # ht = HtmlResponse(url=response.url, body=driver.page_source, encoding="utf-8", request=response.request)
        # open_in_browser(ht)
        self.log("Started Scanning comments")
        # self.expr.scanString(driver.page_source)
        string = originalTextFor(self.expr).searchString(driver.page_source).asList()
        if len(string)>0:
            string = string[0][0]
            comments_json = json.loads("{"+string+"}")["comments"]
            self.log("Finished Scanning comments")
            # comments_ids = set(comments_json['commentsIDs'])
            comments_ = []
            objects = []
            id_url = {}
            users = []
            og_object_id = None
            for k,v in comments_json['idMap'].items():
                if v['type'] == 'ogobject':
                    if og_object_id is not None:
                        raise SystemError
                    og_object_id = v['id']

                if v['type'] == 'user' or v['type'] == 'ogobject':
                    if v['uri'] == '':
                        id_url[v['id']] = v['thumbSrc']
                    else:
                        id_url[v['id']] = v['uri']
                if v['type'] == 'user':
                    yield Person(url=v['uri'],
                            name=v['name'],
                            profile_image=v['thumbSrc'])
            comments = []
            def extract_comments(comment):
                extracted_comment = {
                        'author': id_url[comment['authorID']],
                        # 'name': comment['name'],
                        # 'target': id_url[comment['targetID']],
                        'text': comment['body']['text'],
                        'timestamp': comment['timestamp']['time'],
                        }
                try:
                    extracted_comment['replies'] = [extract_comments(comments_json['idMap'][i]) for i in comment['public_replies']['commentIDs']]
                except Exception as e:
                    pass
                return extracted_comment

            for k,v in comments_json['idMap'].items():
                if v['type'] == 'comment' and v['targetID'] in og_object_id:
                    comment = extract_comments(v)
                    comments.append(comment)

            # comments = json.dumps(comments_json,indent=2)
            # print( json.dumps(comments_json,indent=2))
            # print(comments)

        # print(string)
        # comments = lxml.html.fromstring(driver.page_source)

        # comments = comments.xpath("*[@class='_3-8y _5nz1 clearfix']//*[class='_5mdd']")
        # comments = soup.find("div",id="comentarios").find_all("span",class_="_5mdd")
        content= ""
        for i in texts :
            if i.string != None:    
                content += i.text
                content += "\n"
        tags = None

        yield Publication(title=title,subtitle=subtitle,author=authorlink,text=content,comments=comments)
        # yield {'title':title,'subtitle':subtitle,'author':author,'date':date,'text':content,'comments':comments}
        
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
