import requests
import os
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# GitHub Secrets에서 토큰을 가져옵니다.
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
# 채널 ID는 직접 입력하시거나, 이것도 Secret에 넣으셨다면 os.environ.get("CHANNEL_ID")로 바꾸세요.
CHANNEL_ID = "여기에_채널_ID_입력" 

def get_megabobs_menu():
    url = "https://www.megabobs.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # '코스 1', '코스 2', '테이크아웃' 텍스트가 포함된 섹션을 찾습니다.
        menu_items = []
        for keyword in ["코스 1", "코스 2", "테이크아웃"]:
            target = soup.find(string=lambda t: keyword in t)
            if target:
                content = target.parent.get_text(strip=True)
                menu_items.append(f"✅ *{keyword}*\n{content}")
            else:
                menu_items.append(f"❌ *{keyword}* 정보를 찾지 못했습니다.")
        
        return "\n\n".join(menu_items)
    except Exception as e:
        return f"데이터 추출 중 에러 발생: {e}"

def send_to_slack(message):
    if not SLACK_TOKEN:
        print("에러: SLACK_BOT_TOKEN이 설정되지 않았습니다.")
        return
        
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=f"📢 *오늘의 메뉴 동기화*\n\n{message}")
        print("슬랙 전송 성공!")
    except SlackApiError as e:
        print(f"슬랙 전송 실패: {e.response['error']}")

if __name__ == "__main__":
    menu_info = get_megabobs_menu()
    send_to_slack(menu_info)
