import os
import requests
import feedparser
from groq import Groq
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID        = os.environ["CHAT_ID"]
# ──────────────────────────────────────────────────────────

client = Groq(api_key=GROQ_API_KEY)

# ─── RSS FEED SOURCES ─────────────────────────────────────
RSS_FEEDS = [
    ("Google AI Blog",        "https://blog.research.google/feeds/posts/default"),
    ("OpenAI News",           "https://openai.com/news/rss.xml"),
    ("Hugging Face Blog",     "https://huggingface.co/blog/feed.xml"),
    ("MIT AI News",           "https://news.mit.edu/rss/topic/artificial-intelligence2"),
    ("Reddit PromptEng",      "https://www.reddit.com/r/PromptEngineering/.rss"),
    ("Reddit MachineLearning","https://www.reddit.com/r/MachineLearning/.rss"),
    ("VentureBeat AI",        "https://venturebeat.com/category/ai/feed/"),
    ("The Verge AI",          "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml"),
]
# ──────────────────────────────────────────────────────────


def fetch_rss_news():
    """Fetch latest AI news from RSS feeds."""
    print("📰 Fetching news from RSS feeds...")
    articles = []

    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:  # Take top 2 from each source
                title       = entry.get("title", "No title")
                summary     = entry.get("summary", entry.get("description", "No summary"))
                link        = entry.get("link", "")
                # Clean up summary (remove HTML tags roughly)
                summary = summary.replace("<p>", "").replace("</p>", " ")
                summary = summary[:200] + "..." if len(summary) > 200 else summary
                articles.append({
                    "source": source_name,
                    "title": title,
                    "summary": summary,
                    "link": link
                })
        except Exception as e:
            print(f"⚠️ Could not fetch {source_name}: {e}")
            continue

    return articles


def summarize_with_groq(articles):
    """Send articles to Groq and get a formatted Telegram briefing."""
    print("🤖 Summarizing with Groq...")

    # Build news block
    news_block = ""
    for i, a in enumerate(articles[:12], 1):
        news_block += f"{i}. [{a['source']}] {a['title']}\n{a['summary']}\nLink: {a['link']}\n\n"

    today = datetime.now().strftime("%B %d, %Y")

    prompt = f"""You are PromptPulse, a daily AI prompting intelligence agent.
Below are today's latest articles from top AI sources.
Read them and create a sharp, curated daily briefing for Telegram.
Today's date: {today}

NEWS ARTICLES:
{news_block}

Format your response EXACTLY like this (use Telegram markdown):

🧠 *PromptPulse Daily — {today}*
━━━━━━━━━━━━━━━━━━━━

📌 *TOP STORY*
[Best headline + 2-3 sentence summary + source link]

⚡ *QUICK HITS*
• [Story 2 — 1 sentence + link]
• [Story 3 — 1 sentence + link]
• [Story 4 — 1 sentence + link]

🛠 *TIP OF THE DAY*
[One actionable prompting technique based on today's news, explained in 2-3 sentences]

🔬 *FROM THE RESEARCH WORLD*
[Any research or technical finding from the articles — 2 sentences + link]

💬 *COMMUNITY BUZZ*
[Something interesting from Reddit or the community — 1-2 sentences]

━━━━━━━━━━━━━━━━━━━━
🔁 Delivered daily by PromptPulse"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
        temperature=0.7
    )

    return response.choices[0].message.content


def send_telegram(text):
    """Send the briefing to Telegram."""
    print("📲 Sending to Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print("✅ Message sent successfully!")
    else:
        print(f"❌ Telegram error: {r.status_code} — {r.text}")


def main():
    articles = fetch_rss_news()
    if not articles:
        send_telegram("⚠️ PromptPulse could not find news today. Will try again tomorrow.")
        return
    print(f"✅ Found {len(articles)} articles.")
    briefing = summarize_with_groq(articles)
    send_telegram(briefing)


if __name__ == "__main__":
    main()
