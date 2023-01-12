import math
import sys
from datetime import date

import numpy
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
import re
import pymongo
import requests
import certifi

ca = certifi.where()

timeout_counter = 0
brands = []

'''
    DATABASE
'''
# The code below connects to the database and receives all brands, so the products and their correct data can be
# compared. If something goes wrong with connecting to the database, it will stop the code and retry when the user tells it to.
def connectToDatabaseAndGetBrands():
    global timeout_counter

    timeout_retry = 15
    request_timeout_in_seconds = 5

    counter = timeout_counter

    if counter != timeout_retry:
        try:
            client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca, connectTimeoutMS=5000)

            with client:
                db = client.wjjcn
                e = db.products.find()

                for item in e:
                    brands.append(item)

            if brands:
                return brands

            connectToDatabaseAndGetBrands()
        except KeyboardInterrupt:
                sys.exit()
        except:
            print("Could not connect to database. Please check your internet connection.")
            counter += 1
            timeout_counter = counter
            connectToDatabaseAndGetBrands()
    else:
        pause_and_resume_script()
        timeout_counter = 0
        connectToDatabaseAndGetBrands()

        if brands:
            return brands

        connectToDatabaseAndGetBrands()

def pushToDatabase(productId, body):
    global timeout_counter

    timeout_retry = 15
    request_timeout_in_seconds = 5

    counter = timeout_counter

    if counter != timeout_retry:
        try:
            client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/",
                                         tlsCAFile=ca, connectTimeoutMS=5000)

            with client:
                db = client.wjjcn

                db.products.update_one({"_id": ObjectId(productId)}, {"$push": {"history": body}})

                client.close()

        except KeyboardInterrupt:
            sys.exit()
        except:
            print("Could not connect to database. Please check your internet connection.")
            counter += 1
            timeout_counter = counter
            pushToDatabase(productId, body)
    else:
        pause_and_resume_script()
        timeout_counter = 0
        pushToDatabase(productId, body)

        if brands:
            return brands

        pushToDatabase(productId, body)
'''
    END DATABASE
'''

def cleanText(raw_text):
    cleantext = re.sub('-', ' -', raw_text)
    cleantext = re.sub('[\n\r\t]', ' ', cleantext)
    cleantext = re.sub(' +', ' ', cleantext)
    return cleantext


# Below method gives a number of the distance the textToCompareWith is from the mainText. In other words how much of the
# textToCompareWith is correct with mainText.
def levenshteinDistance(mainText, textToCompareWith):
    if len(mainText) > len(textToCompareWith):
        mainText, textToCompareWith = textToCompareWith, mainText

    distances = range(len(mainText) + 1)
    for i2, c2 in enumerate(textToCompareWith):
        distances_ = [i2+1]
        for i1, c1 in enumerate(mainText):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


# Pauses the program, and continues to wait until the command is given to continue the code.
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
                print("resuming code")
                run = False
            if res == "2":
                sys.exit()
        except KeyboardInterrupt:
            sys.exit()


# The below method tries to get the page from the internet, if there is no connection it will automatically stop the
# program and start retrying when the code is resumed.
def getPage(url):
    global timeout_counter

    timeout_retry = 15
    request_timeout_in_seconds = 5

    counter = timeout_counter

    html = requests

    agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    if counter != timeout_retry:
        try:
            html = requests.get(url, headers=agent, timeout=request_timeout_in_seconds).text

            if html != requests:
                soup = BeautifulSoup(html, "html.parser")
                return soup
            else:
                getPage(url)
        except KeyboardInterrupt:
                sys.exit()
        except:
            print("An error occurred. Please check your internet connection.")
            counter += 1
            timeout_counter = counter
            getPage(url)
    else:
        pause_and_resume_script()
        timeout_counter = 0
        getPage(url)

        if html != requests:
            soup = BeautifulSoup(html, "html.parser")
            return soup
        else:
            getPage(url)


# Finds the start index where the first word of the correct string is equal to the same word within the found text
# somewhere within the text. So for example: (found text=)["This", "is", "Hello", "World"] (correct text first word=)["Hello"] ->
# it will then find Hello in the index: 2, this index will be returned.
def findFirstIndex(textToCheckSplit, correctTextSplit):
    textToCheckLength = len(textToCheckSplit)
    correctTextLength = len(correctTextSplit)
    exitWhile = False

    # A check to see if the correct text fits within the found text else it returns -1, no index found as the correct
    # text would not fit within the found text.
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

