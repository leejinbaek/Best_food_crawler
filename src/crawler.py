import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time

options = Options()
options.add_argument("--start-maximized")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

def crawler(keyword):
    url = f"https://map.naver.com/p/search/{keyword}"
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "input_search")))

    searchbox = driver.find_element(By.ID, "input_search")
    searchbox.send_keys(f"{keyword}")
    time.sleep(2)
    
    searchbtn = driver.find_element(By.CLASS_NAME, "button_search")
    searchbtn.click()
    time.sleep(2)
    
    wheel_location = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "_pcmap_list_scroll_container")))
    action = ActionChains(driver)
    action.move_to_element(wheel_location).perform()
    
    for i in range(10):
        action.scroll_by_amount(0,100).perform()
    
    driver.quit()

crawler("강남역맛집")