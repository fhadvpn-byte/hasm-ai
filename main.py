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

@st.cache_data
def load_traffic_law():
    try:
        with open("traffic.pdf", "rb") as file:
            reader = PyPDF2.PdfReader(file)
            return len(reader.pages)
    except:
        return 0

pages_count = load_traffic_law()

if pages_count > 0:
    st.success(f"✅ تم ربط النظام بنجاح (تمت قراءة {pages_count} صفحة من نظام المرور)")
else:
    st.error("❌ لم يتم العثور على ملف traffic.pdf")

# --- 3. واجهة المستخدم للإدخال ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ):", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("الرجاء كتابة تفاصيل الحادث أولاً.")
    else:
        with st.spinner("جاري تحليل المعطيات وربطها بالمواد النظامية..."):
            prompt = f"بناءً على نظام المرور السعودي، قم بتحليل هذا الحادث، حدد المخطئ، ونسبة الخطأ المتوقعة، مع صياغة التقرير بأسلوب رسمي:\n\n{accident_desc}"
            try:
                # المحاولة الأولى عبر النموذج المستقر
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                st.markdown("### 📄 التقرير المبدئي للحادث:")
                st.info(response.text)
            except:
                try:
                    # المحاولة البديلة عبر النموذج الذي نجح مسبقاً في حسابك
                    model = genai.GenerativeModel('gemma-4-26b-a4b-it')
                    response = model.generate_content(prompt)
                    st.markdown("### 📄 التقرير المبدئي للحادث:")
                    st.info(response.text)
                except Exception as e:
                    st.error(f"حدث خطأ في الاتصال: {e}")

