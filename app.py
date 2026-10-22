from datetime import datetime, timedelta, timezone
import json
import sqlite3
import urllib.request
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ခေါင်းစဉ်နှင့် ဖန်တီးသူအမှတ်အသား
st.markdown(
    "<h3 style='text-align: center; color: gray;'>ဆရာထွန်း၏ဖန်တီးမှု</h3>",
    unsafe_allow_html=True,
)
st.title(" Myanmar 2D Live Tracker (JSON API)")

# ၁။ Auto-refresh (၁၅ စက္ကန့်တစ်ကြိမ်)
count = st_autorefresh(
    interval=15000, limit=None, key="json_api_autorefresh_key"
)

# ၂။ Database ချိတ်ဆက်ခြင်းနှင့် Table ဆောက်ခြင်း
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


# ၃။ API မှ ဒေတာဆွဲယူပြီး Database သို့ သိမ်းမည့် ဖန်ရှင်
def fetch_and_log_json_api():
  # သင့်ရဲ့ တကယ့် API Endpoint လိပ်စာကို ဤနေရာတွင် ထည့်ပါ
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

      # JSON ထဲရှိ 'live' အောက်မှ 'twod' ဂဏန်းကို တိုက်ရိုက်ဆွဲထုတ်ခြင်း
      live_number = str(res_data.get("live", {}).get("twod", ""))

      if live_number and len(live_number) == 2:
        myanmar_tz = timezone(timedelta(hours=6, minutes=30))
        current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Database ထဲတွင် နောက်ဆုံးဂဏန်းနှင့် တူမတူ စစ်ဆေးခြင်း
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


# အလိုအလျောက် ဒေတာဆွဲမည်
fetch_and_log_json_api()

# လက်ဖြင့် ချက်ချင်းဒေတာဆွဲရန် ခလုတ်
if st.button(" ဒေတာအသစ် ချက်ချင်းရယူရန်", key="json_fetch_btn"):
  fetch_and_log_json_api()
  st.rerun()

# ၄။ ဒေတာများကို ဝဘ်ဆိုဒ်ပေါ်တွင် ပြသခြင်း
st.subheader(" ဂဏန်းကျရောက်မှု စာရင်းဇယား")

df = pd.read_sql("SELECT * FROM number_logs ORDER BY id DESC", conn)

if not df.empty:
  st.dataframe(df, use_container_width=True)

  st.subheader(" ရာခိုင်နှုန်း တွက်ချက်မှုများ")
  total_count = len(df)
  counts = df["live_data"].value_counts()

  for num, count in counts.items():
    percentage = (count / total_count) * 100
    st.write(
        f"- ဂဏန်း **{num}**: {count} ကြိမ် ကျ (ရာခိုင်နှုန်း: **{percentage:.2f}%**)"
    )
else:
  st.info("လောလောဆယ် ဒေတာ မရှိသေးပါ။")
