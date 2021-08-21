import pymongo
def start_db():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client.news
    # db.publications.create_index([('url', pymongo.ASCENDING)],unique=True)
    # db.apps.create_index([('appid', pymongo.ASCENDING)],unique=True)
    # db.reviews.create_index([('recommendationid', pymongo.ASCENDING)],unique=True)

    return db
