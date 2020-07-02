# Author: Bapi Roy <mail2bapi@astrosoft.co.in>
# Date: 19 / 06 / 20

import sys
import os
import cloudscraper
from bs4 import BeautifulSoup
from os import path
from pathlib import Path
import magicA1`
import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Directory creator
def dir_creator(directory=''):
    dir_path = os.path.join(parent_dir, directory)
    print(dir_path)
    if not path.exists(dir_path):
        os.mkdir(dir_path)
        print("Directory '% s' created" % dir_path)

    return dir_path


# Get the name of lecture
def get_name(lecture_block=''):
    name = lecture_block.find("span", {'class': 'lecture-name'})
    print(name)
    return name.strip()


# Go to lecture page
def lecture_page(href='', name=''):
    lecture_path = dir_creator(href.split("/")[-1]+'-'+name.replace(" ", "-").replace("\\", ""))

    page_url = base_url + href
    browser.get(page_url)
    time.sleep(6)
    soup = BeautifulSoup(browser.page_source, 'html5lib')

    scraper = cloudscraper.create_scraper()

    # Seek for Textual - lecture-text-container
    html = ''
    for text_content in soup.findAll('div', {'class': 'lecture-text-container'}):
        html += str(text_content)

        # Seek for Image
        try:
            for img in text_content.findAll('img'):
                if "data-imageloader-src" in str(img):
                    # Download file
                    src = img['data-imageloader-src'].split("/")[-1] + '.png'
                    file_name = Path(lecture_path + "/" + src)
                    response = scraper.get(img['data-imageloader-src'], )
                    file_name.write_bytes(response.content)

                    # Adjusting the image path
                    img_src = img['data-imageloader-src'].split("/")[-1]
                    img_type = magic.from_file(str(file_name), mime=True)
                    html = html.replace(img_src, img_src + "." + img_type.split("/")[-1])

                    # Adding correct file extension to file
                    os.rename(str(file_name), str(file_name).replace('png', img_type.split("/")[-1]))

                else:
                    # Download file
                    src = img['src'].split("/")[-1] + '.png'
                    file_name = Path(lecture_path + "/" + src)
                    response = scraper.get(img['src'], )
                    file_name.write_bytes(response.content)

                    # Adjusting the image path
                    img_src = img['src'].split("/")[-1]
                    img_type = magic.from_file(str(file_name), mime=True)
                    html = html.replace(img['src'], img_src + "." + img_type.split("/")[-1])

                    # Adding correct file extension to file
                    os.rename(str(file_name), str(file_name).replace('png', img_type.split("/")[-1]))
        except KeyError:
            pass

        # Seek for Video, pdf, Audio - video-options
        for video_link in soup.findAll('a', {'class': 'download'}):
            try:
                # Download file
                src = video_link['data-x-origin-download-name']
                file_name = Path(lecture_path + "/" + src)
                # downloading large file
                with scraper.get(video_link['href'], stream=True) as response:
                    response.raise_for_status()
                    with open(file_name, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:  # filter out keep-alive new chunks
                                f.write(chunk)
                                f.flush()
                file_name.write_bytes(response.content)
            except KeyError:
                pass


        # Download Html file
        try:
            html = html.replace("data-imageloader-src", "src")
            html = html.replace("https://www.filepicker.io/api/file/", "")
            src = 'index.html'
            file_name = Path(lecture_path + "/" + src)
            file_name.write_text(html)
        except KeyError:
            pass

# entry point
def main(content=''):
    # Scraping
    soup = BeautifulSoup(content, 'html5lib')

    # Iterate through all lectures
    for lecture in soup.findAll('a', {'class': 'item'}):
       print(lecture["href"])
       name = lecture.get_text().replace("Start", "").replace("\n", "")
       name = re.sub('[^A-Za-z0-9]+', '-',  name)
       print(name)

       lecture_page(lecture["href"], name)



if __name__== "__main__":
    # Clean the storage folder
    os.system("rm -rf storage/*")

    # kill any firefox instance
    os.system("pgrep firefox | xargs kill")

    # Base url
    base_url = "https://iwillteachyoualanguage.teachable.com/"
    parent_dir = os.path.dirname(os.path.abspath(__file__)) + "/storage"

    # Login
    url = 'https://sso.teachable.com/secure/136458/users/sign_in?clean_login=true&reset_purchase_session=1'

    options = Options()
    options.headless = True
    options.accept_insecure_certs = True
    browser = webdriver.Firefox(options=options)
    browser.get(url)
    time.sleep(5)

    # Scraping
    page_source = browser.page_source

    # filling the form
    username = browser.find_element_by_id("user_email")
    password = browser.find_element_by_id("user_password")

    username.send_keys("") # user email
    password.send_keys("") #user Password

    browser.find_element_by_name("commit").click()
    print("Logged in")

    # Load/Create the session
    url = sys.argv[1]

    # Scraping
    browser.get(url)
    time.sleep(4)

    main(browser.page_source)

    browser.close()
