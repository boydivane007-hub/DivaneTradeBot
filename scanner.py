import os, requests, yfinance as yf, pandas as pd, numpy as np
from datetime import datetime

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except Exception as e:
        print(e)
    print(msg)

def rsi_calc(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze():
    symbols = {"EURUSD=X": "EUR/USD", "GBPUSD=X": "GBP/USD", "BTC-USD": "BTC", "XAUUSD=X": "GOLD"}
    rapport = f"📊 *Rapport Divane - {datetime.now().strftime('%A %H:%M')}*\n\n"
    is_weekend = datetime.now().weekday() >= 5
    if is_weekend:
        rapport += "_Marché Forex FERMÉ (week-end)_ - Reprise dimanche 23h\n\n"

    signals_found = False
    for yf_sym, name in symbols.items():
        try:
            df = yf.download(yf_sym, period="7d", interval="1h", auto_adjust=True, progress=False)
            if len(df) < 60: continue
            if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
            close = df['Close']
            price = float(close.iloc[-1])
            rsi = float(rsi_calc(close).iloc[-1])
            
            signal_txt = ""
            if rsi < 32:
                signal_txt = "🟢 Zone ACHAT possible"
                signals_found = True
            elif rsi > 68:
                signal_txt = "🔴 Zone VENTE possible"
                signals_found = True
            else:
                signal_txt = "⏸️ Pas de signal"

            rapport += f"*{name}*: {price:.2f} | RSI {rsi:.1f} | {signal_txt}\n"
        except Exception as e:
            rapport += f"*{name}*: erreur {e}\n"

    rapport += f"\n_Bot actif ✅ Prochain scan dans 1h_"
    send(rapport)

if __name__ == "__main__":
    analyze()
