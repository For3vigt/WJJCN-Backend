from bs4 import BeautifulSoup
import re
import pymongo
import requests

brands = []
CLEANR = re.compile('<.*?>')


''' 
    DATABASE
'''
client = pymongo.MongoClient('mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/')

with client:
    db = client.wjjcn
    e = db.brand_retailer_product.find()

    for item in e:
        brands.append(item['brand'])
''' 
    END DATABASE
'''



def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext

def checkStringContainsString(html, stringToCheck):
    returnValue = "False"
    if stringToCheck in html:
        returnValue = "True " + stringToCheck
    return returnValue

url = 'https://www.jumbo.com/producten/red-bull-energy-drink-4-pack-250ml-236284BLK'
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
html = requests.get(url, headers=agent).text
soup = BeautifulSoup(html, "html.parser")

stringArray = ["Energy drink 4-pack", "4x", "Red Bull", "Red Bull Energy Drink wordt wereldwijd gewaardeerd door topsporters.",
               "Stimuleert Lichaam en Geest®", "Het suikergehalte van een blikje is gelijk aan frisdrank: 11g/100ml",
               "Het cafeïnegehalte van een blikje is gelijk aan een kop koffie: 32mg/100ml", "Een 4-pack bevat 4 blikjes van 250ml"]
# print(soup)

# Find all images and span tags, then strip the html tags from span tags
spans = soup.find_all("span")
ps = soup.find_all("p")

# print(soup.find_all("span"))
# print(soup.find_all("p"))

for span in spans:
    text = ""
    if span and span.text.strip():
        text = cleanhtml(span.text)
        i = 0
        for i in range(len(stringArray)):
            returnValue = checkStringContainsString(text, stringArray[i])
            if returnValue != "False":
                print("Span: " + returnValue)

for p in ps:
    text = ""
    if p and p.text.strip():
        text = cleanhtml(p.text)
        i = 0
        for i in range(len(stringArray)):
            returnValue = checkStringContainsString(text, stringArray[i])
            if returnValue != "False":
                print("P: " + returnValue)
