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

# Custom CSS Styles for Modern UI
st.markdown(
    """
    <style>
    .main {
        background-color: #0b0f19;
    }
    .stApp {
        background-color: #0b0f19;
        color: #ffffff;
    }
    .title-text {
        text-align: center;
        color: #f0f2f6;
        font-weight: 800;
        margin-bottom: 25px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
    }
    .live-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(244, 63, 94, 0.2);
        border: 2px solid #f43f5e;
        margin-bottom: 25px;
    }
    .live-title {
        color: #f43f5e;
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
        text-shadow: 0 0 20px rgba(244,63,94,0.6);
    }
    .update-time {
        color: #a7a9be;
        font-size: 15px;
        font-weight: 500;
        margin-top: 5px;
    }
    /* Lucky Numbers Styling */
    .lucky-section {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 2px solid #8b5cf6;
        border-radius: 20px;
        padding: 25px;
        margin-top: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(139, 92, 246, 0.2);
    }
    .lucky-title {
        color: #c084fc;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }
    .number-badge-main {
        background: linear-gradient(135deg, #f43f5e, #be123c);
        color: white;
        padding: 12px 10px;
        border-radius: 15px;
        font-size: 28px;
        font-weight: 900;
        text-align: center;
        box-shadow: 0 5px 15px rgba(244, 63, 94, 0.4);
        border: 2px solid #fda4af;
    }
    .number-badge-sub {
        background: rgba(30, 41, 59, 0.8);
        color: #e2e8f0;
        padding: 12px 10px;
        border-radius: 12px;
        font-size: 20px;
        font-weight: 700;
        text-align: center;
        border: 1px solid #475569;
    }
    .stButton>button {
        width: 100%;
        background-color: #f43f5e;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #e11d48;
        color: #ffffff;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ခေါင်းစဉ်နှင့် ဖန်တီးသူအမှတ်အသား
st.markdown(
    "<h3 class='title-text'>Myanmar 2D Live Tracker</h3>",
    unsafe_allow_html=True,
)

# ၁။ Auto-refresh (၁၅ စက္ကန့်တစ်ကြိမ်)
count = st_autorefresh(
    interval=15000, limit=None, key="modern_ui_autorefresh_key_v2"
)

# ၂။ Database ချိတ်ဆက်ခြင်းနှင့် Tables ဆောက်ခြင်း
conn = sqlite3.connect("my_2d_log.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS number_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        live_data TEXT
    )
""")

# Lucky Numbers အတွက် Table အသစ်
cursor.execute("""
    CREATE TABLE IF NOT EXISTS lucky_numbers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        n1 TEXT,
        n2 TEXT,
        n3 TEXT,
        n4 TEXT,
        n5 TEXT
    )
""")
conn.commit()

# Default Lucky Numbers ထည့်သွင်းခြင်း (မရှိသေးမှသာ)
cursor.execute("SELECT COUNT(*) FROM lucky_numbers")
if cursor.fetchone()[0] == 0:
  cursor.execute(
      "INSERT INTO lucky_numbers (n1, n2, n3, n4, n5) VALUES (?, ?, ?, ?, ?)",
      ("00", "00", "00", "00", "00"),
  )
  conn.commit()


# ၃။ API မှ ဒေတာဆွဲယူပြီး Database သို့ သိမ်းမည့် ဖန်ရှင်
def fetch_and_log_json_api():
  # (မူလ သင့် API URL ဒါမှမဟုတ် dict ကို ဤနေရာတွင် ထည့်သွင်းနိုင်သည်)
  api_data = {
      "live": {"set": "1,626.27", "value": "85,650.24", "twod": "70"}
  }
  try:
    live_number = str(api_data.get("live", {}).get("twod", ""))
    if live_number and len(live_number) == 2:
      myanmar_tz = timezone(timedelta(hours=6, minutes=30))
      current_time = datetime.now(myanmar_tz).strftime("%Y-%m-%d %I:%M:%S %p")

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

# ၄။ UI Display - လက်ရှိ Live ဂဏန်းပြသရန် Card
cursor.execute(
    "SELECT timestamp, live_data FROM number_logs ORDER BY id DESC LIMIT 1"
)
latest_data = cursor.fetchone()

display_num = latest_data[1] if latest_data else "--"

if latest_data and latest_data[0]:
  try:
    dt_obj = datetime.strptime(latest_data[0], "%Y-%m-%d %H:%M:%S")
    display_time = dt_obj.strftime("%Y-%m-%d %I:%M:%S %p")
  except:
    display_time = latest_data[0]
else:
  display_time = "ဒေတာ မရှိသေးပါ"

st.markdown(
    f"""
    <div class="live-card">
        <div class="live-title">Live 2D Result</div>
        <div class="live-number">{display_num}</div>
        <div class="update-time">Updated: {display_time}</div>
    </div>
""",
    unsafe_allow_html=True,
)

