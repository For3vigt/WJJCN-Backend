from bs4 import BeautifulSoup
import re
import pymongo
import requests
import certifi
ca = certifi.where()

brands = []


'''
    DATABASE
'''
client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca)

with client:
    db = client.wjjcn
    e = db.brand_retailer_product.find()

    for item in e:
        brands.append(item)
'''
    END DATABASE
'''


def cleanhtml(raw_html):
    cleantext = re.sub('<.*?>', '', raw_html)
    return cleantext


def cleanText(raw_text):
    if "Red Bull Energy Drink wordt wereldwijd gewaardeerd door topsporters" in raw_text:
        None
    cleantext = re.sub(r'[\n\r\t]', '', raw_text)
    return cleantext


def checkStringContainsString(html, stringToCheck):
    returnValue = "False"
    if stringToCheck in html:
        returnValue = "True " + stringToCheck
    return returnValue


def getPage(url):
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    html = requests.get(url, headers=agent).text
    soup = BeautifulSoup(html, "html.parser")
    return soup


def findFirstIndex(textToCheckSplit, correctTextSplit):
    textToCheckLength = len(textToCheckSplit)
    correctTextLength = len(correctTextSplit)
    exitWhile = False

    if textToCheckLength >= correctTextLength:
        useLength = textToCheckLength
    else:
        return -1

    while not exitWhile:
        for i in range(useLength):
            startIndex = i
            for j in range(len(correctTextSplit)):
                if j + startIndex < len(textToCheckSplit):
                    if textToCheckSplit[startIndex + j] == correctTextSplit[j]:
                        return startIndex + j

                    elif i == len(textToCheckSplit) - 1:
                        exitWhile = True
                else:
                    exitWhile = True

    return -1


def compareTexts(textToCheck, correctText):
    textToCheckSplit = []
    correctTextSplit = []
    # if "Red Bull Energy Drink wordt wereldwijd gewaardeerd door topsporters" in textToCheck and "Red Bull Energy Drink wordt wereldwijd gewaardeerd door topsporters" in correctText:
    #     None
    foundText = []
    correctTextSplit = correctText.split()
    textToCheckSplit = textToCheck.split()

    correctCount = 0
    correctTextFound = False

    foundIndex = findFirstIndex(textToCheckSplit, correctTextSplit)

    if foundIndex != -1:
        for i in range(len(correctTextSplit)):
            if foundIndex + len(correctTextSplit) < len(textToCheckSplit) - foundIndex:
                if textToCheckSplit[foundIndex + i] == correctTextSplit[i]:
                    foundText.append(textToCheckSplit[foundIndex + i])
                    correctCount += 1
            else:
                return False
    else:
        return False

    if correctCount == len(correctTextSplit):
        for i in range(len(correctTextSplit)):
            if foundText[i] != correctTextSplit[i]:
                return False
            else:
                correctTextFound = True

    testString = ""

    if correctTextFound and foundIndex != -1:
        for i in range(len(correctTextSplit)):
            foundText
            testString = testString + " " + foundText[i]

    if correctTextFound:
        return correctText + " in:" + testString
    else:
        return False


def checkCharacterList(characterList, brandItem, characterType):
    correctItems = []
    for key, value in brandItem["product_brand"].items():
        correctItems.append(value)

    for character in characterList:
        text = ""
        if character and character.text.strip():
            text = cleanText(cleanhtml(character.text))
            i = 0
            for i in range(len(correctItems)):
                if not isinstance(correctItems[i], list):
                    stringToCompare = cleanText(correctItems[i])
                    result = compareTexts(text, stringToCompare)
                    if result != False:
                        print(characterType + ": " + result)
                else:
                    for j in range(len(correctItems[i])):
                        stringToCompare = correctItems[i][j]
                        result = compareTexts(text, stringToCompare)
                        if result != False:
                            print(characterType + ": " + result)


def compare(brandItem):
    print(brandItem["product_brand"])
    tagArray = []
    # productItems = []
    # for key, value in brandItem["product_brand"].items():
    #     productItems.append(value)

    url = "https://www.jumbo.com/producten/red-bull-energy-drink-504874BLK" #jumbo bull 1x 250ml
    # url = "https://www.ah.nl/producten/product/wi195821/red-bull-energy-drink" #ah red bull 1x 250ml
    soup = getPage(url)

    spans = soup.find_all("span")
    ps = soup.find_all("p")
    h1s = soup.find_all("h1")
    lis = soup.find_all("li")
    tagArray.append(spans)
    tagArray.append(ps)
    tagArray.append(h1s)
    tagArray.append(lis)

    for i in range(len(tagArray)):
        test = tagArray[i]

        checkCharacterList(test, brandItem, "test")

compare(brands[15]) #jumbo red bull 1x 250ml
compare(brands[0]) #ah red bull 1x 250ml