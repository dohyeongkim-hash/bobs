import requests
import os
import json
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = "C0ANHM7CKFV" 

def get_megabobs_menu():
    url = "https://www.megabobs.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        
        cleaned = html.replace('\\"', '"').replace('\\\\', '\\')
        
        start_idx = cleaned.find('"menus":[')
        if start_idx == -1:
            start_idx = cleaned.find('"menus": [')
            
        if start_idx == -1:
            return "❌ 메뉴를 찾을 수 없습니다."

        array_str = cleaned[start_idx + 8:]
        menus = None
        
        for i in range(len(array_str), 0, -1):
            if array_str[i-1] == ']':
                try:
                    menus = json.loads(array_str[:i])
                    break 
                except json.JSONDecodeError:
                    continue
                    
        if not menus:
            return "❌ JSON 파싱 실패."

        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_items = [m for m in menus if m.get('date') == today_str]
        
        if not daily_items:
            return f"📅 {today_str} 메뉴가 없습니다."

        # 슬랙 메시지 만들기 (문자열 끊김 방지)
        msg_lines = [f"🍱 *{today_str} 구내식당 메뉴*", "━━━━━━━━━━━━━━"]
        
        cat_map = {
            "COURSE_1": "🔵 *코스 1 (한식)*",
            "COURSE_2": "🔴 *코스 2 (양식/일식)*",
            "TAKE_OUT": "🛍️ *테이크아웃*"
        }

        for cat_key, cat_name in cat_map.items():
            menu_data = next((m for m in daily_items if m['category'] == cat_key), None)
            if menu_data:
                items = menu_data.get('items', [])
                total_kcal = sum(item.get('kcal', 0) for item in items)
                food_list = [f"{item['name']} ({item.get('kcal', 0)}kcal)" for item in items]
                
                if cat_key == "TAKE_OUT":
                    msg_lines.append(f"{cat_name}\n> {', '.join(food_list)}\n")
                else:
                    msg_lines.append(f"{cat_name} - 총 {total_kcal}kcal\n> {', '.join(food_list)}\n")
            else:
                msg_lines.append(f"{cat_name}\n> 운영하지 않아요.\n")
        
        return "\n".join(msg_lines)

    except Exception as e:
        return f"❌ 에러 발생: {e}"

def send_to_slack(message):
    if not SLACK_TOKEN: 
        print("🚨 토큰이 없습니다!")
        return
        
    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=message)
        print("✅ 슬랙 전송 성공!")
    except SlackApiError as e:
        print(f"🚨 슬랙 에러: {e.response['error']}")

if __name__ == "__main__":
    menu_info = get_megabobs_menu()
    send_to_slack(menu_info)
