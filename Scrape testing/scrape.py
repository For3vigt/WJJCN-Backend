from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options
# Chrome options for browser its going to open
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('start-maximized')

# Run driver using Chrome
d = webdriver.Chrome(service=Service(
    ChromeDriverManager
    ().install()), chrome_options=chrome_options)

# Product that will be searched and link of the website it will use
product = 'Red Bull Energy Drink 4-pack'
d.get('https://www.jumbo.com/')

# Try to get past cookies
try:
    element = WebDriverWait(d, 1).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(), 'Weigeren')]"))
    )
except:
    print("Could not find element!")
else:
    if element:
        d.find_element(By.XPATH, "//*[contains(text(), 'Weigeren')]").click()

# Try to find search bar
try:
    element = WebDriverWait(d, 1).until(
        EC.presence_of_element_located(
            (By.XPATH, "//input[@placeholder='Waar ben je naar op zoek?']"))
    )
except:
    print("Could not find element!")
else:
    if element:
        e = d.find_element(
            By.XPATH, "//input[@placeholder='Waar ben je naar op zoek?']")
        e = e.send_keys(product + '\n')

# Try to click the right product
try:
    element = WebDriverWait(d, 1).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[normalize-space(text()) = '" + product + "']"))
    )
except:
    try:
        elementContains = WebDriverWait(d, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, "//a[text()[contains(.,'" + product + "')]]"))
        )
    except:
        print("Could not find element!")

    else:
        if elementContains:
            e = d.find_element(
                By.XPATH,  "//a[text()[contains(.,'" + product + "')]]").click()
else:
    if element:
        e = d.find_element(
            By.XPATH,  "//*[normalize-space(text()) = '" + product + "']").click()

# Try to find excel information on the product page
try:
    e = d.find_element(
        By.XPATH,  "//*[text()[contains(.,'" + product + "')]]")
except:
    print("Could not find element!")
else:
    print("Added score to database!")
