import yfinance as yf, pandas as pd, numpy as np, os, json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

CORE_MOMENTUM = ["CUAN.JK","BRPT.JK","DSSA.JK","BRMS.JK"]
CORE_TREND = ["TPIA.JK","PTRO.JK","MAPA.JK","WIFI.JK","ISAT.JK","MDKA.JK","ESSA.JK","INCO.JK"]
FILTERED = CORE_MOMENTUM + CORE_TREND
SHEET_ID = os.environ.get("SHEET_ID")

def rsi(s, p=14):
    d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean()
    rs=g/l; return 100-(100/(1+rs))
def adx(df, p=14):
    h=df['High']; l=df['Low']; c=df['Close']
    pdm=h.diff(); mdm=-l.diff(); pdm[pdm<0]=0; mdm[mdm<0]=0
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(p).mean(); pdi=100*(pdm.rolling(p).mean()/atr); mdi=100*(mdm.rolling(p).mean()/atr)
    dx=100*((pdi-mdi).abs()/(pdi+mdi).abs()); return dx.rolling(p).mean(), pdi, mdi

print(f"Downloading {len(FILTERED)} tickers...")
raw=yf.download(FILTERED, period="6mo", group_by='ticker', auto_adjust=False, threads=True)

signals=[]
for t in FILTERED:
    try:
        df=raw[t].dropna() if len(FILTERED)>1 else raw.dropna()
        if len(df)<60: continue
        df['High55']=df['Close'].rolling(55).max().shift(1)
        df['Low10']=df['Close'].rolling(10).min().shift(1)
        df['Low20']=df['Close'].rolling(20).min().shift(1)
        df['AvgVal20']=(df['Close']*df['Volume']).rolling(20).mean().shift(1)
        df['RSI14']=rsi(df['Close'])
        df['ADX14'], df['+DI'], df['-DI']=adx(df,14)
        df['PrevClose']=df['Close'].shift(1)
        last=df.iloc[-1]; prev=df.iloc[-2]
        high55=last['High55']; low10=last['Low10']; low20=last['Low20']
        close=last['Close']; open_today=last['Open']; prev_close=prev['Close']
        rsi_v=last['RSI14']; adx_v=last['ADX14']; val20=last['AvgVal20']; gap=(open_today/prev_close-1)*100 if prev_close else 0
        is_mom = t in CORE_MOMENTUM
        buy = (close>high55) and (val20>=1e9) and (abs(gap)<5)
        if not is_mom:
            buy = buy and (adx_v>25) and (50 <= rsi_v <= 75) and (last['+DI']>last['-DI'])
        sell_low = low20 if is_mom else low10
        sell = close < sell_low
        signal = "BUY" if buy else "SELL" if sell else "HOLD"
        action = "Beli Open Besok" if buy else "Jual Open Besok" if sell else "Hold"
        signals.append({"Ticker":t.replace('.JK',''), "Ticker_GF":t, "Close":round(close,0), "High55":round(high55,0), "Low":round(sell_low,0), "RSI14":round(rsi_v,1), "ADX14":round(adx_v,1), "AvgVal20_Miliar":round(val20/1e9,2), "Gap%":round(gap,2), "Signal":signal, "Action_Besok":action, "Type":"MOMENTUM" if is_mom else "TREND", "Last_Update":pd.Timestamp.now(tz='Asia/Jakarta').strftime('%Y-%m-%d %H:%M WIB')})
    except Exception as e:
        print(t,e)

df_signals=pd.DataFrame(signals).sort_values("Signal", ascending=False)
df_signals.to_csv("signals_today.csv", index=False)
print(df_signals.to_string(index=False))
print(f"\nSaved signals_today.csv - {len(df_signals)} rows")

# Push to Google Sheets
try:
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID)
    try:
        ws = sheet.worksheet("LIVE_SIGNALS")
    except:
        ws = sheet.add_worksheet(title="LIVE_SIGNALS", rows=100, cols=20)
    ws.clear()
    set_with_dataframe(ws, df_signals)
    print(f"Pushed to Google Sheets: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
except Exception as e:
    print(f"Sheets push failed (maybe secrets not set): {e}")
    print("But CSV is saved - you can upload manually to dashboard")