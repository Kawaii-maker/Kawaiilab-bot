import os
import feedparser
import tweepy
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import random

load_dotenv()

ALLOWED_SOURCES = [
    "Yahoo!ニュース",
    "Real Sound",
    "リアルサウンド",
    "ORICON NEWS",
    "オリコン",
    "ナタリー",
    "ENCOUNT",
    "QJWeb",
    "Quick Japan",
    "Billboard JAPAN",
    "モデルプレス",
]




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
# Google News RSS（最強）
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

def get_random_image(folder):
    if not folder or not os.path.exists(folder):
        return None

    images = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".png"))
    ]

    if not images:
        return None

    return random.choice(images)

auth = tweepy.OAuth1UserHandler(
    os.getenv("API_KEY"),
    os.getenv("API_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET")
)

api_v1 = tweepy.API(auth)



# ======================
# RSSチェック開始
# ======================
for rss_url in RSS_URLS:
    print("🔍 RSS取得:", rss_url)
    feed = feedparser.parse(rss_url)
    print("🟦 件数:", len(feed.entries))

    for entry in feed.entries:
     title = entry.title
     link = entry.link
     title_lower = title.lower()

    # 媒体チェック
    if not hasattr(entry, "source") or "title" not in entry.source:
        continue

    source_name = entry.source.title
    if not any(allowed in source_name for allowed in ALLOWED_SOURCES):
        continue

    # 時間チェック
    if not hasattr(entry, "published_parsed"):
        continue

    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    if published < limit_time:
        continue

    # グループ判定
    image_folder = None
    if "fruits zipper" in title_lower:
        image_folder = "images/fruits_zipper"
    elif "cutie street" in title_lower:
        image_folder = "images/cutie_street"
    elif "candy tune" in title_lower:
        image_folder = "images/candy_tune"

    if link in posted_links:
        continue

    text = f"📰 {title}\n{link}"
    image_path = get_random_image(image_folder)

    print("🚀 投稿:", title)
    print("🖼 画像:", image_path)

    if image_path:
        media = api_v1.media_upload(filename=image_path)
        client.create_tweet(
            text=text,
            media_ids=[media.media_id]
        )
    else:
        client.create_tweet(text=text)

    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

    posted_links.add(link)
    posted_count += 1

print(f"✅ 投稿完了：{posted_count} 件")


# =========================
# テスト投稿（必要な時だけ）
# =========================


# ▼▼▼ テスト投稿用 ▼▼▼
test_mode = False   # ←投稿テストしたいときは True に

if test_mode:
    print("📝 テスト投稿を実行します...")
    client.create_tweet(text="【テスト】仲川瑠夏歌姫")
    print("✅ テスト投稿が完了しました！")
