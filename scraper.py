from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests
import asyncio
import datetime
from flask import Flask, jsonify  # 💡 إضافة jsonify لتحويل البيانات لصيغة JSON
from threading import Thread
import os

# === بياناتك (جاهزة ومدمجة) ===
API_ID = 29002892
API_HASH = '62b7e12f33757712f13a66ad4125cd73'
SESSION_STRING = '1BJWap1wBu6YxwsGVm-Ynolut0efBayxqQp57Vbd9pncvgUQQ1Hm1-XzJIvYsOV7RWVBCGGpE7T32kAeWDHdHiiOgQL5G1G8KtZK8TgEPTghvbPrgp4VhicoQiaVgG0pZuoN2pNr3YmfZoXv4mhLW6SdO0ERTPU6qtEZAcluEPqZgGrO-ADg6p559U8iLnNKpDGubEon9N7AA7KzuanGxd1AsgrjbuvYtmZH7oYKQ3DOubWeeucIFxSW3bjcpnylDJ0DPpjd0cubC4v0S7Wr9MyOFrRMRi_Q8cEForD202OknzOJs0RAIGskQCYFRKgUkEiTOJcN0z6MEznmSbwNZ7tmP9uZxb-8='
WEBHOOK_URL = 'https://flow.sokt.io/func/scriupVsntDz'
TARGET_CHANNEL = '@lydollar'
# ===============================

# 💡 1. متغير جديد بمثابة "ذاكرة مؤقتة" يحفظ آخر سعر يتم سحبه
latest_price_data = {
    "currency": "USD",
    "price_text": "في انتظار أول تحديث للسعر من السوق...",
    "time": "N/A",
    "status": "waiting"
}

# 2. إعداد "خادم الويب الوهمي" (Flask) باش السكريبت يقعد فايق 24 ساعة
app = Flask(__name__)

@app.route('/')
def keep_alive():
    return "السيرفر يخدم وأموره تمام! 🚀 (مسار الـ API هو: /api/price)"

# 💡 3. هذا هو "الـ API" الجديد اللي حيكلمه تطبيق الأندرويد بتاعك
@app.route('/api/price')
def get_price_api():
    # الفانكشن هذي تاخذ المتغير وتحوله لملف JSON تلقائياً
    return jsonify(latest_price_data)

def run_flask():
    # Render يعطينا بورت معين لازم نستخدموه، لو مفيش حيستخدم 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 4. إعداد سكريبت التليجرام الأساسي
async def main():
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

    @client.on(events.NewMessage(chats=TARGET_CHANNEL))
    async def my_event_handler(event):
        global latest_price_data  # 💡 باش نقدروا نحدثوا الذاكرة من داخل الفانكشن
        
        message_text = event.message.message
        print(f"\n📩 رسالة جديدة من {TARGET_CHANNEL}:\n{message_text}\n")
        
        has_green_circle = "🟢" in message_text
        has_today = "اليوم" in message_text
        has_dollar = "الدولار" in message_text
        has_signature = "@lydollar" in message_text
        
        # الشرط: التأكد إن الرسالة لا تحتوي على المركزي نهائياً
        is_not_central = "المركزي" not in message_text and "مركزي" not in message_text
        
        if has_green_circle and has_today and has_dollar and has_signature and is_not_central:
            print("✅ النمط متطابق (سوق موازي). جاري الإرسال وتحديث الـ API...")
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
            
            # 💡 تحديث الذاكرة المؤقتة بالسعر الجديد باش تطلع في تطبيق الموبايل
            latest_price_data["price_text"] = message_text
            latest_price_data["time"] = current_time
            latest_price_data["status"] = "updated"
            
            payload = {"price_data": message_text, "post_time": current_time}
            try:
                # إرسال البيانات للفيسبوك عن طريق Viasocket
                response = requests.post(WEBHOOK_URL, json=payload)
                print(f"🚀 تم الإرسال للفيسبوك! (حالة السيرفر: {response.status_code})")
            except Exception as e:
                print(f"❌ حدث خطأ أثناء الإرسال: {e}")
        else:
            print("🚫 الرسالة تم تجاهلها (لا تطابق النمط أو تابعة للمركزي).")

    print("🤖 جاري الاتصال بتليجرام (السحابة)...")
    await client.start()
    print("✅ نظام المراقبة يعمل الآن 24/7...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    import sys
    # حل مشكلة الويندوز مع البايثون
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    # نشغلوا خادم الـ Flask في مسار (Thread) منفصل
    Thread(target=run_flask).start()
    
    # نشغلوا التليجرام بالطريقة الحديثة
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف السكربت يدوياً.")