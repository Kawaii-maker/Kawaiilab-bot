import os
import feedparser
import tweepy
from dotenv import load_dotenv

load_dotenv()

# X API 認証
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

RSS_URL = "https://news.yahoo.co.jp/rss/topics/entertainment.xml"

# メンバー読み込み
with open("members.txt", "r", encoding="utf-8") as f:
    members = [m.strip().lower() for m in f if m.strip()]

print("🟩 メンバー名（lower）:", members)

# 投稿済み記録
POSTED_FILE = "posted.txt"
if not os.path.exists(POSTED_FILE):
    open(POSTED_FILE, "w", encoding="utf-8").close()

with open(POSTED_FILE, "r", encoding="utf-8") as f:
    posted_links = set(f.read().splitlines())

# RSS取得
feed = feedparser.parse(RSS_URL)

print("🟦 RSS取得件数:", len(feed.entries))
for e in feed.entries[:10]:
    print("・", e.title)

# チェック開始
for entry in feed.entries:
    title = entry.title
    link = entry.link
    title_lower = title.lower()

    print("チェック中:", title)

    if any(name in title_lower for name in members):
        print("⭐ マッチした！:", title)

        if link not in posted_links:
            print("👉 新規投稿:", title)
            break

# ▼▼▼ テスト投稿用 ▼▼▼
test_mode = False   # ←投稿テストしたいときは True に

if test_mode:
    print("📝 テスト投稿を実行します...")
    client.create_tweet(text="【テスト】仲川瑠夏歌姫")
    print("✅ テスト投稿が完了しました！")
