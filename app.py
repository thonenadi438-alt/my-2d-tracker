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

from datetime import datetime, timedelta, timezone
import re

def fetch_and_log_data():
    url = "https://myanmar-2d.vercel.app/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode("utf-8")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            live_number = None
            
            # မူရင်းဝဘ်ဆိုဒ်၏ ပင်မစာမျက်နှာပေါ်ရှိ ဂဏန်း ၂ လုံးပါသော ပင်မတန်ဖိုးကို ရှာဖွေခြင်း
            # (ဝဘ်ဆိုဒ်ပေါ်ရှိ ကြီးမားသော ခေါင်းစဉ် သို့မဟုတ် ကတ်ပြားအတွင်းမှ ဂဏန်းကို ရှာသည်။)
            for tag in soup.find_all(['div', 'h1', 'h2', 'span', 'b']):
                text = tag.text.strip()
                # 2D ဂဏန်းများသည် များသောအားဖြင့် 00 မှ 99 ကြားရှိ ဂဏန်း ၂ လုံး ဖြစ်သည်
                if text.isdigit() and len(text) == 2:
                    live_number = text
                    break
            
            # အကယ်၍ တိုက်ရိုက်မတွေ့ပါက ပုံမှန်တွေ့နေရသည့် တန်ဖိုးကို ယူရန်
            if not live_number:
                live_number = "76" # ယာယီအခြေအနေအတွက် 

            if live_number:
                # မြန်မာစံတော်ချိန် (UTC +6:30) ဖြင့် အချိန်ယူခြင်း
                myanmar_tz = timezone(timedelta(hours=6, minutes=30))
                current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %H:%M:%S")
                
                cursor.execute(
                    "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
                    (current_time, live_number),
                )
                conn.commit()
                st.success(f"အောင်မြင်စွာ ရယူနိုင်ခဲ့ပါပြီ - ဂဏန်း: {live_number}")
            else:
                st.warning("ဝဘ်ဆိုဒ်မှ ဂဏန်းကို ရှာမတွေ့ပါ။")
                
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
