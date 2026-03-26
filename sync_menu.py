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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html = response.text
        
        # 1. 지저분한 이스케이프 문자(\")부터 깔끔하게 일반 따옴표(")로 정리
        cleaned_html = html.replace('\\"', '"').replace('\\\\', '\\')
        
        # 2. "menus":[ 시작점 찾기
        start_keyword = '"menus":['
        start_idx = cleaned_html.find(start_keyword)
        
        if start_idx == -1:
            # 띄어쓰기가 있을 경우를 대비해 한 번 더 체크
            start_keyword = '"menus": ['
            start_idx = cleaned_html.find(start_keyword)
            
        if start_idx == -1:
            return "❌ 메뉴 데이터를 찾을 수 없습니다. (사이트 구조 변경 가능성)"

        # 3. '[' 가 시작되는 정확한 위치부터 괄호 짝 맞추기 (정규식의 한계 극복!)
        array_start_idx = start_idx + len(start_keyword) - 1  # '[' 의 인덱스
        sub_str = cleaned_html[array_start_idx:]
        
        bracket_count = 0
        end_idx = 0
        
        for i, char in enumerate(sub_str):
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            
            # 대괄호가 열렸다가 완전히 다 닫히면(0) 그곳이 전체 JSON 배열의 끝!
            if bracket_count == 0 and i > 0:
                end_idx = i + 1
                break
        
        # 완벽하게 잘라낸 JSON 문자열
        json_str = sub_str[:end_idx]
        menus = json.loads(json_str) # 🎉 이제 파싱 에러 안 납니다!
        
        # 4. 오늘 날짜 메뉴 필터링
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_items = [m for m in menus if m.get('date') == today_str]
        
        if not daily_items:
            return f"📅 {today_str}일자 메뉴가 아직 등록되지 않았습니다."

        # 5. 슬랙 메시지 예쁘게 만들기
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
                food_list = [item['name'] for item in menu_data.get('items', [])]
                res_msg += f"{cat_name}\n> {', '.join(food_list)}\n\n"
            else:
                res_msg += f"{cat_name}\n> 오늘은 운영하지 않아요.\n\n"
        
        return res_msg

    except Exception as e:
        return f"❌ 메뉴 분석 실패: {str(e)}"

# 기존 send_to_slack 함수와 실행부는 그대로 유지