# Compares the text found on the website and the string from the database.
def selectMostLikelyText(textList, stringToCompare):
    scoreArray = []
    stringToComparLowerCase = stringToCompare.casefold()

    stringToCompareHasMultipleBullitPoints = False
    
    if stringToCompare.count('-') > 3 or stringToCompare.count('\u2022') > 3:
        stringToCompareHasMultipleBullitPoints = True

    # Check if text contains bullit points and remove from textList and split on them. After that add each individual bullit point back to textList. 
    if stringToCompareHasMultipleBullitPoints == False:
        for text in textList:
            if "-" in text and len(text) > 60 or u'\u2022' in text:
                textList.remove(text)
                textArray = []
                if "-" in text:
                    textArray = text.split("-", 1)
                elif u'\u2022' in text:
                    textArray = text.split(u'\u2022')

                for bullitpoint in textArray:
                    textList.append(bullitpoint)

    # For each text in the array of text found give a score to that text.
    for text in textList:
        score = 0
        wordArray = text.split()

        stringToCompareLen = len(stringToCompare)
        textLen = len(text)

        # Check if a word from the text found is in the string from the database and vice versa.
        for word in wordArray:
            wordToLowerCase = word.casefold()

            if wordToLowerCase in stringToComparLowerCase:
                score += 1

            wordArrayStringToCompare = stringToCompare.split()

            for wordStringToCompare in wordArrayStringToCompare:
                if wordStringToCompare in text:
                    score += 1

                if word == wordStringToCompare:
                    score += 5

        # if text lenght isn't close to each other then the score will become zero for that text.
        if textLen < stringToCompareLen - 30 or textLen > stringToCompareLen + 30:
            score = 0
        
        # if the score is 0 or 1 then the score will become zero.
        if score < 2 or textLen > 50 and score < 5:
            score = 0

        scoreArray.append(score)

    textMostLikely = None

    # Check if max score in the array is too low depending on the amount of words in the array from string to compare.
    # Else text mostlikely will become the highest score array.
    if max(scoreArray) <= 2 and len(stringToCompare.split()) > 2 or max(scoreArray) == 0:
        textMostLikely = False
    else:
        textMostLikelyIndex = scoreArray.index(max(scoreArray))
        textMostLikely = textList[textMostLikelyIndex]
    
    return textMostLikely


# The function below first splits the received texts by their words like: "Hello World" -> "Hello" "World". Then it will
# try and find the correct text within the found text. First it will call another method that searches the possible
# start index like: (found text =)["This", "is", "Hello", "World"]  (correct text =)"Hello", "World" -> found start
# index would be 2. Then loops over the found text to compare following characters with the correct text to see if it is
# found within the found text. If the correct text is within the found text it will be returned, else False will be returned.
def compareTexts(textToCheck, correctText):
    textToCheckSplit = []
    correctTextSplit = []

    foundText = []
    fullFoundText = ""
    # Here the received texts are split by " " characters and put into two lists.
    correctTextSplit = correctText.split()
    textToCheckSplit = textToCheck.split()

    correctCount = 0
    correctTextFound = False
    exceededLastIndex = False

    # The below method will continue until the length of the correct text doesn't fit or equal the length of the found text
    while not exceededLastIndex:
        # This method will find the start index like: (found text =)["This", "is", "Hello", "World"]
        # (correct text =)"Hello", "World" -> found start index would be 2. If no start index is found -1 is returned.
        foundIndex = findFirstIndex(textToCheckSplit, correctTextSplit)

        # If a start index is found, the found text[start index] will be the comparison beginning point. Then word for
        # word the found text and correct text are checked if there equal. When the words are correct, a counter will increase.
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

        # If the fount word count is equal to the correct text length, it means the correct text is found within the
        # found text and the found text is returned.
        if correctCount == len(correctTextSplit):
            for i in range(len(correctTextSplit)):
                if foundText[i] != correctTextSplit[i]:
                    return False
                else:
                    if fullFoundText:
                        fullFoundText = fullFoundText + " " + foundText[i]
                    else:
                        fullFoundText = foundText[i]
                    correctTextFound = True
                    exceededLastIndex = True

        # If the correct text was not found, the text up until the start index will be removed from the string.
        # Afterwards the loop will continue until the length of the correct string doesn't fit within the found sting.
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
        # return fullFoundText
        return textToCheck
    else:
        return False


