import os
import yfinance as yf
import pandas as pd
import requests
import numpy as np

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram non configuré")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def find_peaks_simple(data, distance=5):
    # Version sans scipy - trouve les pics locaux
    peaks = []
    for i in range(distance, len(data)-distance):
        if data[i] == max(data[i-distance:i+distance+1]):
            peaks.append(i)
    return peaks

def scan_symbol(symbol="EURUSD=X"):
    print(f"Scan {symbol}...")
    data = yf.download(symbol, period="5d", interval="1h")
    if len(data) < 50:
        return "Pas assez de données"
    
    close = data['Close'].values.flatten()
    peaks = find_peaks_simple(close)
    
    msg = f"✅ Divane Bot OK\n{symbol}: {len(close)} bougies analysées\nPics trouvés: {len(peaks)}\nPrix actuel: {close[-1]:.5f}"
    print(msg)
    send_telegram(msg)
    return msg

if __name__ == "__main__":
    scan_symbol("EURUSD=X")
    scan_symbol("BTC-USD")
