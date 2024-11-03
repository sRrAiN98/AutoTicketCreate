# 자동화 티켓 발행 시스템
공인 IP 부재로 인해 웹훅 수신이 불가능한 환경에서, 대안으로 Slack Web UI를 직접 크롤링하는 방식을 구현하여 웹훅 기능을 대체하였습니다.

## 초기 설정 방법
1. 크롬 드라이버 다운로드, **chrome_path**에 경로 설정
2. chrome_init.ipynb에서 유저 데이터 폴더 생성 및 크롬 실행
3. 필요한 사이트들 로그인 진행
4. 유저 데이터 2개 복사 후 이름 변경
5. **user_data_dirs**에 경로 설정

## 주요 파일 설명
- whatab.py: Whatab API를 통해 projects_data.py의 프로젝트 정보 추출
- contacts.py: 프로젝트별 담당자 메일 수동 맵핑
- slack_monitoring.py: 슬랙 알람 모니터링
- whatab_screenshot.py: Whatab 스크린샷 자동화
- gemini_api.py: LLM 프롬프트 처리
- ticket_automation_gpt.py: 티켓 발행 자동화
- ticket_automation_gpt_email.py: 이메일 발행 자동화

## 크롬 실행 설정
일반 실행:
```python
port = start_chrome(2)
driver = setup_driver(port)
```
# 화면 표시 실행
```python
port = start_chrome(3, headless=False)
driver = setup_driver(port, headless=False)
```
# 작동 프로세스

## 1. 윈도우 잠금 방지
- 마우스 1픽셀 움직임
- 스페이스바 입력

## 2. 슬랙 알람 모니터링
- Critical 알람 발생 시 프로젝트/서버 정보 파싱
- 형식: [Critical][INFRA][프로젝트][서버 이름][CPU Used > 90 %]

## 3. Whatab 스크린샷
- 프로젝트 ID 기반 URL 접속
- 서버별 화면 캡처

## 4. LLM 분석
- 스크린샷 기반 장애 원인 분석
- 조치방법 작성

## 5. 티켓/이메일 발행
- 담당자 정보 입력
- 분석 내용 및 스크린샷 첨부
- 발행 완료 후 슬랙 알림

# 참고사항
- 현재 각 파일별로 ID/PW/API 키 개별 입력 필요
- 추후 단일 실행파일에서 입력하도록 개선 예정
- ticket_automation_gpt_email.py는 XPath 사용로 최대한 변경이 일어나도 동작하도록 안정화      
   
   
# ***** 초기 버전의 설명 ***** 
아직 코드의 변수 최적화를 하지 않아서    
각 파일마다 id, password, api키를 입력해야함   
추후 첫 하나의 실행파일에서 입력하도록 변경 예정  

초기 설정 방법 
1. 크롬 드라이버 다운로드, **chrome_path**에 경로 설정
2. chrome_init.ipynb에서 유저 데이터 폴더를 하나만 생성, 크롬을 실행
3. 실행된 크롬으로 필요한 사이트들 로그인 진행
4. 유저 데이터를 2개 복사하여 이름 변경
5. **user_data_dirs**에 경로 설정


whatab.py파일에 Whatab API로 projects_data.py 파일의 프로젝트 이름 : 프로젝트 번호 변수 추출   
contacts.py에 프로젝트 이름: 담당자 메일 수동 맵핑   

크롬이 실제로 동작하는 걸 보기 위해선    
    port = start_chrome(2)   
    driver = setup_driver(port) 크롬 실행 코드를 변경한다.    

    port = start_chrome(3, headless=False) haedless 추가   
    driverk = setup_driver(port, headless=False)


0. 윈도우 잠금 방지   
0.1 마우스 1픽셀 움직이기, 스페이스바 입력   

                            1. 와탭에서 웹훅으로 알람 발생(IP가 없어서 웹훅을 받지 못해서 폐기)      
                            [Critical][INFRA][프로젝트 이름][서버 이름][CPU Used > 90 %]
                            1.1 Critical 일 시
                            1.2 3번째 칸(프로젝트 이름)을 기준으로 projects_data.py 에서  projects 변수에 선언되어 있는 키 밸류값을 기준으로 밸류를 가져옴
                            2.2 4번쨰 칸(서버 이름)에 있는 서버 명을 변수로 저장

1. 웹 슬랙 페이지에서 알람 발생, 발생한 알람을 지속적 파싱            slack_monitoring.py   
[Critical][INFRA][프로젝트][서버 이름][CPU Used > 90 %]   
1.1 Critical 일 시   
1.2 3번째 칸(프로젝트 이름)을 기준으로 projects_data.py 에서  projects 변수에 선언되어 있는 키 밸류값을 기준으로 밸류를 가져옴   
2.2 4번쨰 칸(서버 이름)에 있는 서버 명을 변수로 저장   


2. Whatab 스크린샷                      whatab_screenshot.py   
2.1 "프로젝트": "12345" 를 기준으로 와탭 url에 접속   
2.2 target_url = "https://service.whatap.io/v2/project/sms/{54321}/server/list"  {} 사이를 변수로 변경   
2.3 셀레미움으로 4번쨰 칸에 있는 서버 변수명으로 click 발생   
2.4 해당 화면 스크린샷 파일 저장   

3. LLM 프롬프트                          gemini_api.py   
3.1스크린샷을 LLM에게 전달   
3.2 프롬프트를 기반으로 장애 발생 기준(원인), 간단한 조치방법 작성   

- GPT에게 API로 리턴값 사용

4. 프레시데스크 (셀레미움)                ticket_automation_gpt.py  , ticket_automation_gpt_email.py   
4.1 로그인 진행   
4.2 티켓 페이지 접속   
4.3 와탭 3번 칸 기준으로 미리 만들어둔 담당자 기입   
4.4 내용란에 프롬프트 리턴값, 스크린샷 기입   
4.5 티켓 발행, 슬랙에 티켓 발송 알람 발생(담당자 확인용)   
   


ticket_automation_gpt.py,  ticket_automation_gpt_email.py 차이는   
티켓발행과 이메일 발행 차이,   
각 페이지마다 XPath 명이 다름 (유동적인 XPath 값도 존재)   
ticket_automation_gpt에서 css.selector로 진행하다가    
ticket_automation_gpt_email 에서는 Xpath로 변경 (실행시 더 안정적이였음)   
