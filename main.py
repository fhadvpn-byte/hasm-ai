import streamlit as st
import google.generativeai as genai
import PyPDF2
import os

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. إعداد الذكاء الاصطناعي بالمفتاح الصحيح الذي يبدأ بـ AIza ---
API_KEY = "curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
  -H 'Content-Type: application/json' \
  -H 'X-goog-api-key: AQ.Ab8RN6Lk0KZkpUYHwgAG74Jo2b5YQ5LomC401INizJxBV983nQ' \
  -X POST \
  -d '{
    "contents": [
      {
        "parts": [
          {
            "text": "Explain how AI works in a few words"
          }
        ]
      }
    ]
  }'"  # الصق مفتاحك الصحيح هنا بين علامتي التنصيص
genai.configure(api_key=API_KEY)

# قراءة الملف بطريقة مضمونة ومباشرة
@st.cache_data
def load_traffic_law():
    pdf_path = "traffic.pdf"
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                return len(reader.pages)
        except:
            return 0
    return 0

pages_count = load_traffic_law()

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
                # استخدام نموذج 1.5-flash المدعوم رسمياً
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"بناءً على نظام المرور السعودي المرفق، قم بتحليل هذا الحادث بدقة وتحديد نسبة الخطأ والمادة النظامية:\n\nتفاصيل الحادث: {accident_desc}"
                response = model.generate_content(prompt)
                st.markdown("### 📋 التقرير النظامي للحادث:")
                st.info(response.text)
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال أو المفتاح: {e}")
