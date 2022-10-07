import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import sys
import re

sys.setrecursionlimit(8000)

internal_urls = set()
domain_url = ""


def is_valid(url):
    # Checks whether `url` is a valid URL.
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def check_if_url_starts_with_domain(domain, link):
    urlToTest = "^" + domain
    result = re.findall(urlToTest, link)
    if result != []:
        return True
    else:
        return False


def get_url(url):
    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    html = requests.get(url, headers=agent).text
    soup = BeautifulSoup(html, "html.parser", from_encoding="iso-8859-1")
    return soup


def get_all_website_links(url):
    # Returns all URLs that is found on `url` in which it belongs to the same website
    if "<" not in str(url):
        # all URLs of `url`
        urls = set()

        soup = get_url(url)

        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")

            if href == "" or href is None:
                # href empty tag
                continue
            # if "kookschrift" in href or "recept" in href or "allerhande" in href or "inspiratie" in href:
            #     continue
            if href.startswith("#"):
                continue

            href = urljoin(url, href)

            if not check_if_url_starts_with_domain(domain_url, href):
                continue
            if not href.endswith("/"):
                href = href + "/"
            if href.startswith(" "):
                href = href.lstrip(' ')
            if "?" in href or "tel:" in href:
                continue
            if href in internal_urls:
                # already in the set
                continue
            if check_if_url_starts_with_domain(domain_url, href):
                urls.add(href)
                internal_urls.add(href)
            if href.startswith("/"):
                href = domain_url + href
                urls.add(href)
                internal_urls.add(href)
            continue
    return urls

# number of urls visited so far will be stored here
total_urls_visited = 0


def crawl(url):
    global domain_url
    global domain_name

    if domain_url == "":
        strippedDomain = re.findall("(\w+://[\w\-\.]+)", url)
        domain_url = strippedDomain[0]

    domain_name = re.match(r'(?:\w*://)?(?:.*\.)?([a-zA-Z-1-9]*\.[a-zA-Z]{1,}).*', url).groups()[0]

    if "." in domain_name:
        domain_name = domain_name.replace(".", "-")
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1

    links = get_all_website_links(url)

    print(f"[*] Crawling: {url}")

    sleepCounter = 0

    for link in links:
        if total_urls_visited > 4000:
            break
        if sleepCounter == 10:
            time.sleep(1)
            sleepCounter = 0
        if check_if_url_starts_with_domain(domain_url, link):
            time.sleep(0.2)
            crawl(link)
        else:
            continue


crawl("https://ah.nl")

print("[/---------------------------/]")
print(len(internal_urls))
print("[/---------------------------/]")

with open('links'+domain_name+'.txt', 'w') as f:
    for link in internal_urls:
        print("found link: ", link)
        f.write(link)
        f.write('\n')

f.close()

print("[+] Total links:", len(internal_urls))
