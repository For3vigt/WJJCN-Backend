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
    e = db.products.find()

    for item in e:
        brands.append(item)
'''
    END DATABASE
'''


def cleanhtml(raw_html):
    cleantext = re.sub('<.*?>', ' ', str(raw_html))
    cleantext = re.sub(' +', ' ', cleantext)
    if cleantext.startswith(' '):
        cleantext = cleantext[1:]
        cleantext = cleantext[:-1]
    return cleantext


def cleanText(raw_text):
    cleantext = re.sub('[\n\r\t]', ' ', raw_text)
    return cleantext


def checkStringContainsString(html, stringToCheck):
    returnValue = "False"
    if stringToCheck in html:
        returnValue = "True " + stringToCheck
    return returnValue


def getPage(url):
    agent = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
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
            # for j in range(len(correctTextSplit)):
            if startIndex < len(textToCheckSplit):
                if textToCheckSplit[startIndex] == correctTextSplit[0]:
                    return startIndex

                elif i == len(textToCheckSplit) - 1:
                    exitWhile = True
            else:
                exitWhile = True

    return -1


def compareTexts(textToCheck, correctText):
    textToCheckSplit = []
    correctTextSplit = []

    foundText = []
    fullFoundText = ""
    correctTextSplit = correctText.split()
    textToCheckSplit = textToCheck.split()

    correctCount = 0
    correctTextFound = False
    exceededLastIndex = False

    while not exceededLastIndex:
        foundIndex = findFirstIndex(textToCheckSplit, correctTextSplit)

        if foundIndex != -1:
            for i in range(len(correctTextSplit)):
                if len(correctTextSplit) <= len(textToCheckSplit) - foundIndex:
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
                    exceededLastIndex = True

        if not correctTextFound:
            foundText.clear()
            correctCount = 0
            for i in range(foundIndex):
                del textToCheckSplit[0]

            if foundIndex == 0:
                del textToCheckSplit[0]

            if len(textToCheckSplit) < len(correctTextSplit):
                exceededLastIndex = True


    if correctTextFound:
        return textToCheck
    else:
        return False


def checkCharacterList(characterList, brandItem, characterType):
    correctItems = []
    correctItemsResult = []
    for key, value in brandItem["product_brand"].items():
        correctItems.append(value)
        correctItemsResult.append([])

    for i in range(len(correctItems)):
        if isinstance(correctItems[i], list):
            for j in range(len(correctItems[i])):
                correctItemsResult[i].append([])

    for character in characterList:
        text = ""
        if character and character.text.strip():
            # if "Red Bull Energy Drink wordt wereldwijd gewaardeerd door topsporters" in character.text:
            #     None
            text = cleanText(cleanhtml(character))
            for i in range(len(correctItems)):
                if not isinstance(correctItems[i], list):
                    stringToCompare = cleanText(correctItems[i])
                    result = compareTexts(text, stringToCompare)
                    if result != False:
                        correctItemsResult[i].append(result)
                else:
                    for j in range(len(list(correctItems[i]))):
                        stringToCompare = cleanText(correctItems[i][j])
                        result = compareTexts(text, stringToCompare)
                        if result != False:
                            correctItemsResult[i][j].append(result)
    return correctItemsResult


def compare(brandItem):
    print(brandItem["product_brand"])
    tagArray = []

    jsonKeys = []
    correctItems = []
    correctItemsResult = []
    for key, value in brandItem["product_brand"].items():
        jsonKeys.append(key)
        correctItems.append(value)
        if not isinstance(value, list):
            correctItemsResult.append([])
        else:
            correctItemsResult.append([])
            for i in range(len(value)):
                correctItemsResult[len(correctItemsResult) - 1].append([])

    url = "https://www.jumbo.com/producten/red-bull-energy-drink-504874BLK" #jumbo bull 1x 250ml
    # url = "https://www.ah.nl/producten/product/wi195821/red-bull-energy-drink"  # ah red bull 1x 250ml
    # url = "https://www.jumbo.com/producten/red-bull-energy-drink-24-pack-250ml-504874TRL"
    soup = getPage(url)

    spans = soup.find_all("span")
    ps = soup.find_all("p")
    h1s = soup.find_all("h1")
    lis = soup.find_all("li")
    metaTags = soup.find_all('meta')
    seoTags = []
    for tag in metaTags:
        if tag.get("content"):
            seoTags.append(tag.get("content"))
    tagArray.append(spans)
    tagArray.append(ps)
    tagArray.append(h1s)
    tagArray.append(lis)
    # tagArray.append(seoTags)

    for i in range(len(tagArray)):
        test = tagArray[i]
        if correctItemsResult == []:
            correctItemsResult = checkCharacterList(test, brandItem, "test")
        else:
            tempResult = checkCharacterList(test, brandItem, "test")
            for i in range(len(correctItems)):
                if not isinstance(correctItems[i], list):
                    correctItemsResult[i] = correctItemsResult[i] + tempResult[i]
                else:
                    for j in range(len(correctItems[i])):
                        if tempResult[i][j] != []:
                            correctItemsResult[i][j] = correctItemsResult[i][j] + tempResult[i][j]

    for i in range(len(correctItems)):
        if not isinstance(correctItems[i], list):
            if correctItemsResult[i] != []:
                arry = ["aaaa", "aa", "aaa"]
                test = min(arry, key=len)
                tempArray = correctItemsResult[i]
                print(jsonKeys[i] + " is: " + min(tempArray, key=len))
            else:
                correctItemsResult[i] = "Not found"
                print(jsonKeys[i] + " is: " + correctItemsResult[i])
        else:
            for j in range(len(correctItems[i])):
                if correctItemsResult[i][j] != []:
                    tempArray = correctItemsResult[i][j]
                    print(jsonKeys[i] + " " + str(j) + " is: " + min(tempArray, key=len))
                else:
                    correctItemsResult[i][j] = "Not found"
                    print(jsonKeys[i] + " " + str(j) + " is: " + correctItemsResult[i][j])


# compare(brands[15]) #jumbo red bull 1x 250ml
# compare(brands[0]) #ah red bull 1x 250ml
# compare(brands[30])  #ah red bull 1x 250ml correct
compare(brands[31])  # jumbo red bull 1x 250ml correct
# compare(brands[18])