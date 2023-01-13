import pymongo
import time
import certifi

import main

ca = certifi.where()


class PrintColors:
    INFO = '\033[94m'
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


while True:
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    with client:
        db = client.wjjcn
        checker = db.admin_page_settings.find()
        update_checker = db.admin_page_settings

        query = {"scrape_now": True}
        values_to_update = {"$set": {"scrape_now": False}}

        for item in checker:
            print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + str(item['scrape_now']) + ", no scraping...")

            if item['scrape_now']:
                print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + str(item['scrape_now']) + ", going to scrape!")
                main.main()
                update_checker.update_one(query, values_to_update)

    time.sleep(1)
