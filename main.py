import streamlit as st
import PyPDF2
import os
import requests
import re

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. قراءة المفتاح من الخزنة السرية ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"].strip()
except:
    API_KEY = ""

# --- 3. قراءة نصوص نظام المرور من ملف الـ PDF بالكامل ---
@st.cache_data
def load_traffic_law():
    pdf_path = "traffic.pdf"
    if not os.path.exists(pdf_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        pdf_path = os.path.join(base_dir, "traffic.pdf")
        
    if os.path.exists(pdf_path):
        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                pages_text = []
                for idx, page in enumerate(reader.pages):
                    txt = page.extract_text() or ""
                    pages_text.append(f"[صفحة {idx+1}]\n{txt}")
                return len(reader.pages), pages_text
        except Exception as e:
            return 0, []
    return 0, []

pages_count, law_pages = load_traffic_law()

if pages_count > 0:
    st.success(f"✅ تم ربط النظام بنجاح (تم قراءة {pages_count} صفحة من نظام المرور السعودي)")
else:
    st.error("❌ لم يتم قراءة ملف traffic.pdf، تأكد من رفعه في GitHub بجانب ملف main.py")

# دالة لاستخراج أهم الصفحات والمواد المرتبطة بالحادث من الـ 115 صفحة
def get_relevant_law_text(accident_desc, pages):
    if not pages:
        return ""
    keywords = [w for w in re.findall(r'\w+', accident_desc) if len(w) > 2]
    traffic_terms = ["مادة", "المادة", "حادث", "مسافة", "الخلف", "تجاوز", "إشارة", "أولوية", "مسار", "خطأ", "مخالفة", "تقاطع", "دوار", "سرعة", "وقوف"]
    
    scored_pages = []
    for p in pages:
        score = 0
        for kw in keywords:
            if kw in p:
                score += 3
        for term in traffic_terms:
            if term in p:
                score += 1
        scored_pages.append((score, p))
        
    scored_pages.sort(key=lambda x: x[0], reverse=True)
    top_pages = [p for s, p in scored_pages[:18]]
    return "\n\n".join(top_pages)

# --- 4. واجهة إدخال الحادث والتحليل ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري فحص مواد نظام المرور من ملف الـ PDF وتحليل الحادث..."):
            relevant_law = get_relevant_law_text(accident_desc, law_pages)
            
            prompt = f"""أنت خبير مروري وقانوني مختص في نظام المرور السعودي ولائحته التنفيذية.
أمامك نصوص مستخرجة مباشرة من ملف (نظام المرور السعودي PDF المرفق بالنظام):

--- النصوص والمواد النظامية المستخرجة من ملف الـ PDF ---
{relevant_law[:25000]}

--- تفاصيل الحادث المروري ---
{accident_desc}

المطلوب منك إصدار تقرير مروري رسمي ومفصل يتضمن:
1. **نسبة الخطأ والمسؤولية:** تحديد الطرف المخطئ ونسبة الخطأ.
2. **السند النظامي من ملف الـ PDF:** ذكر رقم المادة النظامية أو الفقرة من نظام المرور السعودي ونصها كما وردت في النظام.
3. **التفسير المروري والفني:** شرح سبب تحميل المسؤولية بناءً على قواعد السير والأولويات في النظام."""

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "أنت مستشار مروري خبير في نظام المرور السعودي. تجيب باللغة العربية الفصحى بدقة وتستشهد بالمواد النظامية المرفقة."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    output_text = response.json()['choices'][0]['message']['content']
                    st.markdown("### 📋 التقرير النظامي للحادث (من واقع ملف نظام المرور):")
                    st.info(output_text)
                else:
                    st.error(f"خطأ في الاتصال ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
