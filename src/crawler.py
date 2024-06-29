from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import traceback
import time
import csv

#키워드 입력 및 실행
keyword = input("키워드를 입력하세요: ")

#옵션 설정
options = Options()
# options.add_argument("headless")
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

#드라이버 설정
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

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
    

#크롤러 작성
def crawler(keyword):
    try:
        
        #url 접근
        url = "https://map.naver.com"
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input_search")))

        #키워드 검색
        searchbox = driver.find_element(By.CLASS_NAME, "input_search")
        if searchbox != driver.find_element(By.CLASS_NAME, "input_search"):
            raise ValueError("search box not found")
        searchbox.send_keys(f"{keyword}")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "button_search")))
        searchbox.send_keys(Keys.ENTER)
        wait.until(EC.presence_of_element_located((By.ID, "searchIframe")))

        #페이지 스크롤
        switch_frame("searchIframe")
        page_down(100)
        
        
        #soup 만들기
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        
        
        #저장공간 만들기
        foods_db = []
        
        
        
        def scrap_page(soup):
            foods = soup.find_all("div", class_="CHC5F")
            
            for food in foods:
                name = food.find("span", class_="place_bluelink TYaxT").text
                menu = food.find("span", class_="KCMnt").text
                new = food.find("span", class_= "h69bs DjPAB")
                status = food.find("span", class_="h69bs MqNOY")
                rate = food.find("span", class_="h69bs orXYY")
                reviews = food.find_all("span", class_="h69bs")
                review = None
                #
                if status:
                    status = status.text
                else:
                    status = None
                #
                if rate:
                    rate = rate.text
                else:
                    rate = None
                #
                if new:
                    new = new.text
                else:
                    new = None
                #review 위치 파악
                if rate is not None and new is None:
                    if len(reviews) == 2:
                        review = reviews[1].text
                    elif len(reviews) > 2:
                        review = reviews[2].text
                elif rate is None and new is not None:
                    if len(reviews) > 2:
                        review = reviews[2].text
                elif rate is None and new is None:
                    if len(reviews) == 2:
                        review = reviews[0].text
                    elif len(reviews) == 1:
                        review = None
                    
                food_data = {
                    "가게명" : name,
                    "요리" : menu,
                    "개업" : new,
                    "운영상태" : status,
                    "별점" : rate,
                    "리뷰" : review
                }
                foods_db.append(food_data)
            
        #총 페이지 수 알아내기
        page_btn_list = soup.find_all("a", class_="mBN2s")
        page_num = len(page_btn_list)
                
        #페이지 넘기면서 크롤링 (페이지 수만큼 반복)
        for i in range(page_num):
            content = driver.page_source
            soup = BeautifulSoup(content, "html.parser")
            scrap_page(soup)
            
            if i < page_num - 1:
                next_page_btn = driver.find_elements(By.CLASS_NAME, "mBN2s")[i+1]
                next_page_btn.click()
                time.sleep(1)
                page_down(100)

        #크롤링 결과 파일로 저장
        with open(f"{keyword}_navermap.csv", "w", newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["가게명", "요리", "개업", "운영상태", "별점", "리뷰"])
            for food in foods_db:
                writer.writerow(food.values())
        
        print("CSV파일이 성공적으로 저장되었습니다.")
        
    except Exception as e:
        print("An error occurred: ", e)
        print(traceback.format_exc())
        
    finally:
        driver.quit()



crawler(f"{keyword}")