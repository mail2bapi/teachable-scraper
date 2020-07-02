# Author: Bapi Roy <mail2bapi@astrosoft.co.in>
# Date: 19 / 06 / 20

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import pickle


url = 'https://sso.teachable.com/secure/136458/users/sign_in?clean_login=true&reset_purchase_session=1'

options = Options()
options.headless = True
browser = webdriver.Firefox(options=options)
browser.get(url)
time.sleep(3)

# Scraping
page_source = browser.page_source

# filling the form
username = browser.find_element_by_id("user_email")
password = browser.find_element_by_id("user_password")

username.send_keys("") # User email
password.send_keys("") # user Password

browser.find_element_by_name("commit").click()

# Saving session
pickle.dump(browser.get_cookies() , open("session.pkl", "wb"))

browser.close()

