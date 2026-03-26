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

        # 3. 확실한 파싱 (뒤에서부터 ']'를 찾아가며 에러 안 날 때까지 파싱 시도)
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
            return f"📅 {today_str}일자 메뉴가 아직 등록
