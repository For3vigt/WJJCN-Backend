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
error_object_id = ''

'''
    DATABASE
'''


class PrintColors:
    INFO = '\033[94m'
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


# The code below connects to the database and receives all brands, so the products and their correct data can be
# compared. If something goes wrong with connecting to the database, it will stop the code and retry when the user tells it to.
# def connectToDatabaseAndGetBrands():
#     global timeout_counter
#
#     timeout_retry = 15
#     request_timeout_in_seconds = 5
#
#     counter = timeout_counter
#
#     if counter != timeout_retry:
#         try:
#             client = pymongo.MongoClient("mongodb+srv://wjjcn:Sl33fAQiLusKGsx8@woc.amjwpqs.mongodb.net/", tlsCAFile=ca, connectTimeoutMS=5000)
#
#             with client:
#                 db = client.wjjcn
#                 e = db.products.find()
#
#                 for item in e:
#                     brands.append(item)
#
#             if brands:
#                 return brands
#
#             connectToDatabaseAndGetBrands()
#         except KeyboardInterrupt:
#                 sys.exit()
#         except:
#             print("Could not connect to database. Please check your internet connection.")
#             counter += 1
#             timeout_counter = counter
#             connectToDatabaseAndGetBrands()
#     else:
#         pause_and_resume_script()
#         timeout_counter = 0
#         connectToDatabaseAndGetBrands()
#
#         if brands:
#             return brands
#
#         connectToDatabaseAndGetBrands()

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
            print(PrintColors.FAIL + "[ERROR]" + PrintColors.ENDC + " Could not connect to database. Please check your internet connection.")
            error_handler(error_object_id, "[ERROR] Could not connect to database. Please check your internet connection.", 'save_to_database')
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
            print(PrintColors.FAIL + "[ERROR]" + PrintColors.ENDC + " An error occurred. Please check your internet connection.")
            error_handler(error_object_id, "[ERROR] An error occurred. Please check your internet connection.", 'product_fetch_compare')
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


def tryFindMostLikelyText(textToCheck, correctText):
    foundText = []
    foundIndexes = []
    fullFoundText = ""
    # Here the received texts are split by " " characters and put into two lists.
    correctTextSplit = correctText.split()
    correctTextSplitToDelete = correctText.split()
    textToCheckSplit = textToCheck.split()

    correctCount = 0
    correctTextFound = False
    exceededLastIndex = False

    while not exceededLastIndex:
        if correctTextSplitToDelete:
            foundIndex = findFirstIndex(textToCheckSplit, correctTextSplitToDelete)
        else:
            correctTextSplitToDelete = correctText.split()
            for i in range(foundIndexes[len(foundIndexes) - 1] + 1):
                del textToCheckSplit[0]
            foundIndexes.clear()
            foundText.clear()
            correctCount = 0
            foundIndex = -1

        if foundIndex != -1:
            if foundIndexes:
                addedToList = False
                for j in range(len(foundIndexes)):
                    if foundIndex != foundIndexes[j] and foundIndex >= foundIndexes[j] - 3 and foundIndex <= foundIndexes[j] + 3 and not addedToList:
                        foundIndexes.append(foundIndex)
                        correctCount += 1
                        foundText.append(textToCheckSplit[foundIndex])
                        addedToList = True
            else:
                foundIndexes.append(foundIndex)
                correctCount += 1
                foundText.append(textToCheckSplit[foundIndex])

        if correctCount == len(correctTextSplit):
            for i in range(len(correctTextSplit)):
                if foundText[i] != correctTextSplit[i]:
                    return False
                else:
                    correctTextFound = True
                    exceededLastIndex = True

        if not correctTextFound:
            if foundIndex != -1:
                del correctTextSplitToDelete[0]

            if foundIndex == 0:
                del textToCheckSplit[0]

            if len(textToCheckSplit) < len(correctTextSplit):
                exceededLastIndex = True

            if foundIndex == -1:
                exceededLastIndex = True

    if correctTextFound:
        return textToCheck
    else:
        return False


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
        correctItemsResult.append([])

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


