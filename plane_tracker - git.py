import requests
from bs4 import BeautifulSoup
import time
import datetime
import csv
import os

# --- CONFIGURATION (UPDATED FOR GITHUB) ---
# Instead of hardcoding, we get these from the environment
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CSV_FILENAME = "planes.csv"


# We don't need the loop or sleep here because GitHub will handle the scheduling!
# ---------------------

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Missing Telegram keys in environment variables.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        print(f"-> Notification sent: {message}")
    except Exception as e:
        print(f"Error sending Telegram: {e}")


def get_search_strings():
    """Reads the list of planes, trying different encodings."""
    search_list = []
    if not os.path.exists(CSV_FILENAME):
        print(f"Warning: {CSV_FILENAME} not found. Using default list.")
        return ["Beluga", "A3ST"]

    encodings_to_try = ['utf-8-sig', 'utf-8', 'cp1252', 'latin-1']

    for encoding in encodings_to_try:
        try:
            with open(CSV_FILENAME, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        search_list.append(row[0].strip())
            return search_list
        except UnicodeDecodeError:
            continue

    print("Error: Could not read CSV.")
    return []


def check_flightaware():
    # Use cloudscraper just in case FlightAware gets stricter
    import cloudscraper
    scraper = cloudscraper.create_scraper()

    url = "https://www.flightaware.com/live/aircrafttype/"

    try:
        current_time = datetime.datetime.now().strftime('%H:%M')
        search_strings = get_search_strings()

        print(f"[{current_time}] Checking for: {search_strings}")

        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Error reaching site: Status {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        found_matches = []
        for plane in search_strings:
            if plane.lower() in page_text.lower():
                found_matches.append(plane)

        if found_matches:
            msg = f"✈️ GITALERT! Found aircraft:\n" + "\n".join(found_matches) + f"\n\nCheck now: {url}"
            send_telegram_alert(msg)
        else:
            print("No matches found.")

    except Exception as e:
        print(f"Error during check: {e}")


if __name__ == "__main__":
    # The 'while True' loop is REMOVED. GitHub runs this script once, then shuts down until next time.

    check_flightaware()

