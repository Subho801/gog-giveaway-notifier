import json
import os
import urllib.parse
import urllib.request
from datetime import datetime

BASE = "https://sections.gog.com/v1/pages/2f"

PARAMS = {
    "countryCode": "IN",
    "locale": "en-US",
    "currencyCode": "USD",
}

STATE_FILE = "gog_state.json"
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK")


def get_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def get_giveaway():
    query = urllib.parse.urlencode(PARAMS)

    page = get_json(f"{BASE}?{query}")

    section = next(
        (
            section
            for section in page.get("sections", [])
            if section.get("sectionType") == "GIVEAWAY_SECTION"
        ),
        None,
    )

    if not section:
        return None

    section_id = section["sectionId"]

    data = get_json(
        f"{BASE}/sections/{section_id}?{query}"
    )

    properties = data.get("properties", {})
    product = properties.get("product")

    if not product or not product.get("title"):
        return None

    return {
        "id": str(product.get("id")),
        "title": product.get("title"),
        "slug": product.get("slug"),
        "endDate": properties.get("endDate"),
        "cover": product.get("coverHorizontal"),
    }


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_state(giveaway):
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        json.dump(giveaway, file, indent=2)



def discord_timestamp(iso_date):
    if not iso_date:
        return "Unknown"

    try:
        dt = datetime.fromisoformat(iso_date)
        timestamp = int(dt.timestamp())

        return f"<t:{timestamp}:R>"

    except Exception:
        return iso_date


def send_discord(giveaway):
    if not DISCORD_WEBHOOK:
        print("❌ DISCORD_WEBHOOK is not configured.")
        return False

    game_url = f"https://www.gog.com/game/{giveaway['slug']}"

    # Replace these with your custom image URLs
    GOG_LOGO_URL = "https://file.garden/afbSsuts32dZ5wSl/gog-galaxy-removebg-preview.png"
    RONALDO_IMAGE_URL = "https://files.catbox.moe/qttqpy.png"

    end_timestamp = discord_timestamp(giveaway["endDate"])

    payload = {
        "content": "@everyone",

        "embeds": [
            {
                "author": {
                    "name": "Subho's GOG Freebie Informer",
                    "icon_url": GOG_LOGO_URL
                },

                "title": f"🎁 {giveaway['title']}",
                "url": game_url,

                "description": (
                    "A new game is available for **free on GOG!**"
                ),

                "fields": [
                    {
                        "name": "🎮 Game",
                        "value": f"[{giveaway['title']}]({game_url})",
                        "inline": True
                    },
                    {
                        "name": "⏰ Ends",
                        "value": end_timestamp,
                        "inline": True
                    },
                    {
                        "name": "🎁 Claim",
                        "value": "[**Claim on GOG**](https://www.gog.com/giveaway/claim)",
                        "inline": False
                    }
                ],

                "image": {
                    "url": giveaway["cover"]
                },

                "footer": {
                    "text": "Subho's GOG Freebie Informer",
                    "icon_url": RONALDO_IMAGE_URL
                }
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "GOG-Giveaway-Notifier",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            if 200 <= response.status < 300:
                print("✅ Discord notification sent.")
                return True

            print(f"❌ Discord returned HTTP {response.status}")
            return False

    except Exception as error:
        print(f"❌ Discord webhook failed: {error}")
        return False


def main():
    print("[1] Checking GOG giveaway...")

    giveaway = get_giveaway()

    if not giveaway:
        print("❌ No active GOG giveaway found.")
        return

    print(f"✅ Current giveaway: {giveaway['title']}")
    print(f"   ID: {giveaway['id']}")
    print(f"   Ends: {giveaway['endDate']}")

    previous = load_state()

    if previous and previous.get("id") == giveaway["id"]:
        print("ℹ️ Same giveaway. Nothing to notify.")
        return

    print("🚨 New GOG giveaway detected!")

    if send_discord(giveaway):
        save_state(giveaway)
        print("✅ Giveaway state saved.")
    else:
        print("⚠️ Notification failed. State was NOT saved.")


if __name__ == "__main__":
    main()
