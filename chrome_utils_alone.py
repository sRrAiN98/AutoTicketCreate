# 크롬 1개만 띄우는 버전의 베이스 파일
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pyautogui
import time
import os
import subprocess

# @@@@@ 필수 입력 란 chrome://settings/help 에서 크롬 버전 확인    ↓여기에 크롬 버전 입력해서 다운로드 @@@@@@@
# https://storage.googleapis.com/chrome-for-testing-public/128.0.6613.119/win64/chromedriver-win64.zip  
chrome_driver_path = r"C:\Users\jaehee\Downloads\automatic\chromedriver-win64\chromedriver.exe"

def is_chrome_running():
    try:
        output = subprocess.check_output(['tasklist'], encoding='mbcs')
        if 'chrome.exe' in output:
            for line in output.splitlines():
                if 'chrome.exe' in line and '--remote-debugging-port=9222' in line:
                    return True
        return False
    except subprocess.CalledProcessError:
        return False

def start_chrome(headless=True):
    # 현재 폴더에 유저 데이터 디렉토리 생성
    current_dir = os.getcwd()
    user_data_dir = os.path.join(current_dir, 'User Data')
    port = 9222  # 기본 포트 설정

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    if is_chrome_running():
        print("Chrome이 이미 실행중입니다.")
        return 

    screen_width, screen_height = pyautogui.size()

    # 크롬 실행
    if headless:
        subprocess.Popen([
            chrome_path,
            f'--remote-debugging-port={port}',
            f'--user-data-dir={user_data_dir}',
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            f'--window-size={screen_width},{screen_height}',  # 자동으로 화면 크기 설정
            '--force-device-scale-factor=1',
            '--high-dpi-support=1'
        ])
    else:
        subprocess.Popen([
            chrome_path,
            f'--remote-debugging-port={port}',
            f'--user-data-dir={user_data_dir}',
            '--force-device-scale-factor=1',
            '--high-dpi-support=1'
        ])

    time.sleep(1)

    return port


def setup_driver(headless=True):
    os.environ['WDM_SSL_VERIFY'] = '0'  # SSL 인증서 검증 비활성화
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:9222")  # 포트 설정

    service = Service(executable_path=chrome_driver_path)
    # service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=chrome_options)