def checkCharacterListForMostLikely(characterList, product):
    correctItems = []
    correctItemsResult = []
    # a list based off of the layout of the received correct item is created to put the found results into.
    for key, value in product["product_brand"].items():
        correctItems.append(value)
        correctItemsResult.append([])

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
                    result = tryFindMostLikelyText(text, stringToCompare)
                    if result != False:
                        correctItemsResult[i].append(result)
                else:
                    for j in range(len(list(correctItems[i]))):
                        stringToCompare = cleanText(correctItems[i][j])
                        result = tryFindMostLikelyText(text, stringToCompare)
                        if result != False:
                            correctItemsResult[i][j].append(result)
    return correctItemsResult


def main(product, url, error_objectid):
    global error_object_id
    error_object_id = error_objectid
    tagArray = []

    jsonKeys = []
    correctItems = []
    correctItemsResult = []
    # The method below creates a multidimensional array based on the contents of product_brand
    for key, value in product["product_brand"].items():
        jsonKeys.append(key)
        correctItems.append(value)
        if not isinstance(value, list):
            correctItemsResult.append([])
        else:
            correctItemsResult.append([])
            for i in range(len(value)):
                correctItemsResult[len(correctItemsResult) - 1].append([])

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

    # testTags = []
    # testTags.append("Red bull energy drink is speciaal ontwikkeld voor momenten waarop je meer wilt presteren.")
    # testTags.append("Red bull energy drink is test speciaal ontwikkeld test test voor test test momenten test test waarop test test je test meer wilt test test presteren.")
    # testTags.append("Red bull energy drink is een ontwikkeld geweldig drankje maar dit is test speciaal ontwikkeld test test voor test test momenten test test waarop test test je test meer wilt test test presteren.")
    # testTags.append("In een blikje Red Bull energy drink, zitten bepaalde stoffen die je gwn goed voor je zijn, lekker drinken maat")
    # testTags.append("De hoeveelheid suiker is vergelijkbaar met sinaasappelsap: 11g/100ml")
    # testcorrect = []
    # testcorrect.append("Het suikergehalte van een blikje is gelijk aan frisdrank: 11g/100ml")
    #
    # temptest = tryFindMostLikelyText(testTags[4], testcorrect[0])

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
        if correctItemsResult == []:
            correctItemsResult = checkCharacterList(tag, product)
        else:
            tempResult = checkCharacterList(tag, product)
            for i in range(len(correctItems)):
                if not correctItemsResult[i]:
                    if not isinstance(correctItems[i], list):
                        correctItemsResult[i] = correctItemsResult[i] + tempResult[i]
                    else:
                        for j in range(len(correctItems[i])):
                            if tempResult[i][j] != []:
                                correctItemsResult[i][j] = correctItemsResult[i][j] + tempResult[i][j]

    # After going through all tag items for all attributes like title, description etc. the shortest match is found and returned.
    for i in range(len(correctItems)):
        if not isinstance(correctItems[i], list):
            if correctItemsResult[i] != []:
                tempArray = correctItemsResult[i]
                correctItemsResult[i] = min(tempArray, key=len)
            else:
                correctItemsResult[i] = "Not found"
        else:
            for j in range(len(correctItems[i])):
                if correctItemsResult[i][j] != []:
                    tempArray = correctItemsResult[i][j]
                    correctItemsResult[i][j] = min(tempArray, key=len)
                else:
                    correctItemsResult[i][j] = "Not found"

    # Add to database
    today = date.today().strftime('%Y-%m-%d')
    foundResult = {}
    correctItemsCount = 0

    for i in range(len(correctItemsResult)):
        equal_to_scraped = False

        if correctItemsResult[i] != "Not found":
            equal_to_scraped = True
            correctItemsCount += 1

        foundResult[jsonKeys[i]] = {"text": correctItemsResult[i], "equal_to_scraped": equal_to_scraped}

    score = round((correctItemsCount / len(correctItemsResult)) * 100)

    historyObject = {
        "scrape_date": today,
        "score": score,
        "product_brand": product["product_brand"],
        "product_scraped": foundResult
    }
    pushToDatabase(product["_id"], historyObject)

# if __name__ == "__main__":
# main(brands[22]) #Jumbo red bull 1x 250ml
# main(brands[0]) #Alberth Heijn red bull 1x 250ml
# main(brands[30]) #Alberth Heijn red bull 1x 250ml correct
# main(brands[31])  # Jumbo red bull 1x 250ml correct
