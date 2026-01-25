import os
import feedparser
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv()

# ======================
# X API 認証
# ======================
client = tweepy.Client(
    consumer_key=os.getenv("API_KEY"),
    consumer_secret=os.getenv("API_SECRET"),
    access_token=os.getenv("ACCESS_TOKEN"),
    access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
)

# ======================
# Google News RSS
# ======================
RSS_URLS = [
    "https://news.google.com/rss/search?q=FRUITS+ZIPPER&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CANDY+TUNE&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CUTIE+STREET&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=KAWAII+LAB&hl=ja&gl=JP&ceid=JP:ja",
]

# ======================
# メンバー読み込み
# ======================
with open("members.txt", "r", encoding="utf-8") as f:
    members = [m.strip().lower() for m in f if m.strip()]

print("🟩 メンバー名:", members)

# ======================
# 投稿済み管理
# ======================
POSTED_FILE = "posted.txt"
if not os.path.exists(POSTED_FILE):
    open(POSTED_FILE, "w", encoding="utf-8").close()

with open(POSTED_FILE, "r", encoding="utf-8") as f:
    posted_links = set(f.read().splitlines())

# ======================
# 時間条件（24時間以内）
# ======================
now = datetime.now(timezone.utc)
limit_time = now - timedelta(hours=24)

posted_count = 0
MAX_POSTS = 3  # 1回の実行で最大投稿数（凍結対策）

# ======================
# RSSチェック開始
# ======================
for rss_url in RSS_URLS:
    if posted_count >= MAX_POSTS:
        break

    print("🔍 RSS取得:", rss_url)
    feed = feedparser.parse(rss_url)
    print("🟦 件数:", len(feed.entries))

    for entry in feed.entries:
        if posted_count >= MAX_POSTS:
            break

        title = entry.title
        link = entry.link
        title_lower = title.lower()

        # 公開時間チェック
        if not hasattr(entry, "published_parsed"):
            continue

        published = datetime(
            *entry.published_parsed[:6],
            tzinfo=timezone.utc
        )

        if published < limit_time:
            continue

        # メンバー or グループ名マッチ
        matched = [name for name in members if name in title_lower]
        if not matched:
            continue

        # 重複投稿防止
        if link in posted_links:
            continue

        related = " / ".join([m.upper() for m in matched])

        # ======================
        # 投稿内容（KAWAII LAB. NEWS）
        # ======================
        text = (
            "📰 KAWAII LAB. NEWS\n"
            f"タイトル：{title}\n"
            f"関連：{related}\n"
            "媒体：Google News\n"
            "🕒 24h以内\n"
            f"🔗 {link}"
        )

        print("🚀 投稿:", title)
        client.create_tweet(text=text)

        # 投稿済み保存
        with open(POSTED_FILE, "a", encoding="utf-8") as f:
            f.write(link + "\n")

        posted_links.add(link)
        posted_count += 1

print(f"✅ 投稿完了：{posted_count} 件")

# ======================
# テスト投稿（必要な時だけ）
# ======================
test_mode = False  # True にするとテスト投稿

if test_mode:
    print("📝 テスト投稿を実行します...")
    client.create_tweet(
        text="📰 KAWAII LAB. NEWS\n【テスト投稿】FRUITS ZIPPER"
    )
    print("✅ テスト投稿が完了しました！")

# =========================
# テスト投稿（必要な時だけ）
# =========================


# ▼▼▼ テスト投稿用 ▼▼▼
test_mode = False   # ←投稿テストしたいときは True に

if test_mode:
    print("📝 テスト投稿を実行します...")
    client.create_tweet(text="【テスト】仲川瑠夏歌姫")
    print("✅ テスト投稿が完了しました！")
