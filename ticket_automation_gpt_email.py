from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import os
import io
import time
import subprocess
import threading
from gemini_api import ImageAnalyzer
import whatab_screenshot
from chrome_utils import start_chrome, setup_driver
from contacts import contacts  # contacts.py에서 contacts 딕셔너리 가져오기

### ember로 시작하는 ID는 변할 수 있음 = 프로그램이 고장날 수 있음 변수 변경 필요

def scroll_and_click(driver, by, value):
    """주어진 XPath를 사용하여 화면을 스크롤 합니다."""
    element = driver.find_element(By.XPATH, value)
    driver.execute_script("arguments[0].scrollIntoView();", element)
    
def wait_and_click(driver, by, value):
    """주어진 XPath를 사용하여 요소가 클릭 가능할 때까지 기다린 후 클릭합니다."""
    element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((by, value)))
    element.click()

def wait_and_click_index(driver, by, value, index=1):
    elements = WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((by, value))
    )
    elements[index].click()
    return elements[index]

def wait_and_send_keys(driver, xpath, keys):
    """주어진 XPath를 사용하여 요소가 존재할 때까지 기다린 후 텍스트를 입력합니다."""
    element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, xpath)))
    element.send_keys(keys)

def select_from_dropdown(driver, by, dropdown_value, option_text, wait_for_loading_message=False):
    """드롭다운에서 주어진 옵션을 선택합니다."""

    if wait_for_loading_message:
        # "검색 중..." 메시지가 보일 때까지 대기
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '.ember-power-select-option--loading-message'))
        )

        # "검색 중..." 메시지가 사라질 때까지 대기
        WebDriverWait(driver, 30).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, '.ember-power-select-option--loading-message'))
        )

    options = driver.find_elements(By.CSS_SELECTOR, '.ember-power-select-option')
    contact_found = False

    for option in options:
        try:
            if option_text in option.text: # 연락처(option_text)가 포함된 옵션 찾기
                option.click()
                contact_found = True
                break
        except:
            # 요소가 더 이상 유효하지 않다면, 다시 찾습니다.
            options = driver.find_elements(By.CSS_SELECTOR, '.ember-power-select-option')
            continue # 다음 옵션으로 넘어갑니다.

    if not contact_found:
        print(f"'{option_text}'를 찾을 수 없습니다.")

def drag_and_drop_image(driver, file_path):
    # 이미지 업로드를 위한 버튼 클릭
    insert_image_button = driver.find_element(By.XPATH, "//button[@data-cmd='insertImage' and @type='button']")
    insert_image_button.click()

    # 파일 입력 요소를 찾을 때까지 대기
    # file_input = driver.find_element(By.ID, "fr-image-upload-layer-1")
    file_input = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )

    # 파일 경로를 절대 경로로 변환
    absolute_file_path = os.path.abspath(file_path)

    # 파일 경로를 입력하여 업로드
    file_input.send_keys(absolute_file_path)

    # 업로드 완료 대기 (class가 없어질 때까지)
    WebDriverWait(driver, 30).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "fr-fil fr-dib fr-uploading"))
    )

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//img[@data-attachment='[object Object]']"))
    )
    print("업로드 완료!")



def drag_and_drop_file(driver, file_path):
    # 절대 경로로 변환
    absolute_file_path = os.path.abspath(file_path)

    # 파일 input 드래그 앤 드롭 요소 찾기
    drop_zone = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@data-test-id='drag-and-drop-component']"))
    )

    # JavaScript로 드롭 이벤트 발생
    driver.execute_script("""
        const dropZone = arguments[0];
        const dataTransfer = new DataTransfer();
        const file = new File([''], arguments[1]); // 빈 파일 생성
        dataTransfer.items.add(file);
        
        const dropEvent = new DragEvent('drop', {
            dataTransfer: dataTransfer,
            bubbles: true,
            cancelable: true,
        });

        dropZone.dispatchEvent(dropEvent);
    """, drop_zone, absolute_file_path)

    # 잠시 대기 (업로드 확인용)
    time.sleep(5)

