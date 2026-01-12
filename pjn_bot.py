import os
import datetime
import feedparser
import requests
import json
import time

# --- 設定 ---
API_KEY = os.environ["GEMINI_API_KEY"]

POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

RSS_URLS = [
    "https://www.thestar.com.my/rss/news/nation",
    "https://www.thestar.com.my/rss/metro/community"
]

def get_working_model():
    """お使いのAPIキーで今使えるモデルを自動で探します"""
    # 試行するエンドポイントとモデルの組み合わせ
    options = [
        ("v1", "gemini-1.5-flash"),
        ("v1", "gemini-pro"),
        ("v1beta", "gemini-1.5-flash"),
        ("v1beta", "gemini-pro")
    ]
    
    for version, model_name in options:
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model_name}:generateContent?key={API_KEY}"
        test_payload = {"contents": [{"parts": [{"text": "Hi"}]}]}
        try:
            response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(test_payload))
            if response.status_code == 200:
                print(f"成功: モデル '{model_name}' (バージョン {version}) が使用可能です。")
                return url
        except:
            continue
    
    # すべて失敗した場合は現在のモデルリストをログに出してデバッグする
    print("利用可能なモデルが見つかりません。APIキーの設定を確認してください。")
    return None

def ask_ai(api_url, title, summary, link):
    print(f"AI翻訳中: {title}")
    
    prompt = f"""
    あなたはペナン在住日本人向けのニュース編集長です。
    以下の英語ニュースを、子育て世帯や母子留学生が読みやすい日本語に全文翻訳・整形してください。

    タイトル: {title}
    内容: {summary}

    【出力ルール】
    1. 冒頭に「ジャンル：〇〇」を明記
    2. タイトルは「【ジャンル】タイトル」の形式に。
    3. 本文は3-4行ごとに改行を入れ、読みやすく。
    4. 最後に「🔗 参照元記事を確認する」というリンクをつける。
    5. 出力は以下のMarkdown形式で。
    ---
    title: "{title}"
    date: "{datetime.date.today()}"
    category: "ニュース"
    ---
    <div class="genre-label">ジャンル：ニュース</div>
    <h3>【内容（全文翻訳）】</h3>
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
        data = response.json()
        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"翻訳エラー: {data}")
            return None
    except Exception as e:
        print(f"接続エラー: {e}")
        return None

# --- メイン処理 ---
print("システム起動...")
active_url = get_working_model()

if not active_url:
    print("【致命的エラー】利用可能なAIモデルが1つも見つかりませんでした。APIキーが正しくコピーされているか、Google AI Studioで新しいキーを作成し直すことをお勧めします。")
else:
    print("ニュース取得開始...")
    articles_count = 0
    for url in RSS_URLS:
        feed = feedparser.parse(url)
        print(f"ソース取得: {url} (記事数: {len(feed.entries)})")
        
        for entry in feed.entries[:5]: 
            if articles_count >= 10: break
            
            clean_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].strip().replace(" ", "_")
            filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{clean_title}.md")
            
            if os.path.exists(filename): continue

            article_md = ask_ai(active_url, entry.title, entry.summary, entry.link)
            
            if article_md:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(article_md)
                print(f"保存完了: {filename}")
                articles_count += 1
            time.sleep(1)

    print(f"本日の業務終了。作成記事数: {articles_count}")
