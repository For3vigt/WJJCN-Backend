from datetime import datetime
from typing import re

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import pymongo
import sys
import re
import certifi

import compare

ca = certifi.where()

brands = []
products = []
product_urls = []
complete_product = []
internal_urls = set()
read_links = []
to_scrape = set()
not_found = set()
already_scraped = []
products_with = []
retailers = []
brands_with = []
startup_retailer_ids = []

error_object_id = ''
domain_url = ""

first_url = ""
total_urls_visited = 0
timeout_counter = 0

timeout_retry = 15
request_timeout_in_seconds = 5


class PrintColors:
    INFO = '\033[94m'
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


''' 
    WEBCRAWLER
'''


def is_valid(url):
    # Checks whether `url` is a valid URL.
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def check_if_url_starts_with_domain(domain, linke):
    global new_domain
    global new_link

    new_domain = domain
    new_link = linke

    if "https://" in new_domain or "https://" in new_link:
        new_domain = new_domain.replace("https://", "")
        new_link = new_link.replace("https://", "")

    if "www." in new_domain or "www." in new_link:
        new_domain = new_domain.replace("www.", "")
        new_link = new_link.replace("www.", "")

    result = re.findall(new_domain, new_link)
    if result != []:
        return True
    else:
        return False


def pause_and_resume_script():
    print("Pausing program \nPlease press enter")
    global timeout_counter

    run = True
    while run == True:
        try:
            # Loop Code Snippet
            val = input()
            val = int(val)
        except ValueError:
            print("""~~~~~~~Code interrupted~~~~~~~ \n Press 1 to resume \n Press 2 to quit """)
            res = input()
            if res == "1":
                timeout_counter = 0
                print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + " resuming code")
                run = False
            if res == "2":
                sys.exit()


def get_url(url):
    global timeout_counter
    counter = timeout_counter

    html = requests

    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    if counter != timeout_retry:
        try:
            html = requests.get(url, headers=agent, timeout=request_timeout_in_seconds).text

            if html != requests:
                soup = BeautifulSoup(html, "html.parser", from_encoding="iso-8859-1")
                return soup
            else:
                get_url(url)
        except:
            error_handler(error_object_id, "[ERROR] An error occurred. Please check your internet connection.", 'link_crawling')
            print(PrintColors.FAIL + "[ERROR]" + PrintColors.ENDC + " An error occurred. Please check your internet connection.")
            counter += 1
            timeout_counter = counter
            get_url(url)
    else:
        pause_and_resume_script()
        timeout_counter = 0
        get_url(url)

        if html != requests:
            soup = BeautifulSoup(html, "html.parser", from_encoding="iso-8859-1")
            return soup
        else:
            get_url(url)


# the method below calls a few methods above to find all links on a page and then checks if they are valid
def get_all_website_links(url):
    if "<" not in str(url):
        # all URLs of on url that is being checked
        urls = set()

        soup = get_url(url)

        try:
            # A loop that loops over all a tags on the webpage that is being checked and then finds all href tags
            for a_tag in soup.findAll("a"):
                href = a_tag.attrs.get("href")

                if href == "" or href is None:
                    continue
                if href.startswith("#"):
                    continue
                if "https://" not in href:
                    if not href.startswith("/"):
                        href = "/" + href
                if "https://www." not in href:
                    if "https://" not in href:
                        if not href.startswith("/"):
                            href = "/" + href

                href = urljoin(url, href)
                # checks if the given url starts with the correct domain else it goes to the next link on the page
                if not check_if_url_starts_with_domain(first_url, href):
                    continue
                # if the url doesn't end with a "/" an "/" will be added to the link
                if not href.endswith("/"):
                    href = href + "/"
                # if the url starts with a space (" ") it will remove the space (" ") form the url
                if href.startswith(" "):
                    href = href.lstrip(' ')
                # if the url contains a query of contains "tel:" it'll be skipped, and it'll go to the next link on the page
                if "#" in href or "tel:" in href:
                    continue
                # if the url already has been scraped it'll be skipped, and it'll go to the next link on the page
                if href in internal_urls:
                    continue
                # a second check to see if the found link does start with the domain, then we'll add the link to the found
                # internal links set
                if check_if_url_starts_with_domain(first_url, href):
                    urls.add(href)
                    internal_urls.add(href)
                # if the found link starts with an "/" we'll add the domain url so every link is a correct link, and we
                # don't have to check where the link came form
                if href.startswith("/"):
                    href = domain_url + href
                    urls.add(href)
                    internal_urls.add(href)
                continue
        except AttributeError:
            error_handler(error_object_id, "[ERROR] Could not crawl the given URL.", 'link_crawling')
            print(PrintColors.FAIL + "[ERROR]" + PrintColors.ENDC + " Could not crawl the given URL.")
    return urls


