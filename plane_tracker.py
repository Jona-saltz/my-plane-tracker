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
CSV_URL = "https://raw.githubusercontent.com/Jona-saltz/my-plane-tracker/refs/heads/main/planes.csv"


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
    """Downloads the CSV and returns a dictionary: { 'PlaneName': 'Description' }"""
    print("Fetching latest plane list from GitHub...")
    try:
        response = requests.get(CSV_URL)
        if response.status_code != 200:
            print(f"Error fetching CSV: {response.status_code}")
            return {}

        file_content = io.StringIO(response.content.decode('utf-8-sig'))

        # We use a dictionary now: Key = Column A (Name), Value = Column B (Description)
        search_data = {}
        reader = csv.reader(file_content)

        for row in reader:
            if row:
                plane_name = row[0].strip()
                # Check if Column B exists, otherwise use empty string
                plane_desc = row[1].strip() if len(row) > 1 else ""

                # Store it in the dictionary
                search_data[plane_name] = plane_desc

        return search_data

    except Exception as e:
        print(f"Error reading online CSV: {e}")
        return {}


def check_flightaware():
    import cloudscraper
    scraper = cloudscraper.create_scraper()
    url = "https://www.flightaware.com/live/aircrafttype/"

    try:
        current_time = datetime.datetime.now().strftime('%H:%M')

        # This is now a dictionary: {'Beluga': 'Transport', 'An-124': 'Heavy'}
        search_data = get_search_strings()

        # We only want to print the Keys (Column A) in the log
        print(f"[{current_time}] Checking for: {list(search_data.keys())}")

        response = scraper.get(url)
        if response.status_code != 200:
            print(f"Error reaching site: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()  # Convert page to lower case once for speed

        found_matches = []

        # Iterate through the dictionary items (Name, Description)
        for plane_name, plane_desc in search_data.items():

            # STRICTLY search only for the Name (Column A)
            if plane_name.lower() in page_text:
                # Format the result as "Name, Description"
                formatted_result = f"{plane_name}, {plane_desc}"
                found_matches.append(formatted_result)

        if found_matches:
            # Join them with newlines so they list nicely
            list_text = '\n'.join(found_matches)
            msg = f"✈️ ALERT! Found aircraft:\n\n{list_text}\n\nCheck now: {url}"
            send_telegram_alert(msg)
        else:
            print("No matches found.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_flightaware()