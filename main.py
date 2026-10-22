import streamlit as st
import PyPDF2
import os
import requests
import json

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. ضع المفتاح الجديد الذي يبدأ بـ AIzaSy هنا ---
API_KEY = "AQ.Ab8RN6Iewx2VB5nSU5tHW0hbJdOmJetm8cQZl3cvI0cqv1qaqw"

# --- 3. قراءة نصوص نظام المرور من ملف الـ PDF ---
@st.cache_data
def load_traffic_law():
    pdf_path = "traffic.pdf"
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                full_text = ""
                for page in reader.pages:
                    full_text += (page.extract_text() or "") + "\n"
                return len(reader.pages), full_text
        except Exception as e:
            return 0, ""
    return 0, ""

pages_count, law_text = load_traffic_law()

if pages_count > 0:
    st.success(f"تم ربط النظام بنجاح (تم قراءة {pages_count} صفحة من نظام المرور)")
else:
    st.error("❌ لم يتم قراءة ملف traffic.pdf، تأكد من وجوده بالمجلد الرئيسي في GitHub")

# --- 4. واجهة إدخال الحادث والتحليل ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري مراجعة مواد نظام المرور وتحليل الحادث..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
                headers = {'Content-Type': 'application/json'}
                
                prompt = f"""أنت خبير مروري. بالاعتماد الحصري على نص نظام المرور السعودي المرفق أدناه، قم بتحليل الحادث التالي وتحديد نسبة الخطأ ورقم المادة النظامية ونصها:

نص نظام المرور المرفق:
{law_text[:30000]}

تفاصيل الحادث:
{accident_desc}"""
                
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
                    st.error(f"خطأ في المفتاح أو الاتصال ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
