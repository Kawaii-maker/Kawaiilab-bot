import os
import random
import time
import feedparser
import tweepy
import unicodedata
from datetime import datetime, timedelta, timezone

ALLOWED_SOURCES = [
    "Yahoo!ニュース",
    "Real Sound",
    "リアルサウンド",
    "QJWeb",
    "モデルプレス",
]

GROUP_HASHTAGS = {
    "FRUITS ZIPPER": "#FRUITSZIPPER",
    "CANDY TUNE": "#CANDYTUNE",
    "CUTIE STREET": "#CUTIESTREET",
    "KAWAII LAB": "#カワラボ"
}


# =========================
# X API 設定
# =========================

API_KEY = "9gJWEzYv9AZgLMnmbNkN6UmVw"
API_SECRET = "qimkBh97gjLRVHnbvi0EH1NfbjADgy6Gt4maYMQB4jaNme2lrg"
ACCESS_TOKEN = "1970985602096254976-5NuQm4PRkWCT6sVW9AcYyTSZNRMefw"
ACCESS_SECRET = "VwG0qM9oKI2GyFsQlISa1LYZ8kyveV5nOGEbhtMzGIZfw"

# v2（ツイート投稿用）
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_SECRET,
)

# v1.1（画像アップロード用）
auth = tweepy.OAuth1UserHandler(
    API_KEY,
    API_SECRET,
    ACCESS_TOKEN,
    ACCESS_SECRET
)
api = tweepy.API(auth)

# =========================
# 設定
# =========================

IMAGE_BASE_DIR = "images"

GROUP_KEYWORDS = {
    "FRUITS_ZIPPER": ["FRUITS ZIPPER", "ＦＲＵＩＴＳ ＺＩＰＰＥＲ"],
    "CANDY_TUNE": ["CANDY TUNE", "ＣＡＮＤＹ ＴＵＮＥ"],
    "CUTIE_STREET": ["CUTIE STREET", "ＣＵＴＩＥ ＳＴＲＥＥＴ"],
    "KAWAII_LAB": ["KAWAII LAB", "KAWAII LAB."]
}

RSS_URLS = [
    "https://news.google.com/rss/search?q=FRUITS+ZIPPER&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CANDY+TUNE&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=CUTIE+STREET&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=KAWAII+LAB&hl=ja&gl=JP&ceid=JP:ja",
]

POST_INTERVAL = 90  # 秒（429対策）
posted_urls = set()

# =========================
# 関数
# =========================

def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)

def get_group_from_title(title: str):
    title_norm = normalize(title)
    for group, keywords in GROUP_KEYWORDS.items():
        for kw in keywords:
            if normalize(kw) in title_norm:
                return group
    return None

def get_random_image(group: str):
    if not group:
        return None

    folder = os.path.join(IMAGE_BASE_DIR, group)
    if not os.path.isdir(folder):
        return None

    images = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    return random.choice(images) if images else None

# =========================
# 関数
# =========================

def build_post_text(title, link, group):
    hashtags = GROUP_HASHTAGS.get(group, "")
    group_label = group.replace("_", " ") if group else "KAWAII LAB."

    return (
        f"{title}\n\n"
        f"🔗 \n"
        f"{link}\n\n"
        f"{hashtags}"
    )

def is_within_24_hours(entry):
    if not hasattr(entry, "published_parsed"):
        return False

    published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    return now - published <= timedelta(hours=24)

# =========================
# 実行
# =========================

for rss_url in RSS_URLS:
    print(f"\n🔍 RSS取得: {rss_url}")
    feed = feedparser.parse(rss_url)
    print(f"🟦 件数: {len(feed.entries)}")

    for entry in feed.entries[:40]:  # ← 最初は5件まで推奨
        title = entry.title
        link = entry.link
        if not is_within_24_hours(entry):
           print("⏭ 24時間外の記事なのでスキップ")
           continue


        # 媒体名チェック
        source_name = ""

        if hasattr(entry, "source") and "title" in entry.source:
         source_name = entry.source.title
        else:
            continue  # 媒体名が取れない記事はスキップ

        if not any(allowed in source_name for allowed in ALLOWED_SOURCES):
            continue  # 指定媒体以外はスキップ


        if link in posted_urls:
            continue

        group = get_group_from_title(title)
        image_path = get_random_image(group)

        print(f"🚀 投稿準備: {title}")
        print(f"🖼 画像: {image_path}")

        try:
            media_ids = None

            if image_path:
                media = api.media_upload(image_path)
                media_ids = [media.media_id]

            post_text = build_post_text(title, link, group)

            client.create_tweet(
               text=post_text,
               media_ids=media_ids)

            

            posted_urls.add(link)
            print("✅ 投稿成功")

            print(f"⏳ {POST_INTERVAL}秒待機")
            time.sleep(POST_INTERVAL)

        except tweepy.errors.TooManyRequests as e:
            print("⏸ 429 Too Many Requests：本日はここで終了")
            raise e

        except Exception as e:
            print("❌ 投稿失敗:", e)