def create_ticket(driver, contact, subject, from_input, class_name, inquiry_type, priority, description, state, group):
    #보낸사람
    from_xpath = "//div[contains(@class, 'ember-power-select-trigger') and @role='button']"
    wait_and_click(driver, By.XPATH, from_xpath)
    time.sleep(0.5)
    select_from_dropdown(driver, By.CLASS_NAME, from_xpath , from_input)

    # 받는 사람 입력
    xpath = "//div[@data-test-id='requester']"
    input_xpath = "//input[@class='ember-power-select-search-input ember-power-select-search-input-trigger']"
    wait_and_click(driver, By.XPATH, xpath)
    # 이메일이 여러 개일 경우 참조 추가 클릭
    if 1 < len(contact):
        try:
            wait_and_send_keys(driver, input_xpath, contact[0])
            select_from_dropdown(driver, By.CLASS_NAME, "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]", contact[0], wait_for_loading_message=False)

            cc_link = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-test-id='showCcLink']")))
            cc_link.click()  # 참조 추가 클릭
            
            for email in contact[1:]:  # 첫 번째 이메일을 제외한 나머지 이메일 추가
                email_input = driver.find_element(By.CSS_SELECTOR, "input.ember-power-select-trigger-multiple-input")
                email_input.send_keys(email)  # 이메일 추가
                
                # "검색 중..." 메시지가 보일 때까지 대기
                try:
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '.ember-power-select-option--loading-message'))
                    )
                    WebDriverWait(driver, 5).until(
                        EC.invisibility_of_element_located((By.CSS_SELECTOR, '.ember-power-select-option--loading-message'))
                    )
                except Exception as e:
                    print(f"로딩 메시지 대기 중 오류 발생: {e}")
                email_input.send_keys(Keys.RETURN)  # 엔터로 추가

            #제목
            subject_xpath  = "//input[@data-test-text-field='subject' and @name='subject' and @type='text']"
            # wait_and_click(driver, By.XPATH, subject)
            wait_and_send_keys(driver, subject_xpath , subject)

            # 설명 입력
            description_input = driver.find_element(By.CLASS_NAME, 'fr-view')  # 설명 입력 필드
            description_input.send_keys(description)
            driver.execute_script("arguments[0].scrollIntoView();", description_input)

            # 이미지 파일 경로
            image_path = 'monitoring_screenshot.png'
            drag_and_drop_image(driver, image_path)

            # 우선 순위
            priority_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
            wait_and_click_index(driver, By.XPATH, priority_xpath, 1)
            select_from_dropdown(driver, By.CLASS_NAME, priority_xpath, priority)

            # 상태
            state_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
            scroll = wait_and_click_index(driver, By.XPATH, state_xpath, 2)
            select_from_dropdown(driver, By.CLASS_NAME, state_xpath, state)
            driver.execute_script("arguments[0].scrollIntoView(true);", scroll)


            # 그룹 입력
            group_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
            wait_and_click_index(driver, By.XPATH, group_xpath, 3)

            input_xpath = "(//input[contains(@class, 'ember-power-select-search-input') and @placeholder='모두'])[1]"
            input_element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
            input_element.send_keys(group)

            group_xpath = "//div[@data-test-id='ember-power-select-options' and contains(@class, 'ember-power-select-options')]" 
            select_from_dropdown(driver, By.CLASS_NAME, group_xpath, group)

            # 문의 유형
            inquiry_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
            wait_and_click_index(driver, By.XPATH, inquiry_xpath, 4)
            select_from_dropdown(driver, By.CLASS_NAME, inquiry_xpath, inquiry_type)

            # 모니터링 분류
            class_xpath = "//div[@data-test-id='trigger-power-select']"
            wait_and_click_index(driver, By.XPATH, class_xpath, 5)

            class_input = "//input[@class='ember-power-select-search-input ember-power-select-search-input-trigger']"
            wait_and_send_keys(driver, class_input, class_name)

            class_text = "//div[@data-test-id='ember-power-select-options' and contains(@class, 'ember-power-select-options')]" 
            select_from_dropdown(driver, By.CLASS_NAME, class_text, class_name)

            # 티켓 생성 버튼 클릭
            time.sleep(0.5)
            create_xpath = "//button[@data-test-button='save-form']"
            wait_and_click(driver, By.XPATH, create_xpath)
            time.sleep(0.5)

        except Exception as e:
            print(f"참조 추가 중 오류 발생: {e}")
    else: # 이메일이 하나 일 경우 
        wait_and_send_keys(driver, input_xpath, contact[0])
        select_from_dropdown(driver, By.CLASS_NAME, "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]", contact[0], wait_for_loading_message=True)

        #제목
        subject_xpath  = "//input[@data-test-text-field='subject' and @name='subject' and @type='text']"
        # wait_and_click(driver, By.XPATH, subject)
        wait_and_send_keys(driver, subject_xpath , subject)

        # 설명 입력
        description_input = driver.find_element(By.CLASS_NAME, 'fr-view')  # 설명 입력 필드
        description_input.send_keys(description)
        driver.execute_script("arguments[0].scrollIntoView();", description_input)

        # 이미지 파일 경로
        image_path = 'monitoring_screenshot.png'
        drag_and_drop_image(driver, image_path)

        # 우선 순위
        priority_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
        wait_and_click_index(driver, By.XPATH, priority_xpath, 1)
        select_from_dropdown(driver, By.CLASS_NAME, priority_xpath, priority)

        # 상태
        state_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
        scroll = wait_and_click_index(driver, By.XPATH, state_xpath, 2)
        select_from_dropdown(driver, By.CLASS_NAME, state_xpath, state)
        driver.execute_script("arguments[0].scrollIntoView(true);", scroll)


        # 그룹 입력
        group_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
        wait_and_click_index(driver, By.XPATH, group_xpath, 3)

        input_xpath = "(//input[contains(@class, 'ember-power-select-search-input') and @placeholder='모두'])[1]"
        input_element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, input_xpath)))
        input_element.send_keys(group)

        group_xpath = "//div[@data-test-id='ember-power-select-options' and contains(@class, 'ember-power-select-options')]" 
        select_from_dropdown(driver, By.CLASS_NAME, group_xpath, group)

        # 문의 유형
        inquiry_xpath = "//div[@data-test-id='trigger-power-select' and contains(@class, 'trigger-power-select')]"
        wait_and_click_index(driver, By.XPATH, inquiry_xpath, 4)
        select_from_dropdown(driver, By.CLASS_NAME, inquiry_xpath, inquiry_type)

        # 모니터링 분류
        class_xpath = "//div[@data-test-id='trigger-power-select']"
        wait_and_click_index(driver, By.XPATH, class_xpath, 5)

        class_input = "//input[@class='ember-power-select-search-input ember-power-select-search-input-trigger']"
        wait_and_send_keys(driver, class_input, class_name)

        class_text = "//div[@data-test-id='ember-power-select-options' and contains(@class, 'ember-power-select-options')]" 
        select_from_dropdown(driver, By.CLASS_NAME, class_text, class_name)

        # 티켓 생성 버튼 클릭
        create_xpath = "//button[@data-test-button='save-form']"
        wait_and_click(driver, By.XPATH, create_xpath)

