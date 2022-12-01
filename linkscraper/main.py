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
products_with = []
retailers = []
brands_with = []

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


def find_product_in_urls(url):
    start_time = datetime.now()

    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    selected_retailer = ""
    selected_retailer_url = ""
    brand_temp_list = []

    with client:
        db = client.wjjcn
        retailer_table = db.retailers.find()

        for retailer in retailer_table:
            if retailer['base_url'] in url:
                selected_retailer = retailer['_id']
                selected_retailer_url = retailer['base_url']
                retailers.append(retailer['base_url'])

        products_per_retailer_table = db.products.find({"retailer": selected_retailer})

        for product in products_per_retailer_table:
            if product['retailer'] == selected_retailer:
                brand_temp_list.append(product['brand'])
                product['name'] = re.sub(' +', '-', product['name'])
                product['name'] = re.sub('-+', '-', product['name'])
                product_urls.append(product['product_url'])
                products.append(product['name'])
                complete_product.append(product)

        brands_table = db.brands.find()

        for brand in brands_table:
            for temp_brand in brand_temp_list:
                if brand["_id"] == temp_brand:
                    brands.append(brand["name"])

    client.close()

    # with open('linksjumbo-com.txt') as f:
    #     for line in f.readlines():
    #         read_links.append(line.strip())
    #
    #     f.close()

    compare_once = False

    for link in internal_urls:
        read_links.append(link)

    for j in range(len(list(read_links))):
        i = 0
        while i < len(list(products)):
            if check_if_url_starts_with_domain(selected_retailer_url, read_links[j]):
                split_link = read_links[j].split("/")
                filtered_link = list(filter(None, split_link))
                compare_once = False

                for x in range(len(filtered_link)):

                    for retailer_table in range(len(brands)):
                        brands_with.append(brands[retailer_table].replace(" ", "-"))

                        if brands_with[retailer_table].lower() in filtered_link[x]:
                            correct_count = 0
                            percentage = 86

                            product_in_database = products[i].lower().split("-")
                            found_product_url = filtered_link[x].split("-")

                            if 'BLK' in found_product_url[-1] or 'PAK' in found_product_url[-1] or 'TRL' in found_product_url[-1]:
                                del found_product_url[-1]

                            if 'ml' in product_in_database[-1] or 'l' in product_in_database[-1]:
                                del product_in_database[-1]

                            for p2 in range(len(found_product_url)):
                                for p in range(len(product_in_database)):
                                    if product_in_database[p] in found_product_url[p2]:
                                        if product_in_database[p] == found_product_url[p2]:
                                            correct_count += 1
                                            if correct_count == len(product_in_database):
                                                if has_numbers(found_product_url[-1]):
                                                    percentage = 76
                                                if (len(product_in_database) / len(found_product_url)) * 100 > percentage:
                                                    if not compare_once:
                                                        if product_urls[i] == read_links[j]:
                                                            to_scrape.add("Product: " + products[i] + "\nURL: " + product_urls[i])
                                                            compare.main(complete_product[i], product_urls[i], error_object_id)
                                                            compare_once = True
                                                            break
                                                        else:
                                                            update_product_url(complete_product[i]['_id'], read_links[j])
                                                            to_scrape.add("Product: " + products[i] + "\nURL: " + read_links[j])
                                                            compare.main(complete_product[i], read_links[j], error_object_id)
                                                            compare_once = True
                                                            break
                                                break
            i += 1

    if len(to_scrape) > 0:
        for product_url in to_scrape:
            print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + " " + product_url)

        end_time = datetime.now()
        print(PrintColors.INFO + '[INFO]' + PrintColors.ENDC + ' Link comparer duration: {}'.format(end_time - start_time))
    else:
        print(PrintColors.WARNING + "[WARN]" + PrintColors.ENDC + " No products found in the scraped URL's...")
        end_time = datetime.now()
        print(PrintColors.INFO + '[INFO]' + PrintColors.ENDC + ' Link comparer duration: {}'.format(end_time - start_time))


def update_product_url(product_id, product_url):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

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
    global error_object_id
    error_object_id = ''

    with client:
        db = client.wjjcn
        retailers_table = db.retailers.find()

        for retailer in retailers_table:
            if retailer["scrape"] == "true":
                retailer_id = retailer["_id"]
                scrape_url.append(retailer["url_to_scrape"])

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
                    'retailer': retailer_id
                }

                get_error_object_id = logs_table.insert_one(new_log)
                error_object_id = get_error_object_id.inserted_id
            else:
                print(PrintColors.WARNING + "[WARN]" + PrintColors.ENDC + " Retailer '" + retailer["name"] + "' is disabled for scraping.")

    client.close()

    return scrape_url


def check_date_runned():
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

    with client:
        db = client.wjjcn
        logs_table = db.logs.find()

        for logs in logs_table:
            if logs['date_run'] == str(datetime.now().date()):
                return True


def error_handler(error_id, message, step):
    client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

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


''' 
    PROGRAM
'''


def main():
    try:
        for scrape_url in get_url_from_database():
            if scrape_url != "":
                if check_date_runned():
                    print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " The scraper as already completed once with this retailer today. Do you want to continue? y/n")
                    check_date = input()

                    if check_date == "y":
                        try:
                            clear_lists()

                            first_url = scrape_url
                            start_time = datetime.now()

                            crawl(first_url)

                            with open('links' + domain_name + '.txt', 'w') as f:
                                for link in internal_urls:
                                    # print("found link: ", link)
                                    f.write(link)
                                    f.write('\n')

                            f.close()

                            print(PrintColors.INFO + "[INFO]" + PrintColors.ENDC + " Total links:", len(internal_urls))

                            end_time = datetime.now()
                            print(PrintColors.INFO + '[INFO]' + PrintColors.ENDC + ' Duration: {}'.format(end_time - start_time))

                            find_product_in_urls(first_url)
                        except BaseException as e:
                            error_handler(error_object_id, "[ERROR] link is not valid. Exception: " + str(e), 'link_crawling')
                            print(PrintColors.FAIL + "[ERROR]" + PrintColors.ENDC + " link is not valid. Exception: " + str(e))

                    elif check_date == "n":
                        print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Goodbye")
                        sys.exit()
                    else:
                        print(PrintColors.WARNING + "[SYSTEM]" + PrintColors.ENDC + " Goodbye")
                        sys.exit()
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
# find_product_in_urls("https://www.jumbo.com/producten")
