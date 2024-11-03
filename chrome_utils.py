from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import subprocess

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

def start_chrome(option, headless=True):
    user_data_dirs = {
        1: (r"C:\Users\jaehee\Downloads\automatic\User Data", 9222),
        2: (r"C:\Users\jaehee\Downloads\automatic\WhatsApp Data", 9223),
        3: (r"C:\Users\jaehee\Downloads\automatic\Slack Data", 9224)
    }
    if option not in user_data_dirs:
        user_data_dir = r"C:\Users\jaehee\Downloads\automatic\User Data"
        port = 9222  # 기본 포트 설정

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir, port = user_data_dirs[option]

    if is_chrome_running():
        print("Chrome이 이미 디버깅 모드로 실행중입니다.")
        return 

    # 크롬 실행
    if headless:
        subprocess.Popen([
        chrome_path,
        f'--remote-debugging-port={port}',
        f'--user-data-dir={user_data_dir}',
        '--headless',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--window-size=1920,1080',
        '--force-device-scale-factor=1',
        '--high-dpi-support=1'])
    else:
        subprocess.Popen([chrome_path, '--remote-debugging-port={}'.format(port), f'--user-data-dir={user_data_dir}',  '--force-device-scale-factor=1', '--high-dpi-support=1'])

    time.sleep(1)

    return port



def setup_driver(port, headless=True):
    os.environ['WDM_SSL_VERIFY'] = '0'  # SSL 인증서 검증 비활성화
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")  # 헤드리스 모드 활성화
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")

    # chrome_options.add_argument("--start-fullscreen")  # 전체화면 모드로 실행
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")  # 포트 설정

    chrome_driver_path = r"C:\Users\jaehee\Downloads\automatic\chromedriver-win64\chromedriver.exe"
    service = Service(executable_path=chrome_driver_path)
    # service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=chrome_options)
