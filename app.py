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
st.title(" Myanmar 2D Live Tracker (Auto)")

# ၁။ ၁၅ စက္ကန့်တစ်ကြိမ် အလိုအလျောက် Refresh လုပ်ရန်
count = st_autorefresh(interval=15000, limit=None, key="auto_fetch_counter")

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
st.title(" Myanmar 2D Live Tracker (Auto)")

# ၁။ ၁၅ စက္ကန့်တစ်ကြိမ် အလိုအလျောက် Refresh လုပ်ရန်
count = st_autorefresh(interval=15000, limit=None, key="auto_fetch_counter")

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


# ၃။ ဒေတာဆွဲယူမည့် ဖန်ရှင် (ပင်မဂဏန်းအကြီးကို တိကျစွာဆွဲရန်)
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

      # နည်းလမ်း - ဝဘ်ဆိုက်၏ ပင်မထိပ်ဆုံးကတ်ပြား (Blue Card) အတွင်းရှိ ကြီးမားသော ဂဏန်း ၂ လုံးကို ရှာဖွေခြင်း
      #  ပင်မဂဏန်းသည် ပထမဆုံးတွေ့ရသော သို့မဟုတ် အကြီးဆုံးဖောင့်ရှိသော ဂဏန်းဖြစ်သည်
      for tag in soup.find_all(["div", "span", "h1", "h2", "b"]):
        text = tag.text.strip()
        # ဂဏန်း ၂ လုံးတိတိ ဖြစ်ရမည် (ဥပမာ - 87)
        if text.isdigit() and len(text) == 2:
          live_number = text
          break  # ပထမဆုံးတွေ့သည့် ပင်မဂဏန်းကို ယူပြီး ရပ်မည်

      if live_number:
        myanmar_tz = timezone(timedelta(hours=6, minutes=30))
        current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %H:%M:%S")

        # Database ထဲသို့ နောက်ဆုံးအကြိမ်က ဝင်ထားသော ဂဏန်းနှင့် တူညီမှသာ (သို့မဟုတ် အသစ်ဖြစ်မှသာ) ထည့်ရန် စစ်ဆေးခြင်း
        cursor.execute(
            "SELECT live_data FROM number_logs ORDER BY id DESC LIMIT 1"
        )
        last_row = cursor.fetchone()

        # တကယ်လို့ နောက်ဆုံးဂဏန်းနဲ့ မတူတော့ဘူး (သို့မဟုတ် ဇယား က လွတ်နေတယ်) မှသာ အသစ်ထည့်မည်
        if not last_row or last_row[0] != live_number:
          cursor.execute(
              "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
              (current_time, live_number),
          )
          conn.commit()
  except Exception as e:
    pass


# Auto-refresh ဖြစ်တိုင်း ဒေတာဆွဲမည်
fetch_and_log_data()

# လက်ဖြင့် ချက်ချင်းဒေတာဆွဲရန် ခလုတ်
if st.button(" ဒေတာအသစ် ချက်ချင်းရယူရန် (Fetch Now)", key="manual_fetch_btn"):
  fetch_and_log_data()
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
  st.info("လောလောဆယ် ဒေတာ မရှိသေးပါ။ ခလုတ်ကို နှိပ်၍ စမ်းပါ။")


# Auto-refresh ဖြစ်တိုင်း ဒေတာဆွဲမည်
fetch_and_log_data()

# လက်ဖြင့် ချက်ချင်းဒေတာဆွဲရန် ခလုတ်
if st.button(" ဒေတာအသစ် ချက်ချင်းရယူရန် (Fetch Now)", key="manual_fetch_btn"):
  fetch_and_log_data()
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
  st.info("လောလောဆယ် ဒေတာ မရှိသေးပါ။ ခလုတ်ကို နှိပ်၍ စမ်းပါ။")