def freshdesk_login_screenshot(driver, login_url, username, password, target_url, output_file, result, message_info):
    try:
        driver.get(login_url)
        time.sleep(5)

        # my-accounts-container 요소가 로딩되는지 확인
        if WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='my-accounts-container']"))):
            # my-accounts-container가 로딩되면 실행
            driver.get(target_url)
            WebDriverWait(driver, 30).until(EC.url_to_be(target_url))

        else:
            # username 요소가 로딩되는지 확인
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='username']")))
            # username이 로딩되면 실행
            wait_and_send_keys(driver, "//input[@name='username']", username)
            wait_and_send_keys(driver, "//input[@name='password']", password)
            wait_and_click(driver, By.XPATH, "//button[@type='submit']")

            WebDriverWait(driver, 30).until(EC.url_changes(login_url))
            WebDriverWait(driver, 30).until(EC.url_contains('https://support.freshdesk.com/a/tickets/new'))
            driver.get(target_url)

        # driver.get(target_url)

        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'ember-power-select-trigger') and @role='button']")))

        # message_info에서 필요한 정보 추출
        project_name = message_info.get("프로젝트 이름", "").replace("'", '"')
        server_name = message_info.get("서버 이름", "")
        event_message = message_info.get("이벤트 메시지", "")

        # project_name에 따라 이메일 리스트 가져오기
        email_list = contacts.get(project_name, [])

        print(f"project_name: {project_name}, email_list: {email_list}")

        create_ticket(
            driver,
            contact=email_list,
            subject= f"[{project_name}] {server_name} 알람 '{event_message}' 발생 관련 내용 전달드립니다.",
            from_input="매니지드 서비스",
            class_name="경고 및 알림",
            inquiry_type="모니터링",
            priority="낮음",
            description=result,
            state="대기 중(고객답변)",
            group="SRE"
        )

        png = driver.get_screenshot_as_png()
        if png:
            im = Image.open(io.BytesIO(png))
            im.save(output_file)
            print(f"Screenshot saved as {output_file}")
        else:
            print("Screenshot data is empty.")
    finally:
        driver.quit()

