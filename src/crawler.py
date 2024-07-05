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

#옵션 설정
options = Options()
options.add_argument("headless")
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

#드라이버 설정
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

#페이지 스크롤 함수
def page_down(num):
    body = driver.find_element(By.TAG_NAME, "body")
    body.click()
    
    for i in range(num):
        body.send_keys(Keys.PAGE_DOWN)
        
#페이지 스크롤&크롤링 함수
def scroll_page(driver, max_item):
    foods_db = []
    seen_data =set()
    
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")
    
    page_btn_list = soup.find_all("a", class_="mBN2s")
    page_num = len(page_btn_list)
    
    def scraper():
        content = driver.page_source
        soup = BeautifulSoup(content, "html.parser")
        page_down(100)
        foods = soup.find_all("li", class_="UEzoS rTjJo")
        
        for food in foods:
            name = food.find("span", class_="place_bluelink TYaxT").text
            menu = food.find("span", class_="KCMnt").text
            new = food.find("span", class_= "h69bs DjPAB")
            status = food.find("span", class_="h69bs MqNOY")
            rate = food.find("span", class_="h69bs orXYY")
            location = food.find("span", class_="h69bs kIy_t")
            comments = food.find_all("div", class_="u4vcQ")
            comment_text = [comment.find("span").text if comment.find("span") else "" for comment in comments]
            comment1 = None
            comment2 = None
            comment3 = None
            if comment_text:
                if len(comment_text) == 3:
                    comment1 = comment_text[0]
                    comment2 = comment_text[1]
                    comment3 = comment_text[2]
                elif len(comment_text) == 2:
                    comment1 = comment_text[0]
                    comment2 = comment_text[1]
                elif len(comment_text) == 1:
                    comment1 = comment_text[0]
            #
            if location:
                location.text
            else:
                location = None
            reviews = food.find_all("span", class_="h69bs")
            review = None
            #
            if status:
                status = status.text
            else:
                status = None
            #
            if rate:
                rate = rate.text.split("별점")[-1].strip()
            else:
                rate = None
            #
            if new:
                new = new.text
            else:
                new = None
            # review 위치 파악 (review 위치는 rate와 new 요소의 영향을 받음)
            # reviews 리스트는 [new,status,rate,review]로 이루어져 있음 
            if rate is not None and new is None:
                if location is None:
                    #[rate,review]의 경우
                    if len(reviews) == 2:
                        review = reviews[1].text.split("리뷰")[-1].strip()
                    #[status,rate,review]의 경우
                    elif len(reviews) > 2:
                        review = reviews[2].text.split("리뷰")[-1].strip()
                else:
                    #[status,rate,location]과 [rate,location]의 경우
                    if len(reviews) >= 2:
                        review = None
                        
            elif rate is None and new is not None:
                if location is None:
                    #[new,status,review]의 경우
                    if len(reviews) > 2:
                        review = reviews[2].text.split("리뷰")[-1].strip()
                    #[new,review]의 경우
                    elif len(reviews) == 2:
                        review =reviews[1].text.split("리뷰")[-1].strip()
                else:
                    #[new,status,location]과 [new,location]의 경우
                    if len(reviews) >= 2:
                        review = None
            elif rate is None and new is None:
                if location:
                    if status:
                        #[status,review,location]의 경우
                        if len(reviews) > 2:
                            review = reviews[1].text.split("리뷰")[-1].strip()
                        #[status,location]의 경우
                        elif len(reviews) == 2:
                            review = None
                    # new,status,rate가 존재하지 않을때 길이가 1이면(주소가 나옴 > 가게에 대한 정보가 없으면 주소만 존재하는 것으로 예상)
                    # 길이가 2이면 [리뷰,위치]로 이루어진 리스트에서 0번 인덱스 값을 뽑아옴
                    else: 
                        # [location]의 경우
                        if len(reviews) == 1:
                            review = None
                        # [review,location]의 경우
                        elif len(reviews) == 2:
                            review = reviews[0].text.split("리뷰")[-1].strip()
                    
            food_data = {
                "가게명" : name,
                "요리" : menu,
                "개업" : new,
                "운영상태" : status,
                "별점" : rate,
                "리뷰수" : review,
                "리뷰1" : comment1,
                "리뷰2" : comment2,
                "리뷰3" : comment3
                
            }
            food_data_tuple = tuple(food_data.items())
            #seen_data와food_data_tuple의 비교를 통해 seen_data에 없는 데이터만 크롤링 하도록 설정
            if food_data_tuple not in seen_data:
                seen_data.add(food_data_tuple)
                foods_db.append(food_data)
            #설정한 데이터의 수만큼만 수집하도록 설정
            if len(foods_db) >= max_item:
                break
    #scraper실행
    scraper()
    
    #데이터의 수를 충족시키지 못했을 때 다음 페이지로 넘어간 후 이어서 데이터를 수집하도록 설계
    for i in range(page_num):
            if i < page_num - 1 and len(foods_db) < max_item:
                next_page_btn = driver.find_elements(By.CLASS_NAME, "mBN2s")[i+1]
                next_page_btn.click()
                time.sleep(1)
                scraper()
    
    # 리뷰 수 기준으로 정렬, 리뷰 수가 같으면 별점 기준으로 정렬
    foods_db.sort(key=lambda x: (int(x["리뷰수"].replace('999+', '1000')) if x["리뷰수"] else 0, float(x["별점"]) if x["별점"] else 0), reverse=True)

# 정렬 후 리뷰 수를 다시 '999+'로 변환
    for food in foods_db:
        if food["리뷰수"] == 1000:
            food["리뷰수"] = '999+'

    return foods_db

#크롤러 작성
def main():
    try:
        #데이터 수 입력
        while True:
            try:    
                max_item = int(input("수집할 데이터의 수를 입력하세요: "))
                break
            except ValueError:
                print("올바른 숫자를 입력하세요.")
        #키워드 입력
        keyword = input("키워드를 입력하세요: ")
        
        #url 접근
        url = "https://map.naver.com"
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "input_search")))

        #키워드 검색
        searchbox = driver.find_element(By.CLASS_NAME, "input_search")
        if searchbox != driver.find_element(By.CLASS_NAME, "input_search"):
            raise ValueError("search box not found")
        searchbox.send_keys(f"{keyword}")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "btn_clear")))
        searchbox.send_keys(Keys.ENTER)
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "searchIframe")))
        print("\n자료 수집중.....\n")
        
        #크롤링
        foods_db = scroll_page(driver,max_item)
        
        #
        if len(foods_db) < max_item:
            print(f"해당 사이트에서 수집할 수 있는 최대 데이터 수는 {len(foods_db)}개 입니다.\n현재까지 수집한 데이터를 저장합니다.")
        
        #크롤링 결과 파일로 저장
        with open(f"{keyword}_navermap_TOP{len(foods_db)}.csv", "w", newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["가게명", "요리", "개업", "운영상태", "별점", "리뷰수", "리뷰1", "리뷰2", "리뷰3"])
            for food in foods_db:
                writer.writerow(food.values())
        
        print("CSV파일이 성공적으로 저장되었습니다.")
        
    except Exception as e:
        print("An error occurred: ", e)
        print(traceback.format_exc())
        
    finally:
        driver.quit()



main()