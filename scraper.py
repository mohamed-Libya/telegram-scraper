from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests
import asyncio
import datetime
from flask import Flask
from threading import Thread
import os

# === بياناتك (جاهزة ومدمجة) ===
API_ID = 29002892
API_HASH = '62b7e12f33757712f13a66ad4125cd73'
SESSION_STRING = '1BJWap1wBu0cAaQqQGPFv4TdQo0mzygdJOPaCaV66E5vRBEblwq_PNbKOTPLgpWEPc2fHb8vcA9I9HSx5z2NNBexAS0FhMamHwDiDy9hacFievGSAVme4voAR8ObPelLh9RcKwITLkGxoNanhy6y3g_NyFbJwKW5_76Gnbq7npbujfIecMWh92RPWYi_dS2Pdg-wiRlZw0PqMqQ26pXay4lCCUGOfeC-9_O1JVAfnzFymFWjjKVpA0P2aE33HI_84f4Qknn3bpYGHsi0p9pe7IF2GZvol-23wArB_rIwRNhJyaPDYNARGKtDNAr8LufM7dhJ5H5DVkXYcp0Sc3N18Shp2LQ4EB3I='
WEBHOOK_URL = 'https://flow.sokt.io/func/scriupVsntDz'
TARGET_CHANNEL = '@lydollar'
# ===============================

# 1. إعداد "خادم الويب الوهمي" (Flask) باش السكريبت يقعد فايق 24 ساعة
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "السيرفر يخدم وأموره تمام! 🚀"

def run_flask():
    # Render يعطينا بورت معين لازم نستخدموه، لو مفيش حيستخدم 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. إعداد سكريبت التليجرام الأساسي
async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(chats=TARGET_CHANNEL))
    async def my_event_handler(event):
        message_text = event.message.message
        print(f"\n📩 رسالة جديدة من {TARGET_CHANNEL}:\n{message_text}\n")
        
        has_green_circle = "🟢" in message_text
        has_today = "اليوم" in message_text
        has_dollar = "الدولار" in message_text
        has_signature = "@lydollar" in message_text
        
        if has_green_circle and has_today and has_dollar and has_signature:
            print("✅ النمط متطابق. جاري الإرسال...")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            
            payload = {"price_data": message_text, "post_time": current_time}
            try:
                response = requests.post(WEBHOOK_URL, json=payload)
                print(f"🚀 تم الإرسال! (حالة السيرفر: {response.status_code})")
            except Exception as e:
                print(f"❌ حدث خطأ أثناء الإرسال: {e}")
        else:
            print("🚫 الرسالة تم تجاهلها (لا تطابق النمط).")

    print("🤖 جاري الاتصال بتليجرام (السحابة)...")
    await client.start()
    print("✅ نظام المراقبة يعمل الآن 24/7...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import sys
    # 1. حل مشكلة الويندوز مع البايثون
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    # 2. نشغلوا خادم الـ Flask في مسار (Thread) منفصل
    Thread(target=run_flask).start()
    
    # 3. نشغلوا التليجرام بالطريقة الحديثة
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف السكربت يدوياً.")