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
    body = driver.find_element(By.CSS_SELECTOR, ".XUrfU")
    body.click()
    
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

#크롤러 작성
def crawler(keyword):
    
    #url 접근
    url = f"https://map.naver.com"
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "input_search")))

    #키워드 검색
    searchbox = driver.find_element(By.CLASS_NAME, "input_search")
    searchbox.send_keys(f"{keyword}")
    time.sleep(2)
    searchbox.send_keys(Keys.ENTER)
    time.sleep(5)
    
    #페이지 스크롤 _____________--막힘
    scrpage = driver.find_element(By.CLASS_NAME, "body.place_on_pcmap")
    scrpage.click()
    page_down(40)
    
    driver.quit()

crawler("강남역맛집")
