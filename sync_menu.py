import requests
import os
import json
import re
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 1. 설정값 (본인의 채널 ID로 수정 필수!)
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = "C0ANHM7CKFV" 

def get_megabobs_menu():
    url = "https://www.megabobs.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        
        # [핵심] 복잡한 텍스트 속에서 메뉴 리스트만 찾아내는 정규식입니다.
        # 따옴표가 이스케이프(\") 처리된 부분까지 고려했습니다.
        match = re.search(r'\\"menus\\":\s*(\[.*?\])', html)
        if not match:
            # 두 번째 시도: 일반적인 JSON 형태 탐색
            match = re.search(r'"menus":\s*(\[.*?\])', html)

        if not match:
            return "❌ 메뉴 데이터를 찾을 수 없습니다. (사이트 구조 변경 가능성)"

        # 찾은 데이터를 파이썬 리스트로 변환 (이스케이프 제거 작업 포함)
        json_str = match.group(1).replace('\\"', '"').replace('\\\\', '\\')
        menus = json.loads(json_str)
        
        # 오늘 날짜 (2026-03-26)
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_items = [m for m in menus if m.get('date') == today_str]
        
        if not daily_items:
            return f"📅 {today_str}일자 메뉴가 아직 등록되지 않았습니다."

        # 슬랙 메시지 예쁘게 만들기
        res_msg = f"🍱 *{today_str} 메가존 구내식당 메뉴*\n"
        res_msg += "━━━━━━━━━━━━━━━━━━━━\n"
        
        category_map = {
            "COURSE_1": "🔵 *코스 1 (한식)*",
            "COURSE_2": "🔴 *코스 2 (일식/양식)*",
            "TAKE_OUT": "🛍️ *테이크아웃*"
        }

        for cat_key, cat_name in category_map.items():
            menu_data = next((m for m in daily_items if m['category'] == cat_key), None)
            if menu_data:
                # 메뉴 이름들 추출 (나주곰탕, 탄탄멘 등)
                food_list = [item['name'] for item in menu_data.get('items', [])]
                res_msg += f"{cat_name}\n> {', '.join(food_list)}\n\n"
            else:
                res_msg += f"{cat_name}\n> 오늘은 운영하지 않아요.\n\n"
        
        return res_msg

    except Exception as e:
        return f"❌ 메뉴 분석 실패: {str(e)}"

def send_to_slack(message):
    if not SLACK_TOKEN: return
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=message)
        print("슬랙 전송 성공!")
    except SlackApiError as e:
        print(f"슬랙 전송 실패: {e.response['error']}")

if __name__ == "__main__":
    menu_info = get_megabobs_menu()
    send_to_slack(menu_info)
