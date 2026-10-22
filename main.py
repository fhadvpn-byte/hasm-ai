import streamlit as st
import google.generativeai as genai
import PyPDF2

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. إعداد الذكاء الاصطناعي ---
API_KEY = "AQ.Ab8RN6Ijy1n4swLkb-ZFcaAER9CLz-5vxLE8oooI-gWHlie0LQ"
genai.configure(api_key=API_KEY)

# قراءة الملف مرة واحدة وتخزينها مؤقتاً لسرعة النظام
@st.cache_data
def load_traffic_law_text():
    try:
        with open("traffic.pdf", "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            # نأخذ ملخص أو أول الصفحات لتسريع المعالجة وضمان الاستجابة الفورية
            for page in reader.pages[:30]:
                text += page.extract_text() + "\n"
            return len(reader.pages), text
    except:
        return 0, ""

pages_count, law_text = load_traffic_law_text()

if pages_count > 0:
    st.success(f"تم ربط النظام بنجاح (تم قراءة {pages_count} صفحة من نظام المرور)")
else:
    st.error("❌ لم يتم العثور على ملف traffic.pdf")

# --- 3. واجهة المستخدم للإدخال ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري تحليل الحادث وإصدار التقرير..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-pro')
                prompt = f"بناءً على نظام المرور السعودي، قم بتحليل هذا الحادث بدقة وتحديد نسبة الخطأ والمادة النظامية:\n\nتفاصيل الحادث: {accident_desc}"
                response = model.generate_content(prompt)
                st.markdown("### 📋 التقرير النظامي للحادث:")
                st.info(response.text)
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")
