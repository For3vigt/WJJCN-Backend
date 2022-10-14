from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import sys
import re

internal_urls = set()
domain_url = ""

first_url = ""
total_urls_visited = 0
timeout_counter = 0

timeout_retry = 15
request_timeout_in_seconds = 5


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


def pause_and_resume_script(url):
    print("Pausing program \nPlease press enter")
    global timeout_counter

    run = True
    while run == True:
        try:
            # Loop Code Snippet
            val = input()
            val = int(val)
        except ValueError:
            print("""~~~~~~~Code interupted~~~~~~~ \n Press 1 to resume \n Press 2 to quit """)
            res = input()
            if res == "1":
                timeout_counter = 0
                print("resuming code")
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
            print("An error occured")
            counter += 1
            timeout_counter = counter
            get_url(url)
    else:
        pause_and_resume_script(url)
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
                if "?" in href or "tel:" in href:
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
            print("Could not crawl the given URL.")
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

    print(f"[*] Crawling: {url}")

    for link in links:
        # if total_urls_visited > 200:
        #    break
        if check_if_url_starts_with_domain(url, link):
            crawl(link)
        else:
            continue


try:
    print("-- Enter the URL you want to crawl --")
    enter_url = input()

    if enter_url != "":
        first_url = enter_url
        start_time = datetime.now()

        crawl(first_url)

        print("[/---------------------------/]")
        print(len(internal_urls))
        print("[/---------------------------/]")

        with open('links' + domain_name + '.txt', 'w') as f:
            for link in internal_urls:
                print("found link: ", link)
                f.write(link)
                f.write('\n')

        f.close()

        print("[+] Total links:", len(internal_urls))

        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))
    if enter_url == "":
        sys.exit()
except ValueError:
    sys.exit()
