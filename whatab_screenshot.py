from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import glob
import os
import time
from chrome_utils import start_chrome, setup_driver

def login(driver, login_url, username, password):
    driver.get(login_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_email"))).clear()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "id_email"))).send_keys(username)
    driver.find_element(By.ID, "id_password").clear()
    driver.find_element(By.ID, "id_password").send_keys(password)

    driver.find_element(By.ID, "btn_login").click()
    WebDriverWait(driver, 10).until(EC.url_changes(login_url))

def navigate_to_target(driver, target_url, link_text):
    driver.get(target_url)
    # 페이지가 완전히 로드될 때까지 기다리기
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )
    time.sleep(0.9)
    # 요소가 클릭 가능해질 때까지 대기
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, link_text))
    )
    element.click()

def wait_for_element(driver, element_id):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, element_id)))

def take_screenshot_of_panels(driver, prefix):
    panels = driver.find_elements(By.CLASS_NAME, 'PannelStyles__Container-iNykUX')
    screenshot_paths = []
    for idx, panel in enumerate(panels):
        screenshot_path = f'{prefix}_{idx + 1}.png'
        driver.execute_script("window.scrollTo(0, 0);")
        panel.screenshot(screenshot_path)
        screenshot_paths.append(screenshot_path)
        time.sleep(0.1)
    return screenshot_paths

def click_fourth_dropdown_item(driver, sorting_type):
    # 현재 설정된 정렬 방식 확인
    current_sorting = driver.find_element(By.XPATH, "//div[contains(@class, 'PannelStyles__Header-eIoeyX')]")

    # 설정된 정렬 방식에 따라 클릭할 항목 결정
    if sorting_type[0] == "memory":
        target_text = '메모리 내림차순'
    elif sorting_type[0] == "cpu":
        target_text = 'CPU 내림차순'
    else:
        return
        print("지원하지 않는 정렬 방식입니다.")

    # 현재 설정된 정렬 방식이 목표와 일치하지 않는 경우 클릭
    if target_text not in current_sorting.text:
        panels = driver.find_elements(By.CLASS_NAME, 'PannelStyles__Container-iNykUX')
        # 5번째 패널 클릭 (인덱스 4)
        if len(panels) >= 5:
            button = panels[4].find_element(By.XPATH, ".//button[contains(@class, 'Styles__Button-bDBZvm')]")
            button.click()  # 버튼 클릭

            # 목표 항목 클릭
            sorting_item = driver.find_element(By.XPATH, f"//li[contains(@class, 'ant-menu-item') and contains(., '{target_text}')]")
            sorting_item.click()
    else:
        print(f"현재 이미 '{target_text}'으로 설정되어 있습니다.")


def click_specific_disk_button(driver):
    panels = driver.find_elements(By.CLASS_NAME, 'PannelStyles__Container-iNykUX')

    # 4번째 패널 클릭 (인덱스 3)
    if len(panels) >= 4:
        panels[3].click()  # 4번째 패널 클릭
        
        # 버튼 클릭
        buttons = panels[3].find_elements(By.XPATH, ".//button[contains(@class, 'Styles__Button-bDBZvm jUvbbD')]")
        if buttons:
            buttons[2].click()  # 여기에서 원하는 버튼의 인덱스 지정 
    else:
        print("패널이 4개 이상이 아닙니다.")


def take_screenshot_of_process(driver, prefix, start_index=6):
    panels = driver.find_elements(By.CLASS_NAME, 'PannelStyles__Container-iNykUX')
    screenshot_paths = []
    for idx, panel in enumerate(panels):
        # 인덱스가 start_index 이상인 경우에만 스크린샷을 찍음
        if idx >= start_index:
            # 데이터가 없음을 나타내는 메시지가 있는지 확인
            no_data_message = panel.find_elements(By.CLASS_NAME, 'ServerResourceListStyle__NoDataMessage-fAyDwk')
            if no_data_message:
                print(f"패널 {idx + 1}은 데이터가 없습니다. 스크린샷을 찍지 않습니다.")
                continue  # 데이터가 없으면 스크린샷을 찍지 않음
            
            screenshot_path = f'{prefix}_{idx + 1}.png'
            driver.execute_script("window.scrollTo(0, 0);")
            panel.screenshot(screenshot_path)
            screenshot_paths.append(screenshot_path)
            time.sleep(0.1)
    return screenshot_paths

