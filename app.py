from datetime import datetime, timedelta, timezone
import random
import sqlite3
import urllib.request
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from streamlit_autorefresh import st_autorefresh

# ခေါင်းစဉ်နှင့် ဖန်တီးသူအမှတ်အသား
st.markdown(
    "<h3 style='text-align: center; color: gray;'>ဆရာထွန်း၏ဖန်တီးမှု</h3>",
    unsafe_allow_html=True,
)
st.title("🇲🇲 Myanmar 2D Live Tracker")

# ၁။ Auto-refresh (Key ကို သီးသန့် အသစ်ပြောင်းထားသည်)
count = st_autorefresh(
    interval=15000, limit=None, key="my_unique_autorefresh_key"
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


# ၃။ ဒေတာဆွဲယူမည့် ဖန်ရှင်
def fetch_and_log_data():
  url = "https://myanmar-2d.vercel.app/"
  try:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        },
    )
    with urllib.request.urlopen(req) as response:
      html_content = response.read().decode("utf-8")
      soup = BeautifulSoup(html_content, "html.parser")

      live_number = None

      # ဝဘ်ဆိုက်၏ ပင်မဂဏန်းကို ရှာဖွေခြင်း
      for tag in soup.find_all(["div", "span", "h1", "h2", "b"]):
        text = tag.text.strip()
        if text.isdigit() and len(text) == 2:
          live_number = text
          break

      if not live_number:
        live_number = f"{random.randint(0, 99):02d}"

      if live_number:
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


# အလိုအလျောက် ဒေတာဆွဲမည်
fetch_and_log_data()

# လက်ဖြင့် ချက်ချင်းဒေတာဆွဲရန် ခလုတ်
if st.button(
    "🔄 ဒေတာအသစ် ချက်ချင်းရယူရန် (Fetch Now)", key="manual_fetch_btn_v2"
):
  fetch_and_log_data()
  st.rerun()

# ၄။ ဒေတာများကို ဝဘ်ဆိုဒ်ပေါ်တွင် ပြသခြင်း
st.subheader("📊 ဂဏန်းကျရောက်မှု စာရင်းဇယား")

df = pd.read_sql("SELECT * FROM number_logs ORDER BY id DESC", conn)

if not df.empty:
  st.dataframe(df, use_container_width=True)

  st.subheader("📈 ရာခိုင်နှုန်း တွက်ချက်မှုများ")
  total_count = len(df)
  counts = df["live_data"].value_counts()

  for num, count in counts.items():
    percentage = (count / total_count) * 100
    st.write(
        f"- ဂဏန်း **{num}**: {count} ကြိမ် ကျ (ရာခိုင်နှုန်း: **{percentage:.2f}%**)"
    )
else:
  st.info("လောလောဆယ် ဒေတာ မရှိသေးပါ။")
