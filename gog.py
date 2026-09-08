import json
import urllib.parse
import urllib.request

BASE = "https://sections.gog.com/v1/pages/2f"

PARAMS = {
    "countryCode": "IN",
    "locale": "en-US",
    "currencyCode": "USD",
}

STATE_FILE = "gog_state.json"


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


def main():
    giveaway = get_giveaway()

    if not giveaway:
        print("No active GOG giveaway.")
        return

    previous = load_state()

    print(f"Current giveaway: {giveaway['title']}")
    print(f"Product ID: {giveaway['id']}")
    print(f"Ends: {giveaway['endDate']}")

    if previous and previous.get("id") == giveaway["id"]:
        print("Same giveaway. Nothing to notify.")
        return

    print("New GOG giveaway detected!")

    save_state(giveaway)


if __name__ == "__main__":
    main()
