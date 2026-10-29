# 📖 Motivate Notify - Daily Bible Quotes Notification System

An automated notification system that delivers personalized Bible quotes directly to your phone twice a day:
- 🌅 **7:00 AM (Morning)**: Uplifting and inspiring quotes to start your day with faith and purpose.
- 🌙 **10:00 PM (Night)**: Peaceful and calming scriptures for sweet rest and protection before sleep.

---

## 🚀 Features

- **Contextual Quotes**: Intelligently detects morning vs. evening to send appropriate scripture.
- **Multiple API Sources + Offline Fallbacks**: Fetches live Verse of the Day from NET Bible API, with a rich offline catalog of curated scriptures for guaranteed delivery.
- **Instant Phone Push Notifications**: Sends real-time lockscreen alerts with sound via [ntfy.sh](https://ntfy.sh).
- **Optional WhatsApp Delivery**: Built-in support for WhatsApp messaging via CallMeBot.
- **Automated Scheduling**:
  - Native Windows Scheduled Task (`DailyBibleQuote7AM_10PM`) running sharp at 7:00 AM & 10:00 PM.
  - Antigravity Scheduled Automation sidecar integration (`CRON_TZ=Asia/Kolkata 0 7,22 * * *`).

---

## 📁 Project Structure

```
├── config.example.json  # Configuration template (rename to config.json for local use)
├── send_bible_quote.py  # Core script: fetches scripture and publishes notifications
├── setup_task.ps1       # One-click Windows Task Scheduler setup script
├── .gitignore           # Keeps local config.json and private credentials off GitHub
└── README.md            # Project documentation
```

---

## 📲 How to Receive Notifications on Your Phone

You can receive notifications on Android or iOS:

1. **Option 1: In Mobile Browser (Instant - No App Needed)**
   - Open `https://ntfy.sh/<YOUR_CHOSEN_TOPIC>` on your phone.
   - Tap **"Subscribe"** and allow notifications.

2. **Option 2: Native App (Recommended for Lockscreen Alarms)**
   - Install **ntfy** from Google Play Store or Apple App Store.
   - Tap `+` and subscribe to your topic name.

---

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sherlinsilvia14/motivate_notify.git
   cd motivate_notify
   ```

2. **Create your local configuration**:
   Copy `config.example.json` to `config.json`:
   ```bash
   copy config.example.json config.json
   ```
   Edit `config.json` to set your desired topic name and phone number.

3. **Run a test notification**:
   ```bash
   python send_bible_quote.py
   ```

4. **Register Windows Scheduled Task** (to run automatically daily at 7 AM & 10 PM):
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup_task.ps1
   ```

---

## 📜 License
MIT License
