import requests
import os
import json
from datetime import datetime, timedelta
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 🚨 대화형 봇은 2개의 토큰이 필요합니다!
SLACK_BOT_TOKEN = os.environ.get("xoxb-7969192954980-10772129863138-gNByWPS3GTXuz4zbBcvGOFkA") # xoxb- 로 시작하는 토큰
SLACK_APP_TOKEN = os.environ.get("xapp-1-A0ANTLSMBJ8-10766228424231-37847f5b0606d7118a5b1a1d2b1971c5a400b1d2fd5110b2b69397e2cf945d8e") # xapp- 으로 시작하는 토큰 (Socket Mode용)

app = App(token=SLACK_BOT_TOKEN)

# ⭐️ 날짜를 입력받아 해당 날짜의 메뉴를 가져오도록 함수를 업그레이드했습니다!
def get_megabobs_menu(target_date_str):
    url = "https://www.megabobs.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
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

        # ⭐️ 입력받은 타겟 날짜(target_date_str)로 필터링합니다.
        daily_items = [m for m in menus if m.get('date') == target_date_str]
        
        if not daily_items:
            return f"📅 {target_date_str} 메뉴가 없습니다."

        msg_lines = [f"🍱 *{target_date_str} 구내식당 메뉴*", "━━━━━━━━━━━━━━"]
        
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

# 💬 "오늘 메뉴 알려줘" 채팅 감지
@app.message("오늘 메뉴 알려줘")
def handle_today_menu(message, say):
    say("잠시만요! 오늘 메뉴를 가져오는 중입니다... 🏃‍♂️💨")
    today_str = datetime.now().strftime("%Y-%m-%d")
    menu_info = get_megabobs_menu(today_str)
    say(menu_info)

# 💬 "내일 메뉴 알려줘" 채팅 감지
@app.message("내일 메뉴 알려줘")
def handle_tomorrow_menu(message, say):
    say("잠시만요! 내일 메뉴를 가져오는 중입니다... 🏃‍♂️💨")
    # ⭐️ timedelta(days=1)을 더해서 내일 날짜를 구합니다!
    tomorrow_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    menu_info = get_megabobs_menu(tomorrow_str)
    say(menu_info)

if __name__ == "__main__":
    print("⚡️ 슬랙 봇이 24시간 대기를 시작합니다...")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
