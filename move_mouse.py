# 디스플레이 끄기 방지
import pyautogui
import time
import random
import threading
import asyncio
from datetime import datetime


async def move_mouse():
    pyautogui.FAILSAFE = False
    while True:
        screenW, screenH = pyautogui.size()
        temp_x, temp_y = pyautogui.position()
        
        # 4분 대기
        time.sleep(240)
        
        current_x, current_y = pyautogui.position()
        
        # 마우스가 움직이지 않았다면 랜덤 위치로 이동
        if temp_x == current_x and temp_y == current_y:
            ran_w = random.randint(1, screenW - 1)  # 화면 너비 내에서 랜덤
            ran_h = random.randint(1, screenH - 1)  # 화면 높이 내에서 랜덤

            pyautogui.moveTo(ran_w, ran_h, 0.3)
            # print("마우스 움직이기 " + datetime.now().strftime("%H:%M"))

            # 키보드 입력 (예: 스페이스바를 누름)
            pyautogui.typewrite(" ", 1)  # 공백 입력
            # pyautogui.press('space')
            print("마우스 움직이기, 스페이스바 입력 " + datetime.now().strftime("%H:%M"))


async def main():
    await move_mouse()


if __name__ == "__main__":
    asyncio.run(main())