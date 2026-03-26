import requests
import os
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 설정값
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = "C0ANHM7CKFV" # 본인의 채널 ID로 유지하세요

def get_megabobs_menu():
    url = "https://www.megabobs.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8' # 한글 깨짐 방지
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # 찾고자 하는 키워드 리스트
        keywords = ["코스 1", "코스 2", "테이크아웃"]
        
        # 사이트 내의 모든 텍스트 요소를 검사
        all_elements = soup.find_all(['div', 'p', 'span', 'h3', 'h4'])
        
        for key in keywords:
            found_text = ""
            for el in all_elements:
                if key in el.get_text():
                    # 해당 키워드가 포함된 요소의 다음 형제 요소나 부모의 텍스트를 가져옴
                    # 보통 메뉴 이름 바로 아래에 상세 메뉴가 적혀 있기 때문입니다.
                    content = el.parent.get_text(separator="\n", strip=True)
                    if len(content) > len(key) + 5: # 단순히 이름만 있는 게 아니라 내용이 있는 경우
                        found_text = content
                        break
            
            if found_text:
                results.append(f"✅ *{found_text}*")
            else:
                results.append(f"❌ *{key}* 정보를 찾지 못했습니다.")
        
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"데이터 추출 중 에러 발생: {e}"

def send_to_slack(message):
    if not SLACK_TOKEN:
        print("에러: SLACK_BOT_TOKEN이 설정되지 않았습니다.")
        return
        
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=f"📢 *오늘의 메가밥스 메뉴 동기화*\n\n{message}")
        print("슬랙 전송 성공!")
    except SlackApiError as e:
        print(f"슬랙 전송 실패: {e.response['error']}")

if __name__ == "__main__":
    menu_info = get_megabobs_menu()
    send_to_slack(menu_info)
