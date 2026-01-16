import os
import json
import time
import feedparser
import tweepy
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

# ===== X API =====
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET"),
)

# ===== 設定 =====
POSTED_FILE = "posted.json"
JST = timezone(timedelta(hours=9))
NOW = datetime.now(JST)
LIMIT_TIME = NOW - timedelta(days=1)  # 1日以内

# Google News RSS（日本）
RSS_URLS = [
    "https://news.google.com/rss/search?q=FRUITS+ZIPPER&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CANDY+TUNE&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CUTIE+STREET&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=KAWAII+LAB&hl=ja&gl=JP&ceid=JP:ja",
]

# ===== メンバー読み込み =====
with open("members.txt", "r", encoding="utf-8") as f:
    members = [m.strip().lower() for m in f if m.strip()]

print("🟩 メンバー名:", members)

# ===== 投稿履歴 =====
if os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        posted = json.load(f)
else:
    posted = {"links": [], "titles": []}

# ===== RSS 処理 =====
for rss_url in RSS_URLS:
    print("🔍 RSS取得:", rss_url)
    feed = feedparser.parse(rss_url)
    print("🟦 件数:", len(feed.entries))

    for entry in feed.entries:
        title = entry.title
        link = entry.link
        title_lower = title.lower()

        # 投稿日時チェック
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime.fromtimestamp(
                time.mktime(entry.published_parsed), JST
            )
            if published < LIMIT_TIME:
                continue
        else:
            continue  # 日付不明は除外

        print("チェック中:", title)

        # メンバー名マッチ
        if not any(name in title_lower for name in members):
            continue

        # 重複防止
        if link in posted["links"] or title in posted["titles"]:
            print("⏭ 既に投稿済み")
            continue

        text = f"{title}\n{link}"

        try:
            client.create_tweet(text=text)
            print("🚀 投稿成功:", title)

            posted["links"].append(link)
            posted["titles"].append(title)

            with open(POSTED_FILE, "w", encoding="utf-8") as f:
                json.dump(posted, f, ensure_ascii=False, indent=2)

        except tweepy.errors.Forbidden:
            print("⚠️ 重複ツイート（403）→ スキップ")

        except Exception as e:
            print("❌ 予期せぬエラー:", e)

print("✅ 実行完了")

# =========================
# テスト投稿（必要な時だけ）
# =========================


# ▼▼▼ テスト投稿用 ▼▼▼
test_mode = False   # ←投稿テストしたいときは True に

if test_mode:
    print("📝 テスト投稿を実行します...")
    client.create_tweet(text="【テスト】仲川瑠夏歌姫")
    print("✅ テスト投稿が完了しました！")
