from datetime import datetime, timedelta, timezone
import json
import sqlite3
import urllib.request
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# Page Configuration
st.set_page_config(
    page_title="Myanmar 2D Live Tracker", page_icon="", layout="centered"
)

# Custom CSS Styles for Modern UI (UI ဒီဇိုင္း အလန္းစားမ်ား)
st.markdown("""
    <style>
    /* Main Background & Font */
    .main {
        background-color: #0e1117;
    }
    /* Header Style */
    .title-text {
        text-align: center;
        color: #f0f2f6;
        font-weight: 800;
        margin-bottom: 25px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    /* Live Card Style */
    .live-card {
        background: linear-gradient(135deg, #1f4068 0%, #162447 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        border: 2px solid #e43f5a;
        margin-bottom: 25px;
    }
    .live-title {
        color: #e43f5a;
        font-size: 20px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .live-number {
        color: #ffffff;
        font-size: 80px;
        font-weight: 900;
        margin: 10px 0;
        text-shadow: 0 0 20px rgba(228,63,90,0.6);
    }
    .update-time {
        color: #a7a9be;
        font-size: 14px;
    }
    /* Button Styling */
    .stButton>button {
        width: 100%;
        background-color: #e43f5a;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #d92027;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# ေခါင္းစဥ္ႏွင့္ ဖန္တီးသူအမွတ္အသား
st.markdown(
    "<h3 class='title-text'> Myanmar 2D Live Tracker</h3>",
    unsafe_allow_html=True,
)

# ၁။ Auto-refresh (၁၅ စက္န႔္တစ္ႀကိမ္)
count = st_autorefresh(
    interval=15000, limit=None, key="modern_ui_autorefresh_key"
)

# ၂။ Database ခ်ိတ္ဆက္ျခင္းႏွင့္ Table ေဆာက္ျခင္း
conn = sqlite3.connect("my_2d_log.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS number_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        live_data TEXT
    )
""")
conn.commit()


# ၃။ API မွ ေဒတာဆြဲယူၿပီး Database သို႔ သိမ္းမည့္ ဖန္ရွင္
def fetch_and_log_json_api():
  api_url = {
  "live": {
    "set": "1,626.27",
    "value": "85,650.24",
    "time": "2021-11-04 16:12:40",
    "twod": "70"
  },
"result": [
    {
      "set": "1,623.03",
      "value": "42,311.39",
      "open_time": "11:00:00",
      "twod": "31"
    },
    {
      "set": "1,621.55",
      "value": "53,762.32",
      "open_time": "12:01:00",
      "twod": "52"
    },
    {
      "set": "1,622.37",
      "value": "67,016.57",
      "open_time": "15:00:00",
      "twod": "76"
    },
    {
      "set": "1,626.27",
      "value": "85,650.24",
      "open_time": "16:30:00",
      "twod": "70"
    }
  ]
}
  try:
    req = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        },
    )
    with urllib.request.urlopen(req) as response:
      res_data = json.loads(response.read().decode("utf-8"))
      live_number = str(res_data.get("live", {}).get("twod", ""))

      if live_number and len(live_number) == 2:
        myanmar_tz = timezone(timedelta(hours=6, minutes=30))
        current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "SELECT live_data FROM number_logs ORDER BY id DESC LIMIT 1"
        )
        last_row = cursor.fetchone()

        if not last_row or last_row[0] != live_number:
          cursor.execute(
              "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
              (current_time, live_number),
          )
          conn.commit()
  except Exception as e:
    pass


# အလိုအေလ်ာက္ ေဒတာဆြဲမည္
fetch_and_log_json_api()

# ၄။ UI Display - လက္ရွိ Live ဂဏန္းျပသရန္ Card အလန္းစား
cursor.execute("SELECT timestamp, live_data FROM number_logs ORDER BY id DESC LIMIT 1")
latest_data = cursor.fetchone()

display_num = latest_data[1] if latest_data else "--"
display_time = (
    latest_data[0] if latest_data else "ေဒတာ မရွိေသးပါ"
)

st.markdown(
    f"""
    <div class="live-card">
        <div class="live-title"> Live 2D Result</div>
        <div class="live-number">{display_num}</div>
        <div class="update-time"> Updated: {display_time}</div>
    </div>
""",
    unsafe_allow_html=True,
)

# လက္ျဖင့္ ခ်က္ခ်င္းေဒတာဆြဲရန္ ခလုတ္
if st.button(" ေဒတာအသစ္ ခ်က္ခ်င္းရယူရန္"):
  fetch_and_log_json_api()
  st.rerun()

st.markdown("---")

# ၅။ ေဒတာမ်ားကို ဝဘ္ဆိုဒ္ေပၚတြင္ ျပသျခင္း (Tabs ျဖင့္ ခြဲထုတ္ျခင္း)
tab1, tab2 = st.tabs([" စာရင္းဇယား (History)", " ရာခိုင္ႏႈန္း ခြဲျခမ္းစိတ္ျဖာမႈ"])

with tab1:
  st.subheader(" မွတ္တမ္းဇယား")
  df = pd.read_sql("SELECT * FROM number_logs ORDER BY id DESC", conn)
  if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
  else:
    st.info("ေလာေလာဆယ္ ေဒတာ မရွိေသးပါ။")

with tab2:
  st.subheader(" ဂဏန္းက်ေရာက္မႈ ရာခိုင္ႏႈန္းမ်ား")
  if not df.empty:
    total_count = len(df)
    counts = df["live_data"].value_counts()

    for num, count in counts.items():
      percentage = (count / total_count) * 100
      st.markdown(f"""
            - ဂဏန္း **{num}**: **{count}** ႀကိမ္ က်ေရာက္ (ရာခိုင္ႏႈန္း: **{percentage:.2f}%**)
            """)
  else:
    st.info("ရာခိုင္ႏႈန္း တြက္ခ်က္ရန္ ေဒတာ မရွိေသးပါ။")