# လက်ဖြင့် ချက်ချင်းဒေတာဆွဲရန် ခလုတ်
if st.button("ဒေတာအသစ် ချက်ချင်းရယူရန်"):
  fetch_and_log_json_api()
  st.rerun()

# ---------------------------------------------------------
# ၅။ LUCKY NUMBERS FOR YOU SECTION (Admin 5 ဃဏန်း)
# ---------------------------------------------------------


def get_lucky_numbers():
  cursor.execute("SELECT n1, n2, n3, n4, n5 FROM lucky_numbers WHERE id=1")
  return cursor.fetchone()


current_nums = get_lucky_numbers()

st.markdown(
    """
    <div class="lucky-section">
        <div class="lucky-title"> Lucky Numbers For You </div>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
  st.markdown(
      f'<div class="number-badge-main"><br>{current_nums[0]}</div>',
      unsafe_allow_html=True,
  )
  st.caption("မိန်း (၁)")
with col2:
  st.markdown(
      f'<div class="number-badge-main"><br>{current_nums[1]}</div>',
      unsafe_allow_html=True,
  )
  st.caption("မိန်း (၂)")
with col3:
  st.markdown(
      f'<div class="number-badge-sub">{current_nums[2]}</div>',
      unsafe_allow_html=True,
  )
  st.caption("အထောက်")
with col4:
  st.markdown(
      f'<div class="number-badge-sub">{current_nums[3]}</div>',
      unsafe_allow_html=True,
  )
  st.caption("အထောက်")
with col5:
  st.markdown(
      f'<div class="number-badge-sub">{current_nums[4]}</div>',
      unsafe_allow_html=True,
  )
  st.caption("အထောက်")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# ၆။ ADMIN PANEL FOR LUCKY NUMBERS
# ---------------------------------------------------------
with st.expander(" Admin Panel (Lucky Numbers ထည့်ရန်)"):
  admin_pass = st.text_input("Admin Password ထည့်ပါ", type="password")

  if admin_pass == "mingalarpar":
    st.success("Admin Password မှန်ကန်ပါသည်။ ဂဏန်းများ ပြောင်းလဲနိုင်ပါပြီ။")

    with st.form("admin_form"):
      col_a, col_b, col_c, col_d, col_e = st.columns(5)
      with col_a:
        new_n1 = st.text_input(
            "မိန်း (၁)", value=current_nums[0], max_chars=2
        )
      with col_b:
        new_n2 = st.text_input(
            "မိန်း (၂)", value=current_nums[1], max_chars=2
        )
      with col_c:
        new_n3 = st.text_input("နံပါတ် ၃", value=current_nums[2], max_chars=2)
      with col_d:
        new_n4 = st.text_input("နံပါတ် ၄", value=current_nums[3], max_chars=2)
      with col_e:
        new_n5 = st.text_input("နံပါတ် ၅", value=current_nums[4], max_chars=2)

      submit_btn = st.form_submit_button(" သိမ်းဆည်းမည်")

      if submit_btn:
        cursor.execute(
            "UPDATE lucky_numbers SET n1=?, n2=?, n3=?, n4=?, n5=? WHERE id=1",
            (new_n1, new_n2, new_n3, new_n4, new_n5),
        )
        conn.commit()
        st.success("ဂဏန်းများ အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ!")
        st.rerun()

  elif admin_pass != "":
    st.error("Password မှားယွင်းနေပါသည်။")

st.markdown("---")

# ၇။ ဒေတာများကို ဝဘ်ဆိုဒ်ပေါ်တွင် ပြသခြင်း (Tabs ဖြင့် ခွဲထုတ်ခြင်း)
tab1, tab2 = st.tabs(["စာရင်းဇယား (History)", "ရာခိုင်နှုန်း ခွဲခြမ်းစိတ်ဖြာမှု"])

with tab1:
  st.subheader("မှတ်တမ်းဇယား")
  df = pd.read_sql("SELECT * FROM number_logs ORDER BY id DESC", conn)
  if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
  else:
    st.info("လောလောဆယ် ဒေတာ မရှိသေးပါ။")

with tab2:
  st.subheader("ဂဏန်းကျရောက်မှု ရာခိုင်နှုန်းများ")
  df = pd.read_sql("SELECT * FROM number_logs ORDER BY id DESC", conn)
  if not df.empty:
    total_count = len(df)
    counts = df["live_data"].value_counts()

    for num, count in counts.items():
      percentage = (count / total_count) * 100
      st.markdown(f"""
            - ဂဏန်း **{num}**: **{count}** ကြိမ် ကျရောက် (ရာခိုင်နှုန်း: **{percentage:.2f}%**)
            """)
  else:
    st.info("ရာခိုင်နှုန်း တွက်ချက်ရန် ဒေတာ မရှိသေးပါ။")
