from datetime import datetime, timedelta, timezone
import sqlite3
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ခေါင်းစဉ်နှင့် ဖန်တီးသူအမှတ်အသား
st.markdown(
    "<h3 style='text-align: center; color: gray;'>ဆရာထွန်း၏ဖန်တီးမှု</h3>",
    unsafe_allow_html=True,
)
st.title(" Myanmar 2D Live Tracker")

# ၁။ Auto-refresh (၁၅ စက္ကန့်တစ်ကြိမ်)
count = st_autorefresh(interval=15000, limit=None, key="autorefresh_v4")

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

# ၃။ တိုက်ရိုက် ဂဏန်းအသစ် ထည့်သွင်းနိုင်မည့် ဖောင် (Manual Input & Auto Save)
st.subheader(" ဂဏန်းအသစ် မှတ်တမ်းတင်ရန်")
with st.form("manual_entry_form"):
  col1, col2 = st.columns([2, 1])
  with col1:
    input_number = st.text_input(
        "လက်ရှိထွက်နေသော ဂဏန်း (ဥပမာ - 87)", max_chars=2
    )
  with col2:
    st.write("")
    st.write("")
    submit_btn = st.form_submit_button(" သိမ်းမည်")

if submit_btn and input_number:
  if input_number.isdigit() and len(input_number) == 2:
    myanmar_tz = timezone(timedelta(hours=6, minutes=30))
    current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %H:%M:%S")

    # နောက်ဆုံးထည့်ထားတဲ့ ဂဏန်းနဲ့ တူစစ်မယ်
    cursor.execute("SELECT live_data FROM number_logs ORDER BY id DESC LIMIT 1")
    last_row = cursor.fetchone()

    if not last_row or last_row[0] != input_number:
      cursor.execute(
          "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
          (current_time, input_number),
      )
      conn.commit()
      st.success(f"ဂဏန်း {input_number} ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
    else:
      st.warning("ဤဂဏန်းမှာ နောက်ဆုံးထည့်ထားသော ဂဏန်းနှင့် တူနေပါသည်။")
  else:
    st.error("ကျေးဇူးပြု၍ ဂဏန်း ၂ လုံးတိတိ (ဥပမာ - 05, 87) ထည့်ပါ။")

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
  st.info("လောလောဆယ် ဒေတာ မရှိသေးပါ။ အထက်ပါဖောင်တွင် ဂဏန်းထည့်၍ စမ်းပါ။")