def main(driver, whatab_target_url, whatab_link_text, keywords, message_info):
    API_KEY = ""  # 본인의 Google API 키 입력
    MODEL="gemini-1.5-flash"
    image_path = "monitoring_screenshot.png"  # 로컬 이미지 파일 경로 입력
    login_url = "https://freshworks.com/login"
    username = "jaehee"
    password = ""
    target_url = "https://support.freshdesk.com/a/tickets/compose-email"
    output_file = "ticket.png"

    # 와탭 로그인 및 스크린샷 
    whatab_login_url = "https://service.whatap.io/account/login"
    whatab_username = "jaehee"
    whatab_password = ""
    whatab_target_url = whatab_target_url
    whatab_link_text = whatab_link_text
    whatab_output_file = "monitoring_screenshot.png"

    # 크롬 실행
    port = start_chrome(2)
    driver_whatab = setup_driver(port)

    # thread = threading.Thread(target=whatab_screenshot.login_and_take_screenshot(whatab_login_url, whatab_username, whatab_password, whatab_target_url, whatab_link_text, whatab_output_file))
    whatab_screenshot.login_and_take_screenshot(driver_whatab, whatab_login_url, whatab_username, whatab_password, whatab_target_url, whatab_link_text, whatab_output_file, keywords)
    # thread.start()


    # LLM APi 
    analyzer = ImageAnalyzer(API_KEY, MODEL)
    result = analyzer.analyze_image(image_path, message_info)
    # LLM API 응답 print
    # result  = "테스트"
    # print("AI의 응답:", result)

    freshdesk_login_screenshot(driver, login_url, username, password, target_url, output_file, result, message_info)

if __name__ == "__main__":
    port = start_chrome(1, headless=False)
    driver = setup_driver(port, headless=False)
    message_info = {
    "알림 레벨": "Critical",
    "프로젝트 번호": "12345",
    "프로젝트 이름": "프로젝트1",
    "서버 이름": "server1",
    "이벤트 메시지": "Memory Used > 90 %",
    "이벤트 시작 시간": "2024-08-29 18:51:40 +0900"
    }
    main(driver, whatab_target_url="https://service.whatap.io/v2/project/sms/12345/server/list", whatab_link_text="server1",keywords="memory", message_info=message_info)
