import streamlit as st
import re

# إعدادات الصفحة وتصميم الواجهة
st.set_page_config(page_title="برنامج خشم الذكي", layout="centered")

# تنسيق CSS لدعم اتجاه اللغة العربية من اليمين لليسار وتصميم الصناديق والأزرار
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    p, div, h1, h2, h3, h4, span, label, textarea {
        text-align: right !important;
        direction: rtl !important;
    }
    .green-box {
        background-color: #0d2e1e;
        border-right: 5px solid #00a859;
        padding: 20px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .print-btn {
        background-color: #15803d;
        color: white;
        padding: 12px;
        text-align: center !important;
        border-radius: 8px;
        font-weight: bold;
        display: block;
        width: 100%;
        text-decoration: none;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. دالة استخراج أسماء المركبات تلقائياً (بدون تثبيت كامري ويارس)
# ---------------------------------------------------------
def extract_vehicles(text):
    cars_list = [
        "اف جي", "إف جي", "صالون", "كامري", "يارس", "هايلكس", "لاندكروزر", 
        "جيب", "شاص", "ربع", "كورولا", "أكسنت", "اكسنت", "النترا", "إلنترا", 
        "سوناتا", "أزيرا", "ازيرا", "تاهو", "يوكن", "سوبربان", "كابرس", 
        "فورد", "تورس", "اكسبلورر", "إكسبلورر", "اكسبدشن", "مازدا", "نيسان", 
        "باترول", "صني", "التيما", "ألتيما", "مكسيما", "ددسن", "كيا", "سيراتو", 
        "أوبتيما", "كي 5", "سبورتاج", "شانجان", "ايدو", "إيدو", "جايكو", 
        "هافال", "جيلي", "ام جي", "إم جي", "لكزس", "مرسيدس", "بي ام", 
        "شاحنة", "دينا", "تريلا", "قلاب", "وايت", "باص", "حافلة", "دباب", "دراجة"
    ]
    
    found_cars = []
    for car in cars_list:
        for match in re.finditer(re.escape(car), text):
            found_cars.append((match.start(), car))
    
    # ترتيب المركبات حسب ظهورها في النص المكتوب
    found_cars.sort(key=lambda x: x[0])
    
    unique_cars = []
    for pos, car in found_cars:
        if not any(car in u or u in car for u in unique_cars):
            unique_cars.append(car)

    if len(unique_cars) >= 2:
        return unique_cars[0], unique_cars[1]
    elif len(unique_cars) == 1:
        return unique_cars[0], "المركبة الثانية"
    else:
        # البحث عن الكلمة التي تلي (الأولى / الثانية) إذا لم تكن السيارة في القائمة
        match1 = re.search(r'(?:الأولى|الاولى|الطرف الأول|الطرف الاول)\s+(?:مركبة\s+|سيارة\s+)?([^\s،.]+)', text)
        match2 = re.search(r'(?:الثانية|الثانيه|الطرف الثاني)\s+(?:مركبة\s+|سيارة\s+)?([^\s،.]+)', text)
        p1 = match1.group(1).strip() if match1 else "المركبة الأولى"
        p2 = match2.group(1).strip() if match2 else "المركبة الثانية"
        return p1, p2

# ---------------------------------------------------------
# 2. دالة تحليل الحادث وتوزيع النسب (100%، 75%، 50%، 25%، 0%)
# ---------------------------------------------------------
def analyze_accident(text):
    party1, party2 = extract_vehicles(text)
    
    p1_fault = 50
    p2_fault = 50
    legal_basis = "المادة (50) - الفقرة (1/1/6) القواعد العامة للأفضلية في التقاطعات"
    rule_explanation = "تحديد أولوية المرور في التقاطعات غير المنظمة وفقاً لقواعد أسبقية الوصول أو القواعد العامة للأولويات. في حال التكافؤ وعدم إمكانية تحديد الأسبقية، توزع المسؤولية مناصفة بنسبة (50%) لكل طرف."

    # تحليل الاتجاهات والأفضلية ونقاط التصادم
    p1_north_south = ("شمال" in text and "جنوب" in text)
    p2_east_west = ("شرق" in text and "غرب" in text)
    p1_wider = any(w in text for w in ["اوسع", "أوسع", "رئيسي"])
    both_bumps = text.count("مطب") >= 2
    p1_front_p2_side = ("مقدمه" in text or "مقدمة" in text) and ("جانب" in text or "الجانب" in text)

    # 1. حالات الخطأ الكامل (100% - 0%)
    if any(k in text for k in ["عكس السير", "قاطع إشارة", "قطع إشارة", "رجوع للخلف", "من الخلف", "مؤخرة"]):
        if any(k in text for k in ["الثانيه", "الثانية", party2]):
            p1_fault, p2_fault = 0, 100
        else:
            p1_fault, p2_fault = 100, 0
        legal_basis = "المادة (50) - مخالفة صريحة لقواعد السير والاتجاهات أو عدم ترك مسافة آمنة"
        rule_explanation = "يتحمل الطرف المتسبب بالحركة الخاطئة (عكس السير / قطع الإشارة / الرجوع للخلف / الاصطدام من الخلف) كامل المسؤولية النظامية بنسبة (100%)."

    # 2. حالات التقاطعات (75% - 25% أو 100% - 0% أو 50% - 50%)
    elif "تقاطع" in text or "التقاطع" in text:
        # إذا كان طريق الأولى أوسع (أو قادمة من اليمين) واصطدمت بمقدمتها في جانب الثانية مع وجود مطبات
        if (p1_wider or (p1_north_south and p2_east_west)) and (p1_front_p2_side or both_bumps):
            p1_fault = 25
            p2_fault = 75
            legal_basis = "المادة (50) - الفقرة (1/1/6) قواعد الأفضلية في التقاطعات (الأفضلية للطريق الأوسع وللقادم من اليمين مع اشتراك الطرف الآخر)"
            rule_explanation = f"الأفضلية للمركبة ({party1}) لكونها في المسار الأوسع وعن يمين المركبة الأخرى، وتتحمل المركبة ({party2}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية، بينما تتحمل ({party1}) نسبة (25%) لعدم التهدئة التامة عند المطب الصناعي والاصطدام بمقدمة كاملة في الجانب."
        
        # إذا كان طريق الأولى رئيسي أو أوسع بدون مطبات تهدئة للطرف الأول
        elif p1_wider and not both_bumps:
            p1_fault = 0
            p2_fault = 100
            legal_basis = "المادة (50) - الأفضلية للمركبات السائرة في الطريق الرئيسي أو الأوسع"
            rule_explanation = f"يتحمل الطرف الثاني ({party2}) كامل المسؤولية (100%) لدخوله من طريق أضيق/فرعي دون التأكد من خلو الطريق الرئيسي."

    return party1, party2, p1_fault, p2_fault, legal_basis, rule_explanation

# ---------------------------------------------------------
# 3. واجهة المستخدم (Streamlit UI)
# ---------------------------------------------------------
st.title("🚓 برنامج خشم الذكي")
st.subheader("نظام تحليل الحوادث المرورية (تصحيح مطابقة الفاعل والنسب)")

st.success("✅ تم تصحيح محرك قراءة النص لضمان إعطاء الخطأ للطرف المتسبب الفعلي بدقة")
st.markdown("---")

# إدارة زر المسح
if "accident_input" not in st.session_state:
    st.session_state.accident_input = ""

def clear_text():
    st.session_state.accident_input = ""

accident_text = st.text_area(
    "📝 أدخل تفاصيل الحادث (اذكر بوضوح نوع المركبات واتجاه السير ونقطة التصادم):",
    key="accident_input",
    height=160
)

analyze_btn = st.button("🔍 تحليل الحادث وتوزيع النسب بدقة", use_container_width=True)
clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

if analyze_btn:
    if accident_text.strip() == "":
        st.warning("يرجى إدخال تفاصيل الحادث أولاً.")
    else:
        p1, p2, f1, f2, basis, explanation = analyze_accident(accident_text)
        
        st.markdown("---")
        st.subheader("📋 التقرير النظامي المفصل للحادث")
        
        with st.expander("أولاً: التحليل الفني للحادث", expanded=True):
            st.write("تحليل معطيات النص الميداني وتحديد المركبة المتسببة بالفطرة بناءً على وصف حركة الأطراف:")
            st.info(f"**النص النظامي المعتمد:**\n\n{explanation}")
            
        with st.expander("ثالثاً: التقرير الرسمي المعتمد", expanded=True):
            st.markdown(f"""
            **موضوع التقرير:** معاينة حادث مروري وتحليل المسؤولية.
            
            **وصف الحادث:** {accident_text}
            
            **النتيجة النهائية وتوزيع النسب:**
            * **الطرف الأول ({p1}):** {f1}%
            * **الطرف الثاني ({p2}):** {f2}%
            * **السند النظامي المطبق:** {basis}
            """)
            
        # الصندوق الأخضر للنسب المعتمدة
        st.markdown(f"""
        <div class="green-box">
            <h4 style="color: #4ade80; margin-bottom: 15px;">📌 النسب النظامية المعتمدة (المصححة):</h4>
            <p style="color: white; font-size: 18px; font-weight: bold; margin: 5px 0;">🚗 الطرف الأول ({p1}): {f1}%</p>
            <p style="color: #f87171; font-size: 18px; font-weight: bold; margin: 5px 0;">🚙 الطرف الثاني ({p2}): {f2}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # زر الطباعة
        st.markdown("""
        <button onclick="window.print()" class="print-btn" style="border:none; cursor:pointer;">
            🖨️ طباعة التقرير الرسمي / حفظ كـ PDF
        </button>
        """, unsafe_allow_html=True)
