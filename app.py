import streamlit as st

# ဖန်တီးသူ အမှတ်အသား စာသားထည့်ရန်
st.markdown(
    "###  ဆရာချီး၏ဖန်တီးမှု "
)  # အရွယ်အစား လိုသလို ကြီးငယ်ညှိနိုင်ပါတယ်

st.title(" Myanmar 2D Live Tracker")

from datetime import datetime
import sqlite3
import urllib.request
import pandas as pd
import streamlit as st


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


# from datetime import datetime
import sqlite3
import urllib.request
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup  # BeautifulSoup ကို တင်သွင်းရန် (အပေါ်ဆုံးတွင် ရှိရပါမည်)

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


# ၂။ ဒေတာအစစ် အမှန်တကယ် သွားယူမည့် ဖန်ရှင် (ဤနေရာတွင် အစားထိုးပါ)
def fetch_and_log_data():
  url = "https://myanmar-2d.vercel.app/"
  try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
      html_content = response.read().decode("utf-8")

      # BeautifulSoup ကိုသုံး၍ HTML ထဲမှ ဒေတာများကို ရှာဖွေခြင်း
      soup = BeautifulSoup(html_content, "html.parser")

      #  အရေးကြီးချက် - ယူလိုသည့် ဝဘ်ဆိုဒ်၏ HTML Tag/Class ပုံစံအပေါ်မူတည်၍ ပြင်ဆင်ရပါမည်။
      # (လက်ရှိ ဥပမာအနေဖြင့် div class="live-number" ကို ရှာထားခြင်း ဖြစ်သည်)
      number_element = soup.find("div", {"class": "live-number"})

      if number_element:
        live_number = number_element.text.strip()
      else:
        live_number = "မတွေ့ရပါ"

      # တကယ်လို့ ဂဏန်း အမှန်တကယ် ရရှိခဲ့ပါက Database ထဲသို့ ထည့်မည်
      if live_number and live_number != "မတွေ့ရပါ":
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
            (current_time, live_number),
        )
        conn.commit()
        st.success(f"အောင်မြင်စွာ ရယူနိုင်ခဲ့ပါပြီ - ဂဏန်း: {live_number}")
      else:
        st.warning(
            "ဝဘ်ဆိုဒ်မှ ဂဏန်းအချက်အလက်ကို တိုက်ရိုက် မဖတ်ယူနိုင်သေးပါ။ (Tag"
            " ပုံစံ စစ်ဆေးရန် လိုအပ်သည်)"
        )

  except Exception as e:
    st.error(f"Error occurred: {e}")


# ခလုတ်နှိပ်ပြီး ဒေတာအသစ် ရယူရန်
if st.button(" ဒေတာအသစ် ရယူရန် (Refresh / Fetch)"):
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



# ခလုတ်နှိပ်ပြီး ဒေတာအသစ် ရယူရန်
if st.button(" ဒေတာအသစ် ရယူရန် (Refresh / Fetch)"):
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