def crawl(url):
    global domain_url
    global domain_name

    # if statement finds the "main" link, it strips all tags after .com
    if domain_url == "":
        stripped_domain = re.findall("(\w+://[\w\-\.]+)", url)
        domain_url = stripped_domain[0]

    # finds the domain name, it strips https from the url to just get the domain (ex https://www.google.com/ -> google.com)
    domain_name = re.match(r'(?:\w*://)?(?:.*\.)?([a-zA-Z-1-9]*\.[a-zA-Z]{1,}).*', url).groups()[0]

    # after finding the domain name it changes . to - to remove conflict in saving it in the explorer
    if "." in domain_name:
        domain_name = domain_name.replace(".", "-")

    global total_urls_visited
    total_urls_visited += 1

    links = get_all_website_links(url)

    print(f"{PrintColors.INFO}[INFO]{PrintColors.ENDC} Crawling: {url} ")

    for link in links:
        # if total_urls_visited > 200:
        #    break
        if check_if_url_starts_with_domain(url, link):
            crawl(link)
        else:
            continue


''' 
    END WEBCRAWLER
'''


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


# This function gets all products that are in the database. Then it will check if a product is in a URL found by the crawler.
# If that is the case, the complete product and URL will be sent to the Comparer.
def find_product_in_urls(url):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    start_time = datetime.now()

    selected_retailer = ""
    selected_retailer_url = ""
    brand_temp_list = []

    with client:
        db = client.wjjcn
        retailer_table = db.retailers.find()

        # Gets all the data necessary for the retailers.
        for retailer in retailer_table:
            if retailer['base_url'] in url:
                selected_retailer = retailer['_id']
                selected_retailer_url = retailer['base_url']
                retailers.append(retailer['base_url'])

        products_per_retailer_table = db.products.find({"retailer": selected_retailer})

        # Gets all the products with the selected retailers.
        for product in products_per_retailer_table:
            if product['retailer'] == selected_retailer:
                brand_temp_list.append(product['brand'])
                product['name'] = re.sub(' +', '-', product['name'])
                product['name'] = re.sub('-+', '-', product['name'])
                product_urls.append(product['product_url'])
                products.append(product['name'])
                complete_product.append(product)
                if product['product_url'] != '':
                    compare.main(product, product['product_url'], error_object_id)
                    already_scraped.append(product['name'])

        brands_table = db.brands.find()

        # Gets all the brands in the database.
        for brand in brands_table:
            for temp_brand in brand_temp_list:
                if brand["_id"] == temp_brand:
                    brands.append(brand["name"])

    client.close()

    for link in internal_urls:
        read_links.append(link)

    # Loop through all found URLs by the crawler.
    for j in range(len(list(read_links))):
        i = 0
        # Loop through all the products per retailer.
        while i < len(list(products)):
            if product_urls[i] == '':
                if check_if_url_starts_with_domain(selected_retailer_url, read_links[j]):
                    # Split the URLs and filter them by a forward slash and an empty space.
                    split_link = read_links[j].split("/")
                    filtered_link = list(filter(None, split_link))
                    compare_once = False

                    # Loop through the split URLs
                    for x in range(len(filtered_link)):
                        # Loop through all the brands per retailer.
                        for retailer_table in range(len(brands)):
                            # Replace all white spaces with dashes so that the brand as the same structure as a URL.
                            brands_with.append(brands[retailer_table].replace(" ", "-"))
                            # Check if a brand is somewhere in the split URLs
                            if brands_with[retailer_table].lower() in filtered_link[x]:
                                correct_count = 0
                                percentage = 86

                                # Split the products and URLs for easy looping.
                                product_in_database = products[i].lower().split("-")
                                found_product_url = filtered_link[x].split("-")

                                # Remove unnecessary information from the URLs found in Jumbo.
                                if 'BLK' in found_product_url[-1] or 'PAK' in found_product_url[-1] or 'TRL' in found_product_url[-1]:
                                    del found_product_url[-1]

                                # Remove units in the products.
                                if 'ml' in product_in_database[-1] or 'l' in product_in_database[-1]:
                                    del product_in_database[-1]

                                # Loop through the double split URL and product.
                                for p2 in range(len(found_product_url)):
                                    for p in range(len(product_in_database)):
                                        # Check if the one of the indexes of the product is in one of the indexes of the URL.
                                        if product_in_database[p] in found_product_url[p2]:
                                            # Check if one of the indexes of the product is equal to one of the indexes of the URL.
                                            if product_in_database[p] == found_product_url[p2]:
                                                correct_count += 1
                                                # Check if the counter has the same length as the length of the split product from the database.
                                                if correct_count == len(product_in_database):
                                                    # If the end of the URL as numbers in it. Set the threshold lower.
                                                    if has_numbers(found_product_url[-1]):
                                                        percentage = 76
                                                    # Check if the percentage correct from the product and the URL are greater than the threshold.
                                                    if (len(product_in_database) / len(found_product_url)) * 100 > percentage:
                                                        # Compare only once!
                                                        if not compare_once:
                                                            # Check if the URL from the product in the database is equal to the found URL.
                                                            if product_urls[i] == read_links[j]:
                                                                to_scrape.add("Product: " + products[i] + "\nURL: " + product_urls[i])
                                                                # Comparer gets the URL from the product in the database.
                                                                compare.main(complete_product[i], product_urls[i], error_object_id)
                                                                compare_once = True
                                                                break
                                                            # Check if the URL from the product in the database is empty.
                                                            elif product_urls[i] == "":
                                                                update_product_url(complete_product[i]['_id'], read_links[j])
                                                                to_scrape.add("Product: " + products[i] + "\nURL: " + read_links[j])
                                                                # Comparer gets the found URL.
                                                                compare.main(complete_product[i], read_links[j], error_object_id)
                                                                compare_once = True
                                                                break
                                                            else:
                                                                to_scrape.add("Product: " + products[i] + "\nURL: " + read_links[j])
                                                                # Comparer gets the found URL.
                                                                compare.main(complete_product[i], read_links[j], error_object_id)
                                                                compare_once = True
                                                                break
                                                    break
            i += 1

    if len(to_scrape) > 0 or len(already_scraped) > 0:
        for product_url in to_scrape:
            print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + " " + product_url)
        for scraped in already_scraped:
            print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + " " + scraped)

        end_time = datetime.now()
        print(PrintColors.INFO + '[INFO]' + PrintColors.ENDC + ' Link comparer duration: {}'.format(end_time - start_time))
    else:
        print(PrintColors.WARNING + "[WARN]" + PrintColors.ENDC + " No products found in the scraped URL's...")
        end_time = datetime.now()
        print(PrintColors.INFO + '[INFO]' + PrintColors.ENDC + ' Link comparer duration: {}'.format(end_time - start_time))


