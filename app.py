from datetime import datetime, timedelta, timezone
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
st.title(" Myanmar 2D History Tracker")

# ၁။ Auto-refresh (၁၅ စက္ကန့်တစ်ကြိမ်)
count = st_autorefresh(
    interval=15000, limit=None, key="history_autorefresh_key"
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


# ၃။ ဇယားကွက် (History Table) ထဲမှ ဒေတာများကို တိုက်ရိုက်ဆွဲယူမည့် ဖန်ရှင်
def fetch_and_log_history():
  # History စာမျက်နှာ လိပ်စာ (သို့မဟုတ် ပင်မစာမျက်နှာ)
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

      myanmar_tz = timezone(timedelta(hours=6, minutes=30))
      current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %H:%M:%S")

      # ဇယားကွက် (Table rows) သို့မဟုတ် ကတ်ပြားများထဲမှ ဂဏန်းများကို ရှာဖွေခြင်း
      # ပုံထဲတွင် ညာဘက်အစွန်ဆုံးကဆဲလ်များတွင် 2D ဂဏန်းများ ပါရှိသည်
      rows = soup.find_all("tr")
      for row in rows:
        cols = row.find_all(["td", "th"])
        if cols and len(cols) >= 4:
          potential_number = cols[-1].text.strip()
          if potential_number.isdigit() and len(potential_number) == 2:
            # တွေ့ရှိသော ဂဏန်းကို Database ထဲသို့ ထည့်ရန် စစ်ဆေးမည်
            cursor.execute(
                "SELECT live_data FROM number_logs ORDER BY id DESC LIMIT 1"
            )
            last_row = cursor.fetchone()

            if not last_row or last_row[0] != potential_number:
              cursor.execute(
                  "INSERT INTO number_logs (timestamp, live_data) VALUES (?,"
                  " ?)",
                  (current_time, potential_number),
              )
              conn.commit()

      # အကယ်၍ HTML table tag မမိပါက ပင်မထိပ်ဆုံးဂဏန်းကို ယူမည်
      top_number_tag = soup.find(["h1", "h2", "div"])
      if top_number_tag:
        text = top_number_tag.text.strip()
        if text.isdigit() and len(text) == 2:
          cursor.execute(
              "SELECT live_data FROM number_logs ORDER BY id DESC LIMIT 1"
          )
          last_row = cursor.fetchone()
          if not last_row or last_row[0] != text:
            cursor.execute(
                "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
                (current_time, text),
            )
            conn.commit()

  except Exception as e:
    pass


# အလိုအလျောက် ဒေတာဆွဲမည်
fetch_and_log_history()

# လက်ဖြင့် ချက်ချင်းဒေတာဆွဲရန် ခလုတ်
if st.button(" ဒေတာအသစ် ချက်ချင်းရယူရန်", key="history_fetch_btn"):
  fetch_and_log_history()
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
