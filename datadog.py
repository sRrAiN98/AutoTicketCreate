# 데이터독 대쉬보드를 캡쳐하여 저장하는 파일
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from chrome_utils_alone import start_chrome, setup_driver

# 데이터 독 시간 설정한 URL 기입
url = "https://app.datadoghq.com/dashboard/~~시간URL"

#chrome_utils_alone.py과 같은 폴더에서 실행
port = start_chrome(headless=False)
driver = setup_driver(headless=False)

driver.get(url)

# 페이지가 로드될 때까지 대기
WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, "multi-size-layout__grid-item")))

# 다수의 객체 스크린샷 찍기
items = driver.find_elements(By.CLASS_NAME, "multi-size-layout__grid-item")

for index, item in enumerate(items):
    # 마우스 커서를 숨기기 위해 다른 요소에 클릭
    ActionChains(driver).move_to_element(driver.find_element(By.XPATH, '//*[@id="single-page-app_layout_page__main-content"]/div/header/div/div[3]/div')).click().perform()

    # 패널 제목 가져오기 (각 패널의 제목 요소를 찾기)
    title_element = item.find_element(By.XPATH, './/h3/span')  # 각 패널 내의 h3/span 요소 찾기
    title = title_element.text.strip().replace('/', '_').replace('\\', '_')  # 파일명에 사용할 수 없는 문자 처리

    # 스크린샷 찍기
    screenshot_path = f'{title}.png'
    item.screenshot(screenshot_path)  # 개별 객체의 스크린샷 찍기
    print(f"Screenshot saved as {screenshot_path}")

    # 각 객체의 위치로 스크롤
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });", item)