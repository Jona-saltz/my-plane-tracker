import requests
from bs4 import BeautifulSoup
import time
import datetime
import csv
import os
import io
# This library allows us to read the .env file locally
from dotenv import load_dotenv

# --- CONFIGURATION ---

# 1. Load Secrets
# This command looks for a .env file on your computer.
# If it doesn't find one (like on GitHub Actions), it skips it without crashing.
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 2. Centralized CSV URL
# This points to the "Raw" version of your file on GitHub.
# Now both your PC and the GitHub Action read from this exact same list.
CSV_URL = "https://raw.githubusercontent.com/Jona-saltz/my-plane-tracker/refs/heads/main/planes.csv?token=GHSAT0AAAAAADSEHR6BZIB4AAUWGQNA4K4E2KYK3NQ"


# ---------------------

def send_telegram_alert(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Error: Keys not found. Check .env (local) or Secrets (GitHub).")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
        print(f"-> Notification sent: {message}")
    except Exception as e:
        print(f"Error sending Telegram: {e}")


def get_search_strings():
    """Downloads the CSV from GitHub so everyone uses the same list."""
    print("Fetching latest plane list from GitHub...")
    try:
        # Get the file from the internet
        response = requests.get(CSV_URL)
        if response.status_code != 200:
            print(f"Error fetching CSV: {response.status_code}")
            return ["Beluga"]  # Fallback if internet fails

        # We decode 'utf-8-sig' to automatically remove that invisible BOM character
        file_content = io.StringIO(response.content.decode('utf-8-sig'))

        search_list = []
        reader = csv.reader(file_content)
        for row in reader:
            if row:
                # remove extra spaces and add to list
                search_list.append(row[0].strip())

        return search_list

    except Exception as e:
        print(f"Error reading online CSV: {e}")
        return []


def check_flightaware():
    # We use cloudscraper to avoid being blocked by FlightAware's anti-bot protection
    import cloudscraper
    scraper = cloudscraper.create_scraper()
    url = "https://www.flightaware.com/live/aircrafttype/"

    try:
        current_time = datetime.datetime.now().strftime('%H:%M')
        search_strings = get_search_strings()

        print(f"[{current_time}] Checking for: {search_strings}")

        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Error reaching site: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        found_matches = []
        for plane in search_strings:
            if plane.lower() in page_text.lower():
                found_matches.append(plane)

        if found_matches:
            msg = f"✈️ ALERT! Found aircraft: {', '.join(found_matches)}\nCheck now: {url}"
            send_telegram_alert(msg)
        else:
            print("No matches found.")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_flightaware()