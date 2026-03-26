import requests
import os
import json
from datetime import datetime
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# 🚨 GitHub Actions Secret에 SLACK_BOT_TOKEN이 잘 들어있는지 꼭 확인하세요!
SLACK_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CHANNEL_ID = "C0ANHM7CKFV" 

def get_megabobs_menu():
    url = "https://www.megabobs.com/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        
        # 1. 지저분한 이스케이프 문자 정리
        cleaned_html = html.replace('\\"', '"').replace('\\\\', '\\')
        
        # 2. "menus":[ 시작점 찾기
        start_keyword = '"menus":['
        start_idx = cleaned_html.find(start_keyword)
        
        if start_idx == -1:
            start_keyword = '"menus": ['
            start_idx = cleaned_html.find(start_keyword)
            
        if start_idx == -1:
            return "❌ 메뉴 데이터를 찾을 수 없습니다."

        # 3. 확실한 파싱
        array_str = cleaned_html[start_idx + len(start_keyword) - 1:]
        menus = None
        
        for i in range(len(array_str), 0, -1):
            if array_str[i-1] == ']':
                try:
                    menus = json.loads(array_str[:i])
                    break 
                except json.JSONDecodeError:
                    continue
                    
        if not menus:
            return "❌ JSON 메뉴 데이터를 파싱하는 데 실패했습니다."

        # 4. 오늘 날짜 메뉴 필터링
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_items = [m for m in menus if m.get('date') == today_str]
        
        if not daily_items:
            return "📅 " + today_str + "일자 메뉴가 아직 등록되지 않았습니다."

        # 5. 슬랙 메시지 만들기 (문자열 깨짐 방지 처리)
        res_msg = "🍱 *" + today_str + " 메가존 구내식당 메뉴*\n"
        res_msg += "━━━━━━━━━━━━━━━━━━━━\n"
        
        category_map = {
            "COURSE_1": "🔵 *코스 1 (한식)*",
            "COURSE_2": "🔴 *코스 2 (일식/양식)*",
            "TAKE_OUT": "🛍️ *테이크아웃*"
        }

        for cat_key, cat_name in category_map.items():
            menu_data = next((m for m in daily_items if m['category'] == cat_key), None)
            if menu_data:
                items = menu_data.get('items', [])
                total_kcal = sum(item.get('kcal', 0) for item in items)
                
                food_list = [f"{item['name']} ({item.get('kcal', 0)}kcal)" for item in items]
                
                # ⭐️ 테이크아웃은 총 칼로리 제외 로직 추가!
                if cat_key == "TAKE_OUT":
                    res_msg += f"{cat_name}\n> {', '.join(food_list)}\n\n"
                else:
                    res_msg += f"{cat_name} - 총 {total_kcal}kcal\n> {', '.join(food_list)}\n\n"
            else:
                res_msg += f"{cat_name}\n> 오늘은 운영하지 않아요.\n\n"
        
        return res_msg

    except Exception as e:
        return "❌ 메뉴 분석 중 알 수 없는 에러 발생
