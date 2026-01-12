import os
import feedparser
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# =========================
# 初期設定
# =========================
load_dotenv()

client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# Google News RSS（専門メディア統合）
RSS_URLS = [
    "https://news.google.com/rss/search?q=FRUITS+ZIPPER&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CANDY+TUNE&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CUTIE+STREET&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=KAWAII+LAB&hl=ja&gl=JP&ceid=JP:ja",
]

# 1回の実行で投稿する最大数
MAX_POSTS_PER_RUN = 10

# =========================
# メンバー読み込み
# =========================
with open("members.txt", "r", encoding="utf-8") as f:
    members = [m.strip().lower() for m in f if m.strip()]

print("🟩 メンバー名:", members)

# =========================
# 投稿済み管理
# =========================
POSTED_FILE = "posted.txt"

if not os.path.exists(POSTED_FILE):
    open(POSTED_FILE, "w", encoding="utf-8").close()

with open(POSTED_FILE, "r", encoding="utf-8") as f:
    posted_links = set(f.read().splitlines())

# =========================
# RSSチェック & 投稿
# =========================
posted_count = 0

for rss_url in RSS_URLS:
    print("🔍 RSS取得:", rss_url)
    feed = feedparser.parse(rss_url)
    print("🟦 件数:", len(feed.entries))

    for entry in feed.entries:
        if posted_count >= MAX_POSTS_PER_RUN:
            print("⛔ 投稿上限に達しました")
            break

        title = entry.title
        link = entry.link
        title_lower = title.lower()

        print("チェック中:", title)

        # メンバー or グループ名判定
        if not any(name in title_lower for name in members):
            continue

        # 重複防止
        if link in posted_links:
            print("⏭ 既投稿スキップ")
            continue

        # 新しさ判定（30分以内）
        published = entry.get("published_parsed")
        if not published:
            print("⏭ 時刻なしスキップ")
            continue

        published_time = datetime(*published[:6], tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - published_time > timedelta(minutes=15):
            print("⏭ 古い記事スキップ")
            continue

        # 投稿文
        tweet_text = (
            f"📰 KAWAII LAB. ニュース\n\n"
            f"{title}\n"
            f"{link}"
        )

        try:
            client.create_tweet(text=tweet_text)
            print("✅ 投稿成功:", title)

            with open(POSTED_FILE, "a", encoding="utf-8") as f:
                f.write(link + "\n")

            posted_links.add(link)
            posted_count += 1

        except Exception as e:
            print("❌ 投稿失敗:", e)

print("🎉 実行完了")
print("📝 投稿数:", posted_count)
print("⏰ 実行時刻:", datetime.now())

# =========================
# テスト投稿（必要な時だけ）
# =========================


# ▼▼▼ テスト投稿用 ▼▼▼
test_mode = False   # ←投稿テストしたいときは True に

if test_mode:
    print("📝 テスト投稿を実行します...")
    client.create_tweet(text="【テスト】仲川瑠夏歌姫")
    print("✅ テスト投稿が完了しました！")
