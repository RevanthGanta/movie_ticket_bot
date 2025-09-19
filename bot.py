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

# 🔹 Telegram Bot Config (HARDCODED)
BOT_TOKEN = "8377818111:AAGBC3dv55LdiS7Qv_V5wLnNoEIF2fYxKCw"
CHAT_ID = "1827266917"

# 🔹 Test Mode: True = simulate, False = real check
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
        return True  # simulate tickets for testing

    try:
        resp = requests.get(movie["url"], timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        if movie["type"] == "district":
            theatre_divs = soup.find_all("div", string=True)
            available_theatres = []
            for div in theatre_divs:
                text = div.get_text(strip=True)
                if "sri" in text.lower() or "svc" in text.lower():
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

            # 🔹 If new tickets found, send alert
            new_theatres = [t for t in available_theatres if t not in last_state[movie["name"]]]
            for theatre in new_theatres:
                send_telegram(f"🎟 {theatre} - Tickets Available! {movie['url']}")

            # 🔹 Update last state
            last_state[movie["name"]] = available_theatres

            status = "AVAILABLE" if available_theatres else "NOT available"
            print(f"[CHECK] {now} - {movie['name']} {status}.")

        time.sleep(60)

if __name__ == "__main__":
    main()