# The below function goes through all items it should find, ex. title, description etc. and compares the correct text
# like title to the found text. It compares if the correct text is somewhere in the found text.
def checkCharacterList(characterList, product):
    correctItems = []
    correctItemsResult = []
    # a list based off of the layout of the received correct item is created to put the found results into.
    for key, value in product["product_brand"].items():
        correctItems.append(value)
        if not isinstance(value, list):
            correctItemsResult.append([])
        else:
            correctItemsResult.append([])
            for i in range(len(value)):
                correctItemsResult[len(correctItemsResult) - 1].append([])

    for i in range(len(correctItems)):
        if isinstance(correctItems[i], list):
            for j in range(len(correctItems[i])):
                correctItemsResult[i].append([])

    # The loop below loops over all found text items to then compare them to the correct text.
    for character in characterList:
        if character:
            # The method below removes all special text characters like: \t, \r, \n etc.
            text = cleanText(character)

            # The below loop goes over all correct items if they are in a list it goes through the list instead.
            for i in range(len(correctItems)):
                if not isinstance(correctItems[i], list):
                    # The method below removes all special text characters like: \t, \r, \n etc.
                    stringToCompare = cleanText(correctItems[i])
                    # The method below compares a singular found text to a component like: title, description, etc.
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


def checkTextFromWebsite(textList, brandItem):
    textListWoc = []
    textListScraped = []
    # a list based off of the layout of the received correct item is created to put the found results into.
    for key, value in brandItem["product_brand"].items():
        textListWoc.append(value)
        if not isinstance(value, list):
            textListScraped.append([])
        else:
            textListScraped.append([])
            for i in range(len(value)):
                textListScraped[len(textListScraped) - 1].append([])

    for i in range(len(textListWoc)):
        if not isinstance(textListWoc[i], list):
            # The method below removes all special text characters like: \t, \r, \n etc.
            stringToCompare = cleanText(textListWoc[i])
            # The method below compares a singular found text to a component like: title, description, etc.
            result = selectMostLikelyText(textList, stringToCompare)
            if result != False:
                textListScraped[i].append(result)
        else:
            for j in range(len(list(textListWoc[i]))):
                stringToCompare = cleanText(textListWoc[i][j])
                result = selectMostLikelyText(textList, stringToCompare)
                if result != False:
                    textListScraped[i][j].append(result)

    return textListScraped


