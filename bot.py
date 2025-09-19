import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 🔹 Movie URLs to track
MOVIES = [
    {
        "name": "BMS - They Call Him OG",
        "url": "https://in.bookmyshow.com/movies/payakaraopeta/they-call-him-og/ET00369074",
        "type": "bms"
    },
    {
        "name": "District - They Call Him OG",
        "url": "https://www.district.in/movies/they-call-him-og-movie-tickets-in-tuni-MV171668",
        "type": "district"
    }
]

# 🔹 Telegram Bot Config
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# 🔹 Test Mode
TEST_MODE = False

# 🔹 Send Telegram message
def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=data)
        print(f"[ALERT] Telegram message sent: {msg}")
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")

# 🔹 Check tickets availability
def tickets_available(movie):
    if TEST_MODE:
        # simulate tickets for testing
        if movie["type"] == "district":
            return ["Sri Rama Theatre", "SVC Theatre"]
        elif movie["type"] == "bms":
            return ["BMS Tickets"]
        return []

    try:
        headers = {}
        if movie["type"] == "bms":
            # Fix BMS 403 issue by adding browser headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/140.0.0.0 Safari/537.36"
            }

        resp = requests.get(movie["url"], timeout=10, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        if movie["type"] == "district":
            theatre_divs = soup.find_all("div", string=True)
            available_theatres = []
            for div in theatre_divs:
                text = div.get_text(strip=True)
                txt_lower = text.lower()
                # Trigger rules: "sri" AND "tuni" OR "svc" AND "payakaraopeta"
                if "sri" in txt_lower and "tuni" in txt_lower:
                    available_theatres.append(text)
                elif "svc" in txt_lower and "payakaraopeta" in txt_lower:
                    available_theatres.append(text)
            return available_theatres

        elif movie["type"] == "bms":
            button = soup.find("button", attrs={"data-phase": "postRelease"})
            return ["BMS Tickets"] if button else []

        return []

    except Exception as e:
        print(f"[ERROR] Failed to fetch {movie['name']}: {e}")
        return []

# 🔹 Main Loop
def main():
    print("[INFO] Movie Ticket Notifier started...")
    last_state = {movie["name"]: [] for movie in MOVIES}

    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for movie in MOVIES:
            available_theatres = tickets_available(movie)

            # Send alert only for **new** theatres
            new_theatres = [t for t in available_theatres if t not in last_state[movie["name"]]]
            for theatre in new_theatres:
                send_telegram(f"🎟 {theatre} - Tickets Available! {movie['url']}")

            last_state[movie["name"]] = available_theatres
            status = "AVAILABLE" if available_theatres else "NOT available"
            print(f"[CHECK] {now} - {movie['name']} {status}.")

        time.sleep(60)

if __name__ == "__main__":
    main()
