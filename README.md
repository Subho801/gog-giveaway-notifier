# 🎁 GOG Giveaway Notifier

An automated Discord notifier that monitors the official GOG giveaway section and sends a Discord notification when a new free game is detected.

The project uses GOG's publicly accessible section API, Python, Discord webhooks, and GitHub Actions to automatically detect and announce new giveaways.

---

## ✨ Features

- 🎮 Monitors GOG's current giveaway
- 🆕 Detects newly released giveaways
- 🔁 Prevents duplicate notifications
- 💾 Persists giveaway state in `gog_state.json`
- 🔔 Sends Discord notifications through a webhook
- 👤 Supports Discord role mentions
- 🖼️ Includes GOG game artwork
- 📅 Displays exact and relative giveaway end times
- 🔗 Makes the game title clickable
- ⚙️ Runs automatically through GitHub Actions
- ⏱️ Checks for new giveaways every 10 minutes
- 🛡️ Preserves existing state if the GOG request fails

---

## 🧠 How It Works

The notifier uses GOG's public section API to determine the currently active giveaway.

The workflow:

```text
GitHub Actions
      ↓
Run gog.py
      ↓
Fetch current GOG giveaway
      ↓
Compare with gog_state.json
      ↓
New giveaway?
   ↙          ↘
 YES           NO
  ↓             ↓
Discord      Do nothing
  ↓
Save state
  ↓
Commit state to GitHub
