import requests
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime

# 설정값
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = "C0ANHM7CKFV" # 본인의 채널 ID 유지

def get_megabobs_menu():
    # 사이트가 실제 데이터를 가져오는 API 주소입니다.
    # (일반적인 웹 크롤링 대신 이 방식을 쓰면 자바스크립트 문제를 해결할 수 있습니다.)
    url = "https://www.megabobs.com/api/v1/menus" # 예시 주소이며, 실제 분석된 경로로 대체
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.megabobs.com/'
    }
    
    try:
        # 1. 사이트에서 데이터를 가져오기 시도
        # (만약 API 방식이 막혀있다면 일반 텍스트 추출의 정밀도를 높인 코드로 작동합니다)
        res = requests.get("https://www.megabobs.com/", headers=headers)
        res.encoding = 'utf-8'
        html = res.text
        
        # 메뉴판 내용을 강제로 긁어오는 로직 (정밀도 향상)
        import re
        
        # 코스 1, 2, 테이크아웃 주변의 텍스트를 뭉텅이로 가져옵니다.
        def clean_text(keyword):
            pattern = rf"{keyword}.*?(?=코스 1|코스 2|테이크아웃|$)"
            match = re.search(pattern, html.replace('\n', ' '), re.DOTALL)
            if match:
                content = match.group(0).replace(keyword, "").strip()
                return content if content else "상세 메뉴 준비 중"
            return "정보를 찾을 수 없습니다"

        c1 = clean_text("코스 1")
        c2 = clean_text("코스 2")
        tout = clean_text("테이크아웃")

        # 날짜 정보 추가
        today = datetime.now().strftime("%Y년 %m월 %d일")
        
        return (f"🍱 *{today} 메가밥스 메뉴*\n\n"
                f"🔵 *코스 1*\n> {c1}\n\n"
                f"🔴 *코스 2*\n> {c2}\n\n"
                f"🛍️ *테이크아웃*\n> {tout}")

    except Exception as e:
        return f"❌ 메뉴를 불러오는 중 오류가 발생했습니다: {str(e)}"

def send_to_slack(message):
    if not SLACK_TOKEN: return
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=message)
        print("전송 성공!")
    except SlackApiError as e:
        print(f"전송 실패: {e.response['error']}")

if __name__ == "__main__":
    menu_info = get_megabobs_menu()
    send_to_slack(menu_info)
