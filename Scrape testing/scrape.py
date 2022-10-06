from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.common.keys import Keys

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options

chrome_options = Options()

chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('start-maximized')

d = webdriver.Chrome(service=Service(
    ChromeDriverManager
    ().install()), chrome_options=chrome_options)
product = 'Energy drink'

d.get('https://www.jumbo.com/')

try :
    element = WebDriverWait(d, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Weigeren')]"))
    )
finally:
    if element:
        d.find_element(By.XPATH, "//*[contains(text(), 'Weigeren')]").click()
    
try :
    element = WebDriverWait(d, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Waar ben je naar op zoek?']"))
    )
finally:
    if element:
        e = d.find_element(By.XPATH, "//input[@placeholder='Waar ben je naar op zoek?']")
        e = e.send_keys(product + '\n')
        




#e = d.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/header/div[2]/div[2]/div[1]/div[1]/form/div/input")
#e = d.find_element(By.XPATH, "//*[contains (text(), 'Waar ben je')]")


