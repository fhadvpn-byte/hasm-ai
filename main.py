import streamlit as st
import os
import requests

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

# --- 2. قراءة المفتاح من الخزنة السرية ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"].strip()
except:
    API_KEY = ""

st.success("✅ تم ربط النظام بنجاح وجاهز لتحليل الحوادث المرورية")

# --- 3. واجهة إدخال الحادث والتحليل ---
st.markdown("---")
accident_desc = st.text_area("📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", height=150)

if st.button("🔍 بدء تحليل الحادث"):
    if accident_desc.strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    elif not API_KEY:
        st.error("⚠️ مفتاح Groq غير موجود في إعدادات Secrets في Streamlit.")
    else:
        with st.spinner("⏳ جاري تحليل الحادث واستخراج المواد النظامية المرورية..."):
            
            prompt = f"""أنت خبير مروري وقانوني معتمد في الإدارة العامة للمرور بالمملكة العربية السعودية، ومختص بتطبيق نظام المرور السعودي ولائحته التنفيذية.
قم بتحليل الحادث المروري التالي بدقة تامة، وأصدر تقريراً نظامياً رسمياً يتضمن:
1. **نسبة الخطأ والمسؤولية:** تحديد الطرف المخطئ ونسبة الخطأ بدقة.
2. **السند النظامي:** ذكر المادة النظامية أو القاعدة المرورية المعتمدة في نظام المرور السعودي والتي تم تطبيقها على هذا الحادث.
3. **التفسير المروري والفني:** شرح سبب تحميل المسؤولية والأولوية بناءً على قواعد السير والمرور.

تفاصيل الحادث المروري المدخلة:
{accident_desc}"""

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {API_KEY}"
            }
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "أنت مستشار مروري خبير في نظام المرور السعودي. تجيب باللغة العربية الفصحى بدقة وتستشهد بالمواد النظامية."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    output_text = response.json()['choices'][0]['message']['content']
                    st.markdown("### 📋 التقرير النظامي للحادث:")
                    st.info(output_text)
                else:
                    st.error(f"خطأ في الاتصال ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"حدث خطأ غير متوقع: {e}")
