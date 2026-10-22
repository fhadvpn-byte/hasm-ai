import streamlit as st
import PyPDF2
import os
import requests

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. إعداد المفتاح والرابط الرسمي المعتمد من حسابك ---
API_KEY = "AQ.Ab8RN6Iewx2VB5nSU5tHW0hbJdOmJetm8cQZl3cvI0cqv1qaqw"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"

# --- 3. قراءة نصوص نظام المرور من ملف الـ PDF ---
@st.cache_data
def load_traffic_law():
    # البحث عن الملف في المسار الرئيسي للتطبيق
    pdf_path = "traffic.pdf"
    if not os.path.exists(pdf_path):
        # محاولة إضافية للبحث في نفس مجلد ملف الكود
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base_dir, "traffic.pdf")
        
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
    st.success(f"✅ تم ربط النظام بنجاح (تم قراءة {pages_count} صفحة من نظام المرور السعودي)")
else:
    st.error("❌ لم يتم قراءة ملف traffic.pdf، تأكد من رفعه في GitHub بجانب ملف main.py")

# --- 4. واجهة إدخال الحادث والتحليل ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري مراجعة مواد نظام المرور وتحليل الحادث..."):
            try:
                # إعداد الترويسة (Headers) مطابقة تماماً لكود cURL الخاص بك
                headers = {
                    "Content-Type": "application/json",
                    "X-goog-api-key": API_KEY
                }
                
                # تجهيز الأمر مع إرفاق نص نظام المرور المستخرج من الـ PDF
                prompt = f"""أنت خبير مروري مختص في نظام المرور السعودي. 
بالاعتماد على نصوص ومواد نظام المرور السعودي المرفقة أدناه، قم بتحليل الحادث المروري التالي بدقة، وحدد:
1. نسبة الخطأ على كل طرف.
2. رقم المادة النظامية المستند عليها ونصها.
3. التبرير النظامي والمروري للحكم.

--- نصوص من نظام المرور المرفق ---
{law_text[:40000]}

--- تفاصيل الحادث المطلوب تحليله ---
{accident_desc}"""

                payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                }
                
                response = requests.post(API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    res_json = response.json()
                    output_text = res_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### 📋 التقرير النظامي للحادث:")
                    st.info(output_text)
                else:
                    st.error(f"حدث خطأ من الخادم ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
