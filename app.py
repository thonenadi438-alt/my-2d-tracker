import sqlite3

# Database ချိတ်ဆက်ခြင်းနှင့် Table အလိုအလျောက်ဆောက်ခြင်း
conn = sqlite3.connect("my_2d_log.db", check_same_thread=False)
cursor = conn.cursor()

# number_logs ဆိုတဲ့ ဇယားမရှိသေးရင် အသစ်ဆောက်မည်
cursor.execute("""
    CREATE TABLE IF NOT EXISTS number_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        live_number TEXT
    )
""")
conn.commit()
from datetime import datetime
import sqlite3
import time
import urllib.request

# ၁။ ဒေတာသိမ်းထားသော Database နှင့် ချိတ်ဆက်ခြင်း
conn = sqlite3.connect("my_2d_log.db")
cursor = conn.cursor()


# ၂. ဝဘ်ဆိုဒ်ဆီကနေ ဒေတာသွားယူမယ့် ဖန်ရှင်
def fetch_website_data():
  try:
    url = "https://myanmar-2d.vercel.app/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
      html_content = response.read().decode("utf-8")

      #  မှတ်ချက်။ ။ အကယ်၍ တကယ့်ဝဘ်ဆိုဒ်ထဲက ကိန်းဂဏန်းအစစ် (ဥပမာ '54' သို့မဟုတ် '83') ကို
      # တိတိကျကျ ဖြတ်ထုတ်ယူနိုင်ပြီဆိုပါက ဤနေရာတွင် ထိုဂဏန်းအစစ်ကို ထည့်ရပါမည်။
      # လောလောဆယ် စမ်းသပ်ရန် ကျပန်းဂဏန်းအချို့ကို ထည့်ပေးထားပါသည်။
      import random

      sample_numbers = ["12", "45", "12", "78", "45", "12"]
      return random.choice(sample_numbers)

  except Exception as e:
    return None


print("--- ဒေတာမှတ်သားခြင်းနှင့် ရာခိုင်နှုန်းတွက်ချက်ခြင်း စတင်ပါပြီ ---")

try:
  # လိုအပ်သလို အချိန်အကြာကြီး မှတ်သားစေရန် while True သုံးထားသည်
  while True:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_number = fetch_website_data()

    if live_number:
      # Database ထဲသို့ သိမ်းမည်
      cursor.execute(
          "INSERT INTO number_logs (timestamp, live_data) VALUES (?, ?)",
          (current_time, live_number),
      )
      conn.commit()
      print(f"[{current_time}] မှတ်တမ်းတင်ပြီး - ဂဏန်း: {live_number}")

    # --- ၃။ အများဆုံးကျခဲ့သည့် နံပါတ်များနှင့် ရာခိုင်နှုန်းများကို တွက်ချက်ပြခြင်း ---
    print("\n---  ဂဏန်းကျရောက်မှု ရာခိုင်နှုန်းစာရင်း ---")

    # စုစုပေါင်း ဘယ်နှစ်ကြိမ် မှတ်မိလဲရေတွက်ခြင်း
    cursor.execute("SELECT COUNT(*) FROM number_logs")
    total_count = cursor.fetchone()[0]

    if total_count > 0:
      # ဂဏန်းတစ်ခုချင်းစီ ဘယ်နှစ်ခါကျလဲ စုစည်းပြီး အများဆုံးကနေ အနည်းကို စီခြင်း
      cursor.execute("""
                SELECT live_data, COUNT(*) as frequency 
                FROM number_logs 
                GROUP BY live_data 
                ORDER BY frequency DESC
            """)
      results = cursor.fetchall()

      for row in results:
        number = row[0]
        count = row[1]
        # ရာခိုင်နှုန်း တွက်ချက်ခြင်း (ကျတဲ့ကြိမ်ရေ / စုစုပေါင်းကြိမ်ရေ * 100)
        percentage = (count / total_count) * 100
        print(
            f"ဂဏန်း {number}: {count} ကြိမ် ကျ (ရာခိုင်နှုန်း: {percentage:.2f}%)"
        )
    else:
      print("ဒေတာ မရှိသေးပါ။")

    print("-" * 40)

    # ၁၀ စက္ကန့် တစ်ကြိမ် ထပ်လုပ်မည် (လိုသလို အချိန်ပြောင်းနိုင်ပါသည်)
    time.sleep(10)

except KeyboardInterrupt:
  conn.close()
  print("\n--- ပရိုဂရမ်ကို ရပ်တန့်လိုက်ပါပြီ ---")
