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
        
        cleaned_html = html.replace('\\"', '"').replace('\\\\', '\\')
        
        start_keyword = '"menus":['
        start_idx = cleaned_html.find(start_keyword)
        
        if start_idx == -1:
            start_keyword = '"menus": ['
            start_idx = cleaned_html.find(start_keyword)
            
        if start_idx == -1:
            return "❌ 메뉴 데이터를 찾을 수 없습니다."

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

        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_items = [m for m in menus if m.get('date') == today_str]
        
        if not daily_items:
            return f"📅 {today_str}일자 메뉴가 아직 등록되지 않았습니다."

        res_msg = f"🍱 *{today_str} 메가존