def main(product, url):
    tagArray = []

    jsonKeys = []
    correctItems = []
    correctItemsResult = []
    mostLikelyItemsResult = []
    # The method below creates a multidimensional array based on the contents of product_brand
    for key, value in product["product_brand"].items():
        jsonKeys.append(key)
        correctItems.append(value)
        if not isinstance(value, list):
            correctItemsResult.append([])
            mostLikelyItemsResult.append([])
        else:
            correctItemsResult.append([])
            mostLikelyItemsResult.append([])
            for i in range(len(value)):
                correctItemsResult[len(correctItemsResult) - 1].append([])
                mostLikelyItemsResult[len(mostLikelyItemsResult) - 1].append([])

    soup = getPage(url)

    # For all tags containing text like span, paragraph, h1, list items etc. an array per tag is created to put all found text into.
    spanTags = []
    pTags = []
    h1Tags = []
    liTags = []

    spans = soup.find_all("span")
    for tag in spans:
        if tag.getText():
            spanTags.append(tag.getText())
    ps = soup.find_all("p")
    for tag in ps:
        if tag.getText():
            pTags.append(tag.getText())
    h1s = soup.find_all("h1")
    for tag in h1s:
        if tag.getText():
            h1Tags.append(tag.getText())
    lis = soup.find_all("li")
    for tag in lis:
        if tag.getText():
            liTags.append(tag.getText())
    # SEO tags, explain more here -------------------------------------------------<
    metaTags = soup.find_all('meta')
    seoTags = []
    for tag in metaTags:
        if tag.get("content"):
            seoTags.append(tag.get("content"))
    tagArray.append(spanTags)
    tagArray.append(pTags)
    tagArray.append(h1Tags)
    tagArray.append(liTags)
    # tagArray.append(seoTags)

    # A loop goes through all tags and checks if the correct text is found in the found text by calling a method,
    # if the correct text is found somewhere in the found text a list is returned.
    for i in range(len(tagArray)):
        tag = tagArray[i]
        if correctItemsResult == []:
            correctItemsResult = checkCharacterList(tag, product)
        else:
            tempResult = checkCharacterList(tag, product)
            for i in range(len(correctItems)):
                if not isinstance(correctItems[i], list):
                    correctItemsResult[i] = correctItemsResult[i] + tempResult[i]
                else:
                    for j in range(len(correctItems[i])):
                        if tempResult[i][j] != []:
                            correctItemsResult[i][j] = correctItemsResult[i][j] + tempResult[i][j]

    for i in range(len(tagArray)):
        tag = tagArray[i]
        if mostLikelyItemsResult == []:
            mostLikelyItemsResult = checkTextFromWebsite(tag, product)
        else:
            tempResult = checkTextFromWebsite(tag, product)
            for i in range(len(correctItems)):
                if not isinstance(correctItems[i], list):
                    mostLikelyItemsResult[i] = mostLikelyItemsResult[i] + tempResult[i]
                else:
                    for j in range(len(correctItems[i])):
                        if tempResult[i][j] != []:
                            mostLikelyItemsResult[i][j] = mostLikelyItemsResult[i][j] + tempResult[i][j]


    # After going through all tag items for all attributes like title, description etc. the shortest match is found and returned.
    for i in range(len(correctItems)):
        if not isinstance(correctItems[i], list):
            if correctItemsResult[i] != []:
                scores = {}
                tempArray = correctItemsResult[i]
                for item in tempArray:
                    scores[item] = 1 - levenshteinDistance(correctItems[i], item)

                import operator
                bestMatch = max(scores.items(), key=operator.itemgetter(1))[0]
                if tempResult == correctItems[i]:
                    correctItemsResult[i] = bestMatch[0]
                else:
                    correctItemsResult[i] = "Not found"
            else:
                correctItemsResult[i] = "Not found"
        else:
            for j in range(len(correctItems[i])):
                if correctItemsResult[i][j] != []:
                    scores = {}
                    tempArray = correctItemsResult[i][j]
                    for item in tempArray:
                        scores[item] = 1 - levenshteinDistance(correctItems[i][j], item)

                    import operator
                    bestMatch = max(scores.items(), key=operator.itemgetter(1))[0]
                    if tempResult == correctItems[i][j]:
                        correctItemsResult[i][j] = bestMatch[0]
                    else:
                        correctItemsResult[i][j] = "Not found"
                else:
                    correctItemsResult[i][j] = "Not found"

    # Add to database
    today = date.today().strftime('%Y-%m-%d')
    foundResult = {}
    correctItemsCount = 0

    
    # print("test ", correctItemsResult)

    for i in range(len(correctItemsResult)):
        equal_to_scraped = False

        if correctItemsResult[i] != "Not found" and correctItemsResult[i] == correctItems[i]:
            if isinstance(correctItemsResult[i], list):
                oneOrMoreNotFound = False
                for item in correctItemsResult[i]:
                    if item == "Not Found":
                        oneOrMoreNotFound = True
                if not oneOrMoreNotFound:
                    equal_to_scraped = True
                    correctItemsCount += 1
            else:
                equal_to_scraped = True
                correctItemsCount += 1
        if correctItemsResult[i] == "Not found" or isinstance(correctItemsResult[i], list) and mostLikelyItemsResult[i] != []:
            if mostLikelyItemsResult[i] != [] and not isinstance(correctItemsResult[i], list):
                scores = {}
                tempArray = mostLikelyItemsResult[i]
                for item in tempArray:
                    scores[item] = 1 - levenshteinDistance(correctItems[i], item)

                import operator
                correctItemsResult[i] = max(scores.items(), key=operator.itemgetter(1))[0]
            if isinstance(correctItemsResult[i], list):
                for j in range(len(correctItemsResult[i])):
                    # print(mostLikelyItemsResult[i])
                    if correctItemsResult[i][j] == "Not found" and mostLikelyItemsResult[i][j] != []:
                        scores = {}
                        tempArray = mostLikelyItemsResult[i][j]
                        for item in tempArray:
                            scores[item] = 1 - levenshteinDistance(correctItems[i][j], item)

                        import operator
                        correctItemsResult[i][j] = max(scores.items(), key=operator.itemgetter(1))[0]
        # print(correctItemsResult)
        foundResult[jsonKeys[i]] = {"text": correctItemsResult[i], "equal_to_scraped": equal_to_scraped}

    score = round((correctItemsCount / len(correctItemsResult)) * 100)

    historyObject = {
        "scrape_date": today,
        "score": score,
        "product_brand": product["product_brand"],
        "product_scraped": foundResult
    }
    print(historyObject["product_scraped"])
    # pushToDatabase(product["_id"], historyObject)


if __name__ == "__main__":
    connectToDatabaseAndGetBrands()
    main(brands[18], "https://www.jumbo.com/producten/bullit-energy-drink-suikervrij-passievrucht-250ml-490330BLK/") #Jumbo red bull 1x 250ml
    # main(brands[0], "https://www.ah.nl/producten/product/wi195821/red-bull-energy-drink") #Alberth Heijn red bull 1x 250ml
    # main(brands[30]) #Alberth Heijn red bull 1x 250ml correct
    # main(brands[31])  #Jumbo red bull 1x 250ml correct