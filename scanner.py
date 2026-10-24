import os, requests, yfinance as yf, pandas as pd, numpy as np

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass
    print(msg)

def rsi_calc(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def find_levels(close, distance=10):
    levels = []
    for i in range(distance, len(close)-distance):
        if close[i] == max(close[i-distance:i+distance+1]) or close[i] == min(close[i-distance:i+distance+1]):
            levels.append(close[i])
    return sorted(set([round(x,5) for x in levels]))

def analyze(symbol="EURUSD=X"):
    df = yf.download(symbol, period="7d", interval="1h", auto_adjust=True, progress=False)
    if len(df) < 60: return
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    
    close = df['Close']
    rsi = rsi_calc(close).iloc[-1]
    price = float(close.iloc[-1])
    levels = find_levels(close.values)
    
    support = [l for l in levels if l < price]
    resistance = [l for l in levels if l > price]
    sup = max(support) if support else price*0.998
    res = min(resistance) if resistance else price*1.002

    # LOGIQUE SIGNAL
    signal = None
    if rsi < 32 and price <= sup*1.001: # survente + sur support
        signal = "ACHAT"
        sl = price - (price-sup)*1.5 if price!=sup else price*0.997
        tp = res
    elif rsi > 68 and price >= res*0.999: # surachat + sur résistance
        signal = "VENTE"
        sl = price + (res-price)*1.5 if price!=res else price*1.003
        tp = sup

    if signal:
        emoji = "🟢" if signal=="ACHAT" else "🔴"
        msg = f"{emoji} *SIGNAL {signal} - {symbol}*\n\nPrix: `{price:.5f}`\nRSI(14): `{rsi:.1f}`\n\nSupport: `{sup:.5f}`\nRésistance: `{res:.5f}`\n\nEntrée: `{price:.5f}`\nSL: `{sl:.5f}`\nTP: `{tp:.5f}`\n\n_Divane Bot - {pd.Timestamp.now().strftime('%H:%M')}_"
        send(msg)
    else:
        print(f"{symbol} - Pas de signal - Prix {price:.5f} RSI {rsi:.1f}")

if __name__ == "__main__":
    for sym in ["EURUSD=X", "GBPUSD=X", "BTC-USD", "XAUUSD=X"]:
        try: analyze(sym)
        except Exception as e: print(e)
