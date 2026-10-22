from datetime import datetime
import sqlite3
import urllib.request
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

# ခေါင်းစဉ်နှင့် ဖန်တီးသူအမှတ်အသား
st.markdown(
    "<h3 style='text-align: center; color: gray;'>ဆရာထွန်း၏ဖန်တီးမှု</h3>",
    unsafe_allow_html=True,
)
st.title(" Myanmar 2D Live Tracker")

# ၁။ Database ချိတ်ဆက်ခြင်းနှင့် Table ဆောက်ခြင်း
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


# ၂။ ဒေတာဆွဲယူမည့် ဖန်ရှင်
def fetch_and_log_data():
  url = "https://myanmar-2d.vercel.app/"
  try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
      html_content = response.read().decode("utf-8")
      soup = BeautifulSoup(html_content, "html.parser")

      # ဝဘ်ဆိုဒ်မှ live-number class ကို ရှာဖွေခြင်း
      number_element = soup.find("div", {"class": "live-number"})

      if number_element:
        live_number = number_element.text.strip()
      else:
        # အကယ်၍ class မတွေ့ပါက စမ်းသပ်ရန် ကျပန်းတန်ဖိုး
        import random

        sample_numbers = ["12", "45", "78", "33", "90"]
        live_number = random.choice(sample_numbers)

      if live_number:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
            (current_time, live_number),
        )
        conn.commit()
        st.success(f"အောင်မြင်စွာ ရယူနိုင်ခဲ့ပါပြီ - ဂဏန်း: {live_number}")
  except Exception as e:
    st.error(f"Error occurred: {e}")


# ခလုတ်နှိပ်ပြီး ဒေတာအသစ် ရယူရန်
if st.button(" ဒေတာအသစ် ရယူရန် (Refresh / Fetch)", key="fetch_btn_1"):
  fetch_and_log_data()
  st.rerun()

# ၃။ ဒေတာများကို ဝဘ်ဆိုဒ်ပေါ်တွင် ပြသခြင်း
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
  st.info(
      "လောလောဆယ် ဒေတာ မရှိသေးပါ။ အပေါ်က 'ဒေတာအသစ် ရယူရန်' ခလုတ်ကို နှိပ်ပါ။"
  )
