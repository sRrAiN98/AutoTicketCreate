import requests

def get_projects(api_token):
    url = "https://api.whatap.io/open/api/json/projects"
    headers = {
        "x-whatap-token": api_token
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # 요청이 실패하면 예외 발생
        data = response.json()  # JSON 형식으로 응답 변환
        return data['data']  # 'data' 필드 반환
    except requests.exceptions.RequestException as e:
        print(f"API 요청 중 오류 발생: {e}")
        return None

# 자신의 와탭 API 토큰 입력
API_TOKEN = ""

# 프로젝트 목록 조회
projects = get_projects(API_TOKEN)

# 프로젝트 데이터를 파일로 저장
if projects:
    with open('projects_data.py', 'w', encoding='utf-8') as f:
        f.write("# projects_data.py\n\n")
        f.write("projects = {\n")
        for project in projects:
            project_name = project['projectName']
            project_code = project['projectCode']
            f.write(f'    "{project_name}": "{project_code}",\n')
        f.write("}\n")
