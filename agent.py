import os
import requests
from groq import Groq

# ─── CONFIG ───────────────────────────────────────────────
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]
NEWS_API_KEY   = os.environ["NEWS_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID        = os.environ["CHAT_ID"]
# ──────────────────────────────────────────────────────────

client = Groq(api_key=GROQ_API_KEY)


def fetch_ai_news():
    """Fetch latest AI prompting news from NewsAPI."""
    print("📰 Fetching news from NewsAPI...")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": "prompt engineering OR AI prompting OR LLM agents OR GPT prompts",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }
    r = requests.get(url, params=params)
    articles = r.json().get("articles", [])

    news_block = ""
    for i, a in enumerate(articles[:8], 1):
        title       = a.get("title", "No title")
        description = a.get("description", "No description")
        source      = a.get("source", {}).get("name", "Unknown")
        url_link    = a.get("url", "")
        news_block += f"{i}. [{source}] {title}\n{description}\nLink: {url_link}\n\n"

    return news_block


def summarize_with_groq(news_block):
    """Send the news to Groq and get a formatted Telegram briefing."""
    print("🤖 Summarizing with Groq...")

    prompt = f"""You are PromptPulse, a daily AI prompting intelligence agent.
Below are today's latest news articles about AI prompting and prompt engineering.
Read them and create a sharp, curated daily briefing for Telegram.

NEWS ARTICLES:
{news_block}

Format your response EXACTLY like this (use Telegram markdown):

🧠 *PromptPulse Daily*
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
[Something interesting or trending from the articles — 1-2 sentences]

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
    news_block = fetch_ai_news()
    if not news_block.strip():
        send_telegram("⚠️ PromptPulse could not find news today. Will try again tomorrow.")
        return
    briefing = summarize_with_groq(news_block)
    send_telegram(briefing)


if __name__ == "__main__":
    main()
