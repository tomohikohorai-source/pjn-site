import os
import datetime
import feedparser
import google.generativeai as genai

# --- 設定 ---
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 保存先フォルダの作成（これがないと保存に失敗します）
POSTS_DIR = "src/pages/posts"
os.makedirs(POSTS_DIR, exist_ok=True)

# ニュースソース（複数のソースを試すように改良）
RSS_URLS = [
    "https://www.thestar.com.my/rss/metro/community",
    "https://www.thestar.com.my/rss/news/nation"
]

def ask_ai(title, summary, link):
    print(f"AI翻訳中: {title}")
    prompt = f"""
    あなたはペナン在住日本人向けのニュース編集長です。
    以下の英語ニュースを、子育て世帯や母子留学生が読みやすい日本語に全文翻訳・整形してください。

    【ニュース内容】
    タイトル: {title}
    内容: {summary}

    【出力ルール】
    1. 冒頭に「ジャンル：〇〇」を明記（教育、生活、交通など）
    2. 本文は3-4行ごとに改行を入れ、読みやすく。
    3. 最後に「🔗 参照元記事を確認する」というリンクをつける。
    4. 出力は以下のMarkdown形式の「中身」だけを出力してください。
    ---
    title: "{title}"
    date: "{datetime.date.today()}"
    category: "ニュース"
    ---
    <div class="genre-label">ジャンル：ニュース</div>
    <h3>【内容（全文翻訳）】</h3>
    (本文をここに)

    <a href="{link}" class="source-link">🔗 参照元記事を確認する</a>
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"AIエラー: {e}")
        return None

# --- メイン処理 ---
print("ニュース取得開始...")
articles_count = 0

for url in RSS_URLS:
    feed = feedparser.parse(url)
    print(f"ソース取得中: {url} (記事数: {len(feed.entries)})")
    
    for entry in feed.entries[:5]: # 各ソースから最大5件
        if articles_count >= 10: break
        
        # ファイル名の作成（記号などを除去）
        safe_title = "".join([c for c in entry.title if c.isalnum() or c==' '])[:30].replace(" ", "_")
        filename = os.path.join(POSTS_DIR, f"{datetime.date.today()}-{safe_title}.md")
        
        # すでにファイルがある場合はスキップ
        if os.path.exists(filename):
            continue

        article_md = ask_ai(entry.title, entry.summary, entry.link)
        
        if article_md:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(article_md)
            print(f"保存完了: {filename}")
            articles_count += 1

print(f"本日の業務終了。作成した記事数: {articles_count}")
