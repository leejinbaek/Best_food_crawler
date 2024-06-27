import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
#옵션 설정
options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

#드라이버 설정
driver = webdriver.Chrome(options=options)

#페이지 스크롤 함수
def page_down(num):
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)
        
#frame 변경 함수
def switch_frame(frame):
    driver.switch_to.default_content()
    driver.switch_to.frame(frame)
    
#페이지 개수 알아내는 함수
def switch_page():
    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    count = len(soup.find_all("a", class_="mBN2s"))
    return count
    

#크롤러 작성
def crawler(keyword):
    
    #url 접근
    url = f"https://map.naver.com"
    driver.get(url)
    time.sleep(3)

    #키워드 검색
    searchbox = driver.find_element(By.CLASS_NAME, "input_search")
    searchbox.send_keys(f"{keyword}")
    time.sleep(2)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(5)
    
    #페이지 스크롤
    switch_frame("searchIframe")
    page_down(100)
    
    #soup 만들기
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    foods_db = []
    
    def scrap_page(soup):
        foods = soup.find_all("div", class_="CHC5F")
        
        for food in foods:
            name = food.find("span", class_="place_bluelink TYaxT").text
            menu = food.find("span", class_="KCMnt").text
            status_review = food.find_all("span", class_="h69bs")
            rate = food.find("span", class_="h69bs orXYY")
            if rate:
                rate = rate.text
                status = status_review[0].text
                review = status_review[2].text
                
            else:
                rate = None
                status = status_review[0].text
                review = status_review[1].text
            
            
            food_data = {
                "가게명" : name,
                "요리" : menu,
                "운영상태" : status,
                "별점" : rate,
                "리뷰수" : review
            }
            foods_db.append(food_data)
    scrap_page(soup)
    print(foods_db)
crawler("강남역맛집")
