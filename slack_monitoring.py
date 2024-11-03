from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from PIL import Image
import time
import threading
import re
import asyncio
import queue
import io
import ticket_automation_gpt_email
# import ticket_automation_gpt
from chrome_utils import start_chrome, setup_driver
from move_mouse import move_mouse

# 작업 큐 생성
task_queue = queue.Queue()

def workspace_login(driver, workspace):
    driver.get(workspace)
    time.sleep(1)
    # 현재 URL 확인
    current_url = driver.current_url
    if "app.slack.com/workspace-signin" in current_url:    
        domain_input = driver.find_element(By.ID, "domain")
        domain_input.send_keys("sre-datadog-temp")

        # 버튼 클릭
        submit_button = driver.find_element(By.CSS_SELECTOR, ".c-button[data-qa='submit_team_domain_button']")
        submit_button.click()

    # 특정 요소가 로딩될 때까지 대기
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".c-message_attachment__text[data-qa='message_attachment_text']"))
    )

def process_tickets():
    while True:
        try:
            # 큐에서 작업 가져오기
            ticket_data = task_queue.get()
            # if ticket_data is None:  # 종료 신호
            #     break
            driver_ticket, whatab_target_url, oname, found_keywords, message_info = ticket_data
            print("큐 처리 시작"+ datetime.now().strftime("%H:%M"))
            ticket_automation_gpt_email.main(driver_ticket, whatab_target_url, oname, found_keywords, message_info)
            task_queue.task_done()
        except Exception as e:
            print(f"티켓 처리 중 오류 발생: {e}")

def monitor_slack(driver):
    slack_url = "https://app.slack.com/client/T01TXTSHL6L/C01TMCP7ZH7"
    workspace_login(driver, slack_url)

    #티켓용 브라우저
    # port = start_chrome(1, headless=False)
    # driver_ticket = setup_driver(port, headless=False)
    port = start_chrome(1)
    driver_ticket = setup_driver(port)

    last_message = None

    while True:
        try:
            # 메시지 요소를 찾아서 마지막 메시지 확인
            messages = driver.find_elements(By.XPATH, '//div[@data-qa="virtual-list-item"]')

            if messages:
                # 가장 최근 메시지의 pretext 가져오기
                last_message_element = messages[-1].find_element(By.XPATH, './/span[@class="c-message_attachment__pretext" and @data-qa="message_attachment_pretext"]')
                current_message = last_message_element.text if last_message_element else None

                if last_message != current_message:
                    print(f"새 메시지: {current_message}")
                    last_message = current_message

                    # 알림 내용 추출
                    attachment = messages[-1].find_element(By.XPATH, './/div[@class="c-message_attachment" and @data-qa="message_attachment_default"]')
                    attachment_text = attachment.find_element(By.XPATH, './/span[@class="c-message_attachment__text" and @data-qa="message_attachment_text"]').text

                    #알림 내용을 줄 단위로 분리
                    lines = attachment_text.split('\n')

                    # 정보 초기화
                    alert_level = ""
                    project_number = ""
                    project_name = ""
                    server_name = ""
                    event_message = ""
                    event_start = "" 

                    # 알림 위험도
                    alert_level_match = re.search(r'\[(\w+)\]', last_message)
                    alert_level = alert_level_match.group(1) if alert_level_match else ""

                    # 각 줄을 확인하여 정보 추출
                    for line in lines:
                        if "프로젝트 번호" in line or "프로젝트 코드" in line:
                            project_number_match = re.search(r'(?:프로젝트 번호|프로젝트 코드)\s*:\s*(\d+)', line)
                            project_number = project_number_match.group(1) if project_number_match else ""
                        elif "프로젝트 이름" in line:
                            project_name_match = re.search(r'프로젝트 이름\s*:\s*([^\n]+)', line)
                            project_name = project_name_match.group(1).strip() if project_name_match else ""
                        elif "서버 이름" in line:
                            server_name_match = re.search(r'서버 이름\s*:\s*([^\n]+)', line)  
                            server_name = server_name_match.group(1).strip() if server_name_match else ""
                        elif "메시지" in line or "이벤트 메시지" in line:
                            event_message_match = re.search(r'(?:메시지|이벤트 메시지)\s*:\s*([^\n]+)', line)
                            event_message = event_message_match.group(1).strip() if event_message_match else ""
                        elif "이벤트 시작 시간" in line:
                            event_start_match = re.search(r'이벤트 시작 시간\s*:\s*([^\n]+)', line) 
                            event_start = event_start_match.group(1).strip() if event_start_match else ""

                    # 모든 필수 정보가 존재하는지 확인
                    message_info = {
                        "알림 레벨": alert_level,
                        "프로젝트 번호": project_number,
                        "프로젝트 이름": project_name,
                        "서버 이름": server_name,
                        "이벤트 메시지": event_message,
                        "이벤트 시작 시간": event_start
                    }

                    print("추출된 정보:", message_info)

                    # 키워드 리스트
                    keywords = ["cpu", "memory", "disk"]

                    # 조건 확인 후 ticket_automation_gpt.main() 호출
                    if alert_level == "Critical":
                        found_keywords = [keyword for keyword in keywords if keyword.lower() in event_message.lower()]
                        
                        if found_keywords:
                            pcode = project_number
                            oname = server_name
                            whatab_target_url = f"https://service.whatap.io/v2/project/sms/{pcode}/server/list"
                            print(whatab_target_url, oname)

                            # 작업을 큐에 추가
                            task_queue.put((driver_ticket, whatab_target_url, oname, found_keywords, message_info))
                            # ticket_automation_gpt_email.main(driver_ticket, whatab_target_url, oname, found_keywords, message_info)

            # 잠시 대기 후 다시 확인
            time.sleep(2)

        except Exception as e:
            print(f"{datetime.now().strftime('%H:%M')} 오류 발생: {e}")
            time.sleep(60)
            driver.execute_script("arguments[0].scrollIntoView();", messages[-1])

def debug(driver):
    while True:
        try:
            # 디버깅
            png = driver.get_screenshot_as_png()
            if png:
                im = Image.open(io.BytesIO(png))
                im.save("debug.png")
                print("Screenshot saved as debug.png")
            else:
                print("Screenshot data is empty.")
        except Exception as e:
            print(f"Error in debug: {e}")

        time.sleep(300)  # 1분 대기


async def main():
    # 크롬 백그라운드
    port = start_chrome(3)
    driver_slack = setup_driver(port)

    # 크롬 창 띄우기
    # port = start_chrome(3, headless=False)
    # driver_slack = setup_driver(port, headless=False)

    # 티켓 처리 스레드 시작
    ticket_thread = threading.Thread(target=process_tickets)                          
    ticket_thread.daemon = True
    ticket_thread.start()

    # Slack 모니터링 스레드 시작
    monitor_thread = threading.Thread(target=monitor_slack, args=(driver_slack,))
    monitor_thread.daemon = True
    monitor_thread.start()

    # 디버깅 스레드 시작
    debug_thread = threading.Thread(target=debug, args=(driver_slack,))
    debug_thread.daemon = True
    debug_thread.start()

    # 비동기 마우스 이동 실행
    await move_mouse()


if __name__ == "__main__":
    asyncio.run(main())