def update_product_url(product_id, product_url):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    # Update the URL of the given product_id
    with client:
        db = client.wjjcn
        products_table = db.products

        query = {"_id": product_id}
        values_to_update = {"$set": {"product_url": product_url}}

        products_table.update_one(query, values_to_update)

    client.close()


def get_url_from_database():
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    scrape_url = []
    global startup_retailer_ids

    with client:
        db = client.wjjcn
        retailers_table = db.retailers.find()

        # Get every scrape able URL inside the database if the retailer has scrape enabled.
        for retailer in retailers_table:
            if retailer["scrape"] == "true":
                scrape_url.append(retailer["url_to_scrape"])
                startup_retailer_ids.append(retailer['_id'])
            else:
                print(PrintColors.WARNING + "[WARN]" + PrintColors.ENDC + " Retailer '" + retailer["name"] + "' is disabled for scraping.")

    client.close()

    return scrape_url


def create_log_on_init(retailer_url):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    global error_object_id
    error_object_id = ''

    # Create a log for the given retailer_url
    with client:
        db = client.wjjcn
        retailers_table = db.retailers.find_one({'scrape': 'true', 'url_to_scrape': retailer_url})

        logs_table = db.logs

        new_log = {
            'date_run': str(datetime.now().date()),
            'steps': {
                'link_crawling': {
                    'status': True,
                    'error': ''
                },
                'link_check': {
                    'status': True,
                    'error': ''
                },
                'product_fetch_compare': {
                    'status': True,
                    'error': ''
                },
                'save_to_database': {
                    'status': True,
                    'error': ''
                }
            },
            'retailer': retailers_table['_id']
        }

        # Get the id from the inserted record for error handling.
        get_error_object_id = logs_table.insert_one(new_log)
        error_object_id = get_error_object_id.inserted_id

    client.close()


