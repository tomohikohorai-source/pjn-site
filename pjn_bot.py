import os, datetime, feedparser, requests, json, time

API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
MODEL_NAME = "gemini-2.0-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={API_KEY}"
POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

def ask_ai(title, summary, link):
    prompt = f"Translate to Japanese: {title}\n\n{summary}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        # 1日の上限に達しているか確認
        response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, data=json.dumps(payload), timeout=10)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"   ⚠️ AI制限中 (Status: {response.status_code})")
            return None
    except:
        return None

print("🚀 PJN 緊急モード始動")
feed = feedparser.parse("https://news.google.com/rss/search?q=Penang+when:24h&hl=en-MY&gl=MY&ceid=MY:en")
count = 0

for entry in feed.entries[:3]:
    safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
    filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
    if os.path.exists(filename): continue

    translated = ask_ai(entry.title, entry.summary, entry.link)
    
    # 【重要】AIが制限されていても、ニュースを英語のまま投稿してサイトを更新する！
    content = translated if translated else f"（AI翻訳制限中のため原文を表示）\n\n{entry.summary}"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"---\ntitle: \"{entry.title}\"\ndate: \"{datetime.date.today()}\"\ncategory: \"重要\"\n---\n{content}\n\n<a href='{entry.link}' target='_blank' class='source-link'>🔗 原文記事を確認</a>")
    
    print(f"✅ 保存完了: {filename}")
    count += 1
    time.sleep(10) # 429回避のため短めに待機

print(f"完了。作成記事数: {count}")
