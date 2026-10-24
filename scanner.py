import yfinance as yf
import numpy as np
from scipy.signal import find_peaks
import requests
import os

MARKETS = {
    "EUR/USD": "EURUSD=X",
    "FRA40": "^FCHI",
    "DXY": "DX-Y.NYB",
    "GBP/USD": "GBPUSD=X"
}

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    print(msg)

def get_data(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="4h", progress=False)
        if df is None or len(df)==0:
            return None
        return df.dropna()
    except Exception as e:
        print(f"Erreur {ticker}: {e}")
        return None

for name, ticker in MARKETS.items():
    df = get_data(ticker)
    if df is None or len(df) < 60:
        continue
    highs = df['High'].values.flatten()
    lows = df['Low'].values.flatten()
    close = float(df['Close'].iloc[-1])

    peaks, _ = find_peaks(highs, distance=15, prominence=np.std(highs)*0.5)
    troughs, _ = find_peaks(-lows, distance=15, prominence=np.std(lows)*0.5)

    # DOUBLE TOP / BOTTOM
    if len(peaks)>=2 and abs(highs[peaks[-1]]-highs[peaks[-2]])/highs[peaks[-1]] < 0.015:
        send(f"🚨 *DOUBLE TOP* sur *{name}* H4\nPrix: {close:.2f}")
    if len(troughs)>=2 and abs(lows[troughs[-1]]-lows[troughs[-2]])/lows[troughs[-1]] < 0.015:
        send(f"🚨 *DOUBLE BOTTOM* sur *{name}* H4\nPrix: {close:.2f}")

    # ETE / ETE INVERSE
    if len(peaks)>=3:
        p1,p2,p3 = peaks[-3],peaks[-2],peaks[-1]
        if highs[p2] > highs[p1] and highs[p2] > highs[p3] and abs(highs[p1]-highs[p3])/highs[p1] < 0.03:
            send(f"🚨 *ETE* sur *{name}* H4\nTete plus haute")
    if len(troughs)>=3:
        t1,t2,t3 = troughs[-3],troughs[-2],troughs[-1]
        if lows[t2] < lows[t1] and lows[t2] < lows[t3] and abs(lows[t1]-lows[t3])/lows[t1] < 0.03:
            send(f"🚨 *ETE INVERSE* sur *{name}* H4")

    # TRIANGLE
    if np.std(highs[-5:]) < np.mean(highs)*0.003 and lows[-1] > lows[-10]:
        send(f"🚨 *TRIANGLE ASCENDANT* sur *{name}* H4")
    if np.std(lows[-5:]) < np.mean(lows)*0.003 and highs[-1] < highs[-10]:
        send(f"🚨 *TRIANGLE DESCENDANT* sur *{name}* H4")
