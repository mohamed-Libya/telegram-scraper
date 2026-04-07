import requests
from bs4 import BeautifulSoup
import time
import datetime
import pytz
from flask import Flask
from threading import Thread
import os

# === إعداداتك ===
NEW_WEBHOOK_URL = 'https://flow.sokt.io/func/scri1lywEHM4'
# ===============================

# 1. إعداد "خادم الويب الوهمي" باش Render ما يطفيش السكريبت
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "سيرفر مراقبة الموقع يخدم أموره طيبة! 🌐"

def run_flask():
    port = int(os.environ.get("PORT", 10001))
    app.run(host='0.0.0.0', port=port)

# ذاكرة السكريبت
last_saved_prices = ""

def check_website_for_changes():
    global last_saved_prices
    url = "https://www.eanlibya.com/exchangerate/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    # تحديد توقيت ليبيا بشكل قاطع
    libya_tz = pytz.timezone('Africa/Tripoli')
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tables = soup.find_all('table')
        
        if tables:
            current_prices = tables[0].get_text(separator="\n", strip=True)
            
            if last_saved_prices == "":
                print("✅ [تأسيس الذاكرة]: تم حفظ الأسعار لأول مرة، جاري المراقبة...")
                last_saved_prices = current_prices
                
            elif current_prices != last_saved_prices:
                print("🚨 تم رصد تغيير في أسعار الموقع! جاري إيقاظ الذكاء الاصطناعي...")
                
                # أخذ الوقت بتوقيت ليبيا حصرياً
                current_time = datetime.datetime.now(libya_tz).strftime("%Y-%m-%d %I:%M %p")
                
                payload = {
                    "website_data": current_prices, 
                    "post_time": current_time,
                    "source": "عين ليبيا"
                }
                
                res = requests.post(NEW_WEBHOOK_URL, json=payload)
                print(f"🚀 تم الإرسال للـ AI Agent! (حالة السيرفر: {res.status_code})")
                
                last_saved_prices = current_prices
                
            else:
                now = datetime.datetime.now(libya_tz).strftime('%I:%M %p')
                print(f"⏳ [{now}] تم الفحص: لا يوجد تغيير في الأسعار.")
                
        else:
            print("❌ لم أتمكن من العثور على جدول الأسعار في الموقع.")
            
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الاتصال بالموقع: {e}")

def start_monitoring():
    print("🤖 بدأ تشغيل رادار مراقبة موقع 'عين ليبيا'...")
    while True:
        check_website_for_changes()
        time.sleep(900) 

if __name__ == '__main__':
    Thread(target=run_flask).start()
    start_monitoring()