# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Publication(scrapy.Item):
    title = scrapy.Field()
    subtitle = scrapy.Field()
    author = scrapy.Field()
    last_modification = scrapy.Field()
    text = scrapy.Field()
    obtained = scrapy.Field()
    main_image = scrapy.Field()
    read_time = scrapy.Field()
    url = scrapy.Field()
    key_words = scrapy.Field()

class Pessoa(scrapy.Item):
    profile_image = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()

class Author(Pessoa):
    key_words = scrapy.Field()
    description = scrapy.Field()
    

