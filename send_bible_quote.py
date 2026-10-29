import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

CONFIG_FILE = Path(__file__).parent / "config.json"
LOG_FILE = Path(__file__).parent / "execution.log"

NTFY_TOPIC = "daily-bible-quotes"

MORNING_VERSES = [
    {
        "text": "The steadfast love of the Lord never ceases; his mercies never come to an end; they are new every morning; great is your faithfulness.",
        "reference": "Lamentations 3:22-23"
    },
    {
        "text": "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future.",
        "reference": "Jeremiah 29:11"
    },
    {
        "text": "The Lord is my shepherd; I shall not want. He makes me lie down in green pastures. He leads me beside still waters.",
        "reference": "Psalm 23:1-2"
    },
    {
        "text": "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight.",
        "reference": "Proverbs 3:5-6"
    },
    {
        "text": "I can do all things through Christ who strengthens me.",
        "reference": "Philippians 4:13"
    },
    {
        "text": "This is the day that the Lord has made; let us rejoice and be glad in it.",
        "reference": "Psalm 118:24"
    },
    {
        "text": "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.",
        "reference": "Joshua 1:9"
    }
]

EVENING_VERSES = [
    {
        "text": "In peace I will lie down and sleep, for you alone, Lord, make me dwell in safety.",
        "reference": "Psalm 4:8"
    },
    {
        "text": "When you lie down, you will not be afraid; when you lie down, your sleep will be sweet.",
        "reference": "Proverbs 3:24"
    },
    {
        "text": "Come to me, all you who are weary and burdened, and I will give you rest.",
        "reference": "Matthew 11:28"
    },
    {
        "text": "Peace I leave with you; my peace I give you. I do not give to you as the world gives. Do not let your hearts be troubled and do not be afraid.",
        "reference": "John 14:27"
    },
    {
        "text": "He who dwells in the shelter of the Most High will abide in the shadow of the Almighty. I will say to the Lord, 'My refuge and my fortress, my God, in whom I trust.'",
        "reference": "Psalm 91:1-2"
    },
    {
        "text": "Cast all your anxiety on him because he cares for you.",
        "reference": "1 Peter 5:7"
    },
    {
        "text": "The Lord bless you and keep you; the Lord make his face shine upon you and be gracious to you; the Lord turn his face toward you and give you peace.",
        "reference": "Numbers 6:24-26"
    }
]

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    try:
        print(formatted)
    except UnicodeEncodeError:
        print(formatted.encode("ascii", errors="replace").decode("ascii"))
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log(f"Warning: Could not read config file: {e}")
    return {}

def fetch_verse(is_morning: bool) -> tuple[str, str]:
    """Fetch verse from API or time-contextual curated scriptures."""
    day_of_year = datetime.now().timetuple().tm_yday
    verse_pool = MORNING_VERSES if is_morning else EVENING_VERSES

    # If morning, try NET Bible verse of the day
    if is_morning:
        try:
            req = urllib.request.Request(
                "https://labs.bible.org/api/?passage=votd&type=json",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                if data and isinstance(data, list):
                    book = data[0].get("bookname", "")
                    chapter = data[0].get("chapter", "")
                    verses_text = " ".join(v.get("text", "").strip() for v in data)
                    first_verse = data[0].get("verse", "")
                    last_verse = data[-1].get("verse", "")
                    v_range = f"{first_verse}" if first_verse == last_verse else f"{first_verse}-{last_verse}"
                    ref = f"{book} {chapter}:{v_range}"
                    return verses_text.strip(), ref.strip()
        except Exception as e:
            log(f"Online API notice ({e}), using curated morning scripture.")

    # Select from contextual verse pool based on day index
    idx = day_of_year % len(verse_pool)
    item = verse_pool[idx]
    return item["text"], item["reference"]

def send_ntfy_notification(topic: str, title: str, message: str, tags: str) -> bool:
    """Send instant push notification to phone via ntfy."""
    url = f"https://ntfy.sh/{topic}"
    try:
        req = urllib.request.Request(
            url,
            data=message.encode("utf-8"),
            headers={
                "Title": urllib.parse.quote(title),
                "Priority": "default",
                "Tags": tags
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            log(f"ntfy push notification sent successfully (status {resp.status})")
            return True
    except Exception as e:
        log(f"Failed to send ntfy notification: {e}")
        return False

def send_callmebot_whatsapp(phone: str, message: str, apikey: str) -> bool:
    """Optionally send WhatsApp if API key is provided."""
    encoded_text = urllib.parse.quote(message)
    cleaned_phone = phone.replace("+", "").replace(" ", "").replace("-", "")
    url = f"https://api.callmebot.com/whatsapp.php?phone={cleaned_phone}&text={encoded_text}&apikey={apikey}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8")
            log(f"CallMeBot API Response: {body}")
            return "error" not in body.lower()
    except Exception as e:
        log(f"CallMeBot WhatsApp notification skipped or failed: {e}")
        return False

def main():
    config = load_config()
    topic = config.get("ntfy_topic", NTFY_TOPIC)
    phone = config.get("phone", "")
    apikey = config.get("callmebot_apikey")

    now = datetime.now()
    current_hour = now.hour

    # Morning if before 12:00 PM, otherwise Evening / Night
    is_morning = current_hour < 12

    time_label = "Morning" if is_morning else "Evening"
    log(f"Fetching Daily {time_label} Bible Quote (Hour: {current_hour})...")

    verse_text, reference = fetch_verse(is_morning=is_morning)

    today_str = now.strftime("%A, %d %B %Y")

    if is_morning:
        title = f"Morning Bible Verse - {reference}"
        tags = "sunrise,pray,book"
        notification_body = (
            f"\"{verse_text}\"\n\n"
            f"— {reference}\n\n"
            f"Have a blessed and joyful day ahead! 🙏✨"
        )
        whatsapp_msg = (
            f"🌅 *Good Morning! Daily Bible Quote*\n"
            f"📅 {today_str}\n\n"
            f"\"{verse_text}\"\n\n"
            f"— *{reference}*\n\n"
            f"✨ Have a blessed and joyful day ahead! 🙏"
        )
    else:
        title = f"Night Bible Verse - {reference}"
        tags = "crescent_moon,pray,bed"
        notification_body = (
            f"\"{verse_text}\"\n\n"
            f"— {reference}\n\n"
            f"Rest peacefully in God's peace and grace tonight! 😴🙏"
        )
        whatsapp_msg = (
            f"🌙 *Good Night! Evening Bible Quote*\n"
            f"📅 {today_str}\n\n"
            f"\"{verse_text}\"\n\n"
            f"— *{reference}*\n\n"
            f"😴 Rest peacefully in God's peace and grace tonight! 🙏"
        )

    log(f"Sending Verse: {reference} [{title}]")

    # Primary delivery: ntfy push notification to phone
    success = send_ntfy_notification(topic=topic, title=title, message=notification_body, tags=tags)

    # Secondary delivery: if CallMeBot API key is configured, also send via WhatsApp
    if apikey and apikey != "YOUR_API_KEY_HERE":
        log("Attempting WhatsApp delivery as well...")
        send_callmebot_whatsapp(phone=phone, message=whatsapp_msg, apikey=apikey)

    if success:
        log(f"SUCCESS: Daily {time_label} Bible Quote successfully delivered to phone!")
    else:
        log("ERROR: Failed to deliver notification.")
        sys.exit(1)

if __name__ == "__main__":
    main()
