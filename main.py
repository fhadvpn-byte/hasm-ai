import streamlit as st
import PyPDF2
import os
import requests
import json

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. إعداد المفتاح المباشر ---
API_KEY = "AQ.Ab8RN6LLWlu9ULEhJqJFdjSR6rt4HgOzfMAyUB2IS43XwIBtVA"

# قراءة الملف بطريقة مضمونة ومباشرة
@st.cache_data
def load_traffic_law():
    pdf_path = "traffic.pdf"
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return len(reader.pages), text
        except:
            return 0, ""
    return 0, ""

pages_count, pdf_text = load_traffic_law()

if pages_count > 0:
    st.success(f"تم ربط النظام بنجاح (تم قراءة {pages_count} صفحة من نظام المرور)")
else:
    st.error("❌ لم يتم قراءة ملف traffic.pdf، تأكد من وجوده بالمجلد الرئيسي")

# --- 3. واجهة المستخدم للإدخال ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري تحليل الحادث وإصدار التقرير..."):
            try:
                # استخدام الاتصال المباشر عبر HTTP لضمان قبول التوكن وتجنب خطأ 401
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                headers = {'Content-Type': 'application/json'}
                
                prompt = f"بناءً على نظام المرور السعودي، قم بتحليل هذا الحادث بدقة وتحديد نسبة الخطأ والمادة النظامية:\n\nتفاصيل الحادث: {accident_desc}"
                
                data = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }
                
                response = requests.post(url, headers=headers, data=json.dumps(data))
                
                if response.status_code == 200:
                    res_json = response.json()
                    output_text = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### 📋 التقرير النظامي للحادث:")
                    st.info(output_text)
                else:
                    st.error(f"خطأ من الخادم ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")