def merge_images(image_paths, output_path):
    images = []
    for path in image_paths:
        # 제외할 이미지 경로
        if path in ['panel_3.png', 'panel_6.png']:
            continue
        img = Image.open(path)
        images.append(img)

    if images:
        # 첫 번째 이미지 기준으로 최대 너비와 총 높이 설정
        widths, heights = zip(*(img.size for img in images))
        total_height = sum(heights)
        max_width = max(widths)

        # 새 이미지 생성
        new_image = Image.new('RGB', (max_width, total_height))

        # 이미지를 세로로 합치기
        y_offset = 0
        for img in images:
            new_image.paste(img, (0, y_offset))
            y_offset += img.height

        new_image.save(output_path)


def cleanup_files(file_prefix, count):
    for i in range(1, count + 1):
        img_file = f'{file_prefix}_{i}.png'
        if os.path.exists(img_file):
            os.remove(img_file)

def delete_files():
    base_directory = os.getcwd()

    # panel 파일 삭제
    panel_files = glob.glob(os.path.join(base_directory, "panel*.png"))
    for file in panel_files:
        if os.path.exists(file):  # 파일 존재 여부 확인
            try:
                os.remove(file)
                print(f"{file} 삭제 성공")
            except Exception as e:
                print(f"{file} 삭제 실패: {e}")

    # process PNG 파일 삭제
    process_files = glob.glob(os.path.join(base_directory, "process*.png"))
    for file in process_files:
        if os.path.exists(file): 
            try:
                os.remove(file)
                print(f"{file} 삭제 성공")
            except Exception as e:
                print(f"{file} 삭제 실패: {e}")

def login_and_take_screenshot(driver, login_url, username, password, target_url, link_text, output_file, keyword):
    # try:
    login(driver, login_url, username, password)
    navigate_to_target(driver, target_url, link_text)
    wait_for_element(driver, "CPU Usage")
    time.sleep(3)

    # 첫 번째 패널 스크린샷
    prefix = 'panel'
    # keywork값 변수가 cpu,memory로 왔을 경우 프로세스 해당 내림차순 클릭
    click_fourth_dropdown_item(driver, keyword)
    #스크린 샷 찍기
    screenshot_paths = take_screenshot_of_panels(driver, prefix)

    # keywork값 변수가 disk로 왔을 경우 disk 상세보기 클릭
    if keyword == "disk": 
        click_specific_disk_button(driver)
        # 디스크 스크린샷 찍기
        prefix = 'disk'
        new_screenshot_paths = take_screenshot_of_process(driver, prefix, start_index=6)
        screenshot_paths.extend(new_screenshot_paths)
        #닫기 버튼 클릭
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'ant-drawer-close')]"))
        )
        button.click()

    # # 프로세스 패널의 해당 <div> 아래의 버튼 요소 찾기 (상세 프로세스 모니터링 진입)
    # parent_div = driver.find_element(By.CLASS_NAME, 'ProcessTableStyle__NameGroup-dklpga')
    # button = parent_div.find_element(By.CLASS_NAME, 'Styles__Button-bDBZvm')
    # button.click()
    # # 커서 위치 제거용 클릭
    # try:
    #     no_data_message = WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.CLASS_NAME, 'ServerResourceListStyle__NoDataMessage-fAyDwk'))
    #     )
    #     no_data_message.click()
    # except:
    #     pass

    # #웹 로딩 대기
    # time.sleep(0.5)

    # # 프로세스 패널 스크린샷 추가
    # prefix = 'process'
    # new_screenshot_paths = take_screenshot_of_process(driver, prefix, start_index=6)
    # screenshot_paths.extend(new_screenshot_paths)

    # 사용할 이미지 경로 리스트
    image_paths = glob.glob('panel_*.png') + glob.glob('disk_*.png') + glob.glob('process_*.png')

    # 이미지 합치기
    merge_images(image_paths, output_file)

    # 원본 패널 파일 삭제
    # cleanup_files('panel', len(screenshot_paths))
    delete_files()
    print(f"Screenshot saved as {output_file}")

def main(driver, whatab_target_url, whatab_link_text, keyword):
    whatab_login_url = "https://service.whatap.io/account/login"
    whatab_username = "jaehee"
    whatab_password = ""
    whatab_output_file = "monitoring_screenshot.png"
    login_and_take_screenshot(driver, whatab_login_url, whatab_username, whatab_password, whatab_target_url, whatab_link_text, whatab_output_file, keyword)

if __name__ == "__main__":
    port = start_chrome(2)
    driver = setup_driver(port)
    whatab_login_url = "https://service.whatap.io/account/login"
    whatab_target_url = "https://service.whatap.io/v2/project/sms/12345/server/list"  # 타겟 URL 정의
    whatab_link_text = "server1"  # 링크 텍스트 정의
    whatab_output_file = "monitoring_screenshot.png"
    keyword = "cpu"
    main(driver, whatab_target_url, whatab_link_text, keyword)  # main 함수 호출 추가
