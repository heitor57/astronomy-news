import scrapy 
import time
from bs4 import BeautifulSoup
import re
from scrapy_splash import SplashRequest 
script = """
function main(splash)
    local num_scrolls = 10
    local scroll_delay = 1.0

    local scroll_to = splash:jsfunc("window.scrollTo")
    local get_body_height = splash:jsfunc(
        "function() {return document.body.scrollHeight;}"
    )
    assert(splash:go(splash.args.url))
    splash:wait(splash.args.wait)

    for _ = 1, num_scrolls do
        scroll_to(0, get_body_height())
        splash:wait(scroll_delay)
    end        
    return splash:html()
end
"""

class IGSpider(scrapy.Spider):
    name = "ig"
    allowed_domains=['ultimosegundo.ig.com.br']
    start_urls =['https://ultimosegundo.ig.com.br/colunas/astronoticias/']

    def start_requests(self): 
        for url in self.start_urls: 
            yield SplashRequest(url, self.parse, 
                endpoint='render.html', 
                args={'wait': 10.0}, 
           ) 


    def parse_target(self,response):
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find("h1", id="noticia-titulo-h1").string
        subtitle = soup.find("h2", id="noticia-olho").string
        autor = soup.find("strong", class_="complemento-credito").string
        autorlink = None
        readtime = None
        image = None
        date = soup.find("time", itemprop="datePublished").string
        #image = soup.find("div", class_="image").get('src')
        
        texts = soup.find("div", id="noticia").find_all("p")
        content= ""
        for i in texts :
            if i.string != None:    
                content += i.text
                content += "\n"
        tags = None

        yield {'title':title,'subtitle':subtitle,'autor':autor,'date':date,'text':content}
        
    def parse(self, response):
        urls = response.xpath('//a/@href').getall()

        pattern = re.compile(r'\?p=[0-9]+')

        urls = [i for i in urls if pattern.match(i)]
        target_urls = response.xpath("//a[contains(@class, 'empilhaDesc')]/@href").getall()

        for target_url in target_urls:
            yield SplashRequest(target_url, self.parse_target, 
                    endpoint='render.html', 
                    args={'wait': 10.0,'lua_source':script})

        # self.log(urls)
        if len(urls) > 0:
            for url in urls:
                url = response.urljoin(url)
                yield SplashRequest(url, self.parse, 
                    endpoint='render.html', 
                    args={'wait': 10.0})
