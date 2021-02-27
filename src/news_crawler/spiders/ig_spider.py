import scrapy 
import time
from bs4 import BeautifulSoup
import re
from scrapy_splash import SplashRequest 
from scrapy.utils.response import open_in_browser
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

        local scroll_comentarios = splash:jsfunc([[
        function() {document.getElementById('comentarios').scrollIntoView();}
        ]])
        scroll_comentarios();
        splash:wait(5)

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
    start_urls =['https://ultimosegundo.ig.com.br/colunas/astronoticias/']

    def start_requests(self): 
        for url in self.start_urls: 
            yield SplashRequest(url, self.parse, 
                endpoint='render.html', 
                args={'wait': 10.0}, 
           ) 


    def parse_target(self,response):

        # from scrapy.http.response.html import HtmlResponse
        # ht = HtmlResponse(url=response.url, body=response.body, encoding="utf-8", request=response.request)
        # open_in_browser(ht)
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
        comments = soup.find("div",id="comentarios").find_all("span",class_="_5mdd")
        content= ""
        for i in texts :
            if i.string != None:    
                content += i.text
                content += "\n"
        tags = None

        yield {'title':title,'subtitle':subtitle,'autor':autor,'date':date,'text':content,'comments':comments}
        
    def parse(self, response):
        urls = response.xpath('//a/@href').getall()

        pattern = re.compile(r'\?p=[0-9]+')

        urls = [i for i in urls if pattern.match(i)]
        target_urls = response.xpath("//a[contains(@class, 'empilhaDesc')]/@href").getall()

        for target_url in target_urls:
            # if target_url == 'https://ultimosegundo.ig.com.br/colunas/astronoticias/2019-10-25/estrelas-binarias-em-uma-rosquinha-cosmica.html':
            yield SplashRequest(target_url, self.parse_target, 
                    endpoint='execute', 
                    args={'wait': 0.2,'lua_source':script})

        # self.log(urls)
        if len(urls) > 0:
            for url in urls:
                url = response.urljoin(url)
                yield SplashRequest(url, self.parse, 
                    endpoint='render.html', 
                    args={'wait': 10.0})