def check_date_runned(retailer_url):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    # Check if the script has already completed once on the same date for the given retailer_url
    with client:
        db = client.wjjcn
        retailers_table = db.retailers.find_one({'scrape': 'true', 'url_to_scrape': retailer_url})
        logs_table = db.logs.find_one({'date_run': str(datetime.now().date()), 'retailer': retailers_table['_id']})

        if logs_table is None:
            return "ok"
        elif logs_table['date_run'] == str(datetime.now().date()):
            return "exists"
        else:
            return "ok"


def error_handler(error_id, message, step):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    # Update the log with the given error_id and step with a message.
    with client:
        db = client.wjjcn
        update_logs_table = db.logs

        query = {"_id": error_id}
        values_to_update = {"$set": {'steps.' + step: {
            "status": False,
            "error": message
        }}}

        update_logs_table.update_one(query, values_to_update)

    client.close()


def clear_lists():
    # Clear every global list and set when the script runs again.
    brands.clear()
    products.clear()
    product_urls.clear()
    complete_product.clear()
    internal_urls.clear()
    read_links.clear()
    to_scrape.clear()
    not_found.clear()
    products_with.clear()
    retailers.clear()
    brands_with.clear()


def crawler(scrape_url):
    try:
        clear_lists()
        create_log_on_init(scrape_url)

        first_url = scrape_url
        start_time = datetime.now()

        crawl(first_url)

        # Save the URLs in a .txt for debugging
        # with open('links' + domain_name + '.txt', 'w') as f:
        #     for link in internal_urls:
        #         f.write(link)
        #         f.write('\n')
        #
        # f.close()

        print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + " Total links:", len(internal_urls))

        end_time = datetime.now()
        print(PrintColors.INFO + '[INFO]' + PrintColors.ENDC + ' Duration: {}'.format(end_time - start_time))

        find_product_in_urls(first_url)
    except BaseException as e:
        error_handler(error_object_id, "[ERROR] link is not valid. Exception: " + str(e), 'link_crawling')
        print(PrintColors.FAIL + "[ERROR]" + PrintColors.ENDC + " link is not valid. Exception: " + str(e))


''' 
    PROGRAM
'''


def main():
    try:
        for scrape_url in get_url_from_database():
            if scrape_url != "":
                if check_date_runned(scrape_url) == "exists":
                    print(
                        PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " The scraper as already completed once with this retailer today.\nIf you continue a new history entry will be created.\nDo you want to continue? y/n")
                    check_date = input()
                    if check_date == "y":
                        crawler(scrape_url)
                    elif check_date == "n":
                        print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Goodbye")
                        sys.exit()
                    else:
                        print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Goodbye")
                        sys.exit()
                else:
                    crawler(scrape_url)

            else:
                sys.exit()
    except ValueError as e:
        sys.exit(e)
    finally:
        print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Do you want to run the script again? y/n")
        key_input = input()

        if key_input == "y":
            main()
        elif key_input == "n":
            print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Goodbye")
            sys.exit()
        else:
            print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Goodbye")
            sys.exit()


''' 
    END PROGRAM
'''

main()
