import requests
import pymongo
import time
import utils
URL = "https://rapidapi.p.rapidapi.com/api/search/NewsSearchAPI"
news = utils.start_db()
page_number = 1
while True:
    # query = "astronomy"
    # query = "planet"
    # query = "space"
    # query = "star"
    # query = "mars"
    # query = "galaxy OR 'comet' OR 'astrophysics' OR 'universe' OR 'astronomer' OR 'observatory' OR 'astrometry' OR 'asteroid' OR 'astrology' OR 'black hole' OR 'solar system' OR 'neutron star' OR 'astronomical object' OR 'supernova' OR 'physical cosmology' OR 'cosmic microwave background radiation' OR 'cosmology' OR 'pulsar' OR 'sun' OR 'milky way' OR 'uranus' OR 'natural science' OR 'chemistry' OR 'nebula' OR 'natural satellite' OR 'earth' OR 'maya civilization' OR 'astronomical' OR 'telescope'"
    # query = "galaxy"
    # query = "comet"
    # query = "astrophysics"
    # query = "astronomer"
    # query = "observatory"
    # query = "astrometry"
    # query = "asteroid"
    # query = "solar system"
    # query = "neutron star"
    # query = "astronomical object"
    # query = "supernova"
    # query = "physical cosmology"
    # query = "cosmic microwave background radiation"
    # query = "cosmology"
    # query = "pulsar"
    # query = "milky way"
    # query = "uranus"
    # query = "nebula"
    # query = "natural satellite"
    query = "telescope"
    page_size = 50
    auto_correct = True
    safe_search = False
    with_thumbnails = True
    from_published_date = ""
    to_published_date = ""

    querystring = {"q": query,
                   "pageNumber": page_number,
                   "pageSize": page_size,
                   "autoCorrect": auto_correct,
                   "safeSearch": safe_search,
                   "withThumbnails": with_thumbnails,
                   "fromPublishedDate": from_published_date,
                   "toPublishedDate": to_published_date}

    response = requests.get(URL, headers=HEADERS, params=querystring).json()

    # print(response)

    total_count = response["totalCount"]
    print("=============")
    print(page_number)
    print(total_count)
    print(len(response["value"]))
    for web_page in response["value"]:
        url = web_page["url"]
        title = web_page["title"]
        description = web_page["description"]
        body = web_page["body"]
        date_published = web_page["datePublished"]
        language = web_page["language"]
        is_safe = web_page["isSafe"]
        provider = web_page["provider"]["name"]

        image_url = web_page["image"]["url"]
        image_height = web_page["image"]["height"]
        image_width = web_page["image"]["width"]

        thumbnail = web_page["image"]["thumbnail"]
        thumbnail_height = web_page["image"]["thumbnailHeight"]
        thumbnail_width = web_page["image"]["thumbnailWidth"]
        news.publications.insert_one({'url':url,'title':title,'description':description, 'body':body,
            'date_published':date_published,
            'language':language,
            'is_safe':is_safe,
            'provider':provider,
            'image_url':image_url,
            'image_height':image_height,
            'image_width':image_width,
            'thumbnail':thumbnail,
            'thumbnail_height':thumbnail_height,
            'thumbnail_width':thumbnail_width,
            })

    if len(response['value']) < page_size:
        break
        # print("Url: {}. Title: {}. Published Date: {}.".format(url, title, date_published))
    page_number+=1
    time.sleep(2)
