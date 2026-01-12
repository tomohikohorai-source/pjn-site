import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# あなたのリストにあった、最も軽量な「2.0-flash-lite」を使用します
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

RSS_URLS = ["https://www.thestar.com.my/rss/news/nation"]

def ask_ai(title, summary, link):
    print(f"AI翻訳中: {title}")
    
    prompt = f"以下の英語ニュースを日本人向けに日本語で全文翻訳して。タイトル: {title}, 内容: {summary}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    # 429エラーが出た場合に3回までやり直す機能
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            
            if response.status_code == 200:
                data = response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                return f"""---
title: "{title}"
date: "{datetime.date.today()}"
category: "ニュース"
---
<div class="genre-label">ジャンル：ニュース</div>
<h3>【内容（全文翻訳）】</h3>

{content}

<a href="{link}" class="source-link">🔗 参照元記事を確認する</a>
"""
            elif response.status_code == 429:
                print(f"⚠️ 制限中... 60秒待機して再試行します ({attempt + 1}/3)")
                time.sleep(60) # 429が出たら1分休む
            else:
                print(f"❌ APIエラー: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 接続エラー: {e}")
            return None
    return None

# --- メイン実行 ---
print(f"PJN Bot 起動 (モデル: {MODEL_NAME})")

feed = feedparser.parse(RSS_URLS[0])
count = 0

for entry in feed.entries[:3]: # 確実に成功させるため、まずは3件
    safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
    filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
    
    if os.path.exists(filename): continue

    result = ask_ai(entry.title, entry.summary, entry.link)
    if result:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"✅ 保存完了: {filename}")
        count += 1
        print("次の記事まで 60秒 休憩します...") # 無料枠を労わる
        time.sleep(60)

print(f"本日の業務終了。作成記事数: {count}")
