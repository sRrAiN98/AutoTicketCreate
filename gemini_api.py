import base64
import os
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class ImageAnalyzer:
    def __init__(self, api_key, model):
        self.llm = ChatGoogleGenerativeAI(google_api_key=api_key, model=model, temperature=0)
        self.output_file = "analysis_results.txt"  # 결과를 저장할 파일 경로

    def analyze_image(self, image_path, message_info):
        try:
            # 로컬 이미지 파일을 읽어 Base64로 인코딩
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")

            # message_info에서 필요한 정보 추출
            project_name = message_info.get("프로젝트 이름", "")
            server_name = message_info.get("서버 이름", "")
            event_message = message_info.get("이벤트 메시지", "")
            event_start = message_info.get("이벤트 시작 시간", "")
            
            # 미리 채워놓을 텍스트 생성
            prefilled_text = (
                f"고객사 | {project_name}\n"
                f"서버 이름 | {server_name}\n"
                f"알람 발생 시간 | {event_start}\n"
                f"알람 내용 | {event_message}\n"
            )

            # HumanMessage 생성
            message = HumanMessage(
                content=[
                    {"type": "text", "text": f"당신은 서버 모니터링 담당자로서 고객에게 알람 발생 원인과 그에 따른 조치 방법을 안내하는 AI 어시스턴트입니다. 고객이 직접 조치를 취할 수 있도록 구체적인 단계를 제시하며, 제공된 스크린샷과 이벤트 정보를 분석하여 문제를 파악합니다. 명확하고 간결한 언어로 설명하며, 설득력 있는 문구를 사용하여 고객이 이해하기 쉽도록 작성합니다. 어떤 프로세스가 문제인지 구체적으로 알려줍니다. 10줄 이내로 대답하며, 시스템 업그레이드와 같이 실질적으로 조치하기 어려운 언급은 피합니다.  참고할 수 있는 이벤트 정보: {event_message}, 프로세스에 대해서 말을 할거면 해당 프로세스는 어떤 프로그램인지도 설명해줘 시작 소개는 내가 적을테니 원인, 결과, 해결법을 알려줘야해 해결 방법은 큰 문제가 생기지 않도록 책임 소재가 적은 방법으로 말해줘"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ]
            )

            # AI 모델에 메시지 전송
            ai_msg = self.llm.invoke([message])

            # 결과를 텍스트 파일에 추가
            with open(self.output_file, "a", encoding="utf-8") as file:
                file.write(ai_msg.content + "\n")  # 각 결과를 새 줄에 추가

            final_response = prefilled_text + "\n AI의 응답: " + ai_msg.content

            return final_response
        except Exception as e:
            return f"이미지 처리 중 오류 발생: {str(e)}"


if __name__ == "__main__":
    API_KEY = ""  # 본인의 Google API 키 입력
    MODEL="gemini-1.5-flash"
    # MODEL="gemini-1.5-pro"
    image_path = "monitoring_screenshot.png"  # 로컬 이미지 파일 경로 입력
    
    analyzer = ImageAnalyzer(API_KEY, MODEL)
    message_info = {
    "알림 레벨": "Critical",
    "프로젝트 번호": "12345",
    "프로젝트 이름": "프로젝트1",
    "서버 이름": "server1",
    "이벤트 메시지": "Memory Used > 90 %",
    "이벤트 시작 시간": "2024-08-29 18:51:40 +0900"
    }


    result = analyzer.analyze_image(image_path, message_info)
    print(result)
