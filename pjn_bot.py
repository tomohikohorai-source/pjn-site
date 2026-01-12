import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# Googleニュース経由（ペナンと教育関連）
RSS_URLS = [
    "https://news.google.com/rss/search?q=Penang+when:24h&hl=en-MY&gl=MY&ceid=MY:en",
    "https://news.google.com/rss/search?q=Malaysia+Education+when:24h&hl=en-MY&gl=MY&ceid=MY:en"
]

def ask_ai(title, summary, link):
    print(f"🤖 AI翻訳依頼中: {title[:40]}...")
    prompt = f"以下の英語ニュースをペナン在住日本人向けに翻訳・整形して。1行目は「ジャンル：〇〇」として（グルメ、重要、暮らし、おでかけ、教育、エンタメ、お得 のいずれか）。タイトル: {title}, 内容: {summary}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=30)
        if response.status_code == 200:
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            lines = content.strip().split('\n')
            genre = "暮らし"
            if "ジャンル：" in lines[0]:
                genre = lines[0].replace("ジャンル：", "").strip()
                body = "\n".join(lines[1:])
            else:
                body = content

            return f"""---
title: "{title}"
date: "{datetime.date.today()}"
category: "{genre}"
---
<div class="genre-label">ジャンル：{genre}</div>
<h3>【内容】</h3>

{body}

<a href="{link}" target="_blank" rel="noopener noreferrer" class="source-link">🔗 参照元記事を確認する</a>
"""
        else:
            print(f"   ⚠️ AIエラー (Code {response.status_code}): {response.text[:100]}")
            return None
    except Exception as e:
        print(f"   ⚠️ 通信エラー: {e}")
        return None

# --- メイン実行 ---
print(f"🚀 PJN Bot 始動")
count = 0

for url in RSS_URLS:
    if count >= 3: break
    print(f"📡 ニュース取得中: {url}")
    feed = feedparser.parse(url)
    
    # ニュースの冒頭5件だけを対象にする（API節約のため）
    for entry in feed.entries[:5]:
        if count >= 3: break
        
        # 安全なファイル名の作成
        safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
        filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
        
        if os.path.exists(filename): continue

        result = ask_ai(entry.title, entry.summary, entry.link)
        
        if result:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"   ✅ 保存成功: {filename}")
            count += 1
            print("   💤 成功したので60秒間休みます...")
            time.sleep(60)
        else:
            print("   💤 失敗したので30秒間休みます...")
            time.sleep(30)

print(f"🏁 完了。作成した記事数: {count}")
