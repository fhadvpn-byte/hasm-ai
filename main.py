import streamlit as st
import re

st.set_page_config(page_title="برنامج خشم الذكي", layout="centered")

# تنسيق الواجهة بدون علامات تنصيص ثلاثية لتجنب أي أخطاء نسخ
css_style = (
    "<style>"
    ".stApp { direction: rtl; text-align: right; }"
    "p, div, h1, h2, h3, h4, span, label, textarea, li { text-align: right !important; direction: rtl !important; }"
    ".law-box { background-color: #1e293b; border-right: 4px solid #38bdf8; padding: 15px; border-radius: 8px; margin: 10px 0; color: #f8fafc; }"
    ".green-box { background-color: #0d2e1e; border-right: 5px solid #00a859; padding: 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 15px; }"
    ".print-btn { background-color: #15803d; color: white; padding: 12px; text-align: center !important; border-radius: 8px; font-weight: bold; display: block; width: 100%; border: none; cursor: pointer; margin-top: 15px; }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

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
        match1 = re.search(r'(?:الأولى|الاولى|الطرف الأول|الطرف الاول)\s+(?:مركبة\s+|سيارة\s+)?([^\s،.]+)', text)
        match2 = re.search(r'(?:الثانية|الثانيه|الطرف الثاني)\s+(?:مركبة\s+|سيارة\s+)?([^\s،.]+)', text)
        p1 = match1.group(1).strip() if match1 else "المركبة الأولى"
        p2 = match2.group(1).strip() if match2 else "المركبة الثانية"
        return p1, p2

def is_party2_at_fault(text, party1, party2, keywords):
    for kw in keywords:
        if kw in text:
            before_kw = text.split(kw)[0]
            if party2 in before_kw[-35:] or "الثانيه" in before_kw[-35:] or "الثانية" in before_kw[-35:]:
                return True
            if party1 in before_kw[-35:] or "الاولى" in before_kw[-35:] or "الأولى" in before_kw[-35:]:
                return False
    if "وقوف" in text or "متوقفة" in text or "واقفه" in text:
        before_stop = text.split("وقوف")[0] if "وقوف" in text else ""
        if party1 in before_stop or "الاولى" in before_stop or "الأولى" in before_stop or text.find(party1) < text.find(party2):
            return True
    return True

def analyze_accident(text):
    party1, party2 = extract_vehicles(text)
    
    p1_fault = 50
    p2_fault = 50
    article_num = "المادة (50) - الفقرة (1/1/6) من نظام المرور ولائحته التنفيذية"
    article_text = "تحدد أولوية المرور في التقاطعات غير المنظمة بإشارات أو لوحات مرورية وفقاً لقواعد الأفضلية العامة وأسبقية الوصول."
    application_text = "في حال التكافؤ في أولوية الطريق وعدم إمكانية تحديد أسبقية الدخول للتقاطع، توزع المسؤولية مناصفة بنسبة (50%) لكل طرف."

    p1_north_south = ("شمال" in text and "جنوب" in text)
    p2_east_west = ("شرق" in text and "غرب" in text)
    p1_wider = any(w in text for w in ["اوسع", "أوسع", "رئيسي"])
    both_bumps = text.count("مطب") >= 2
    p1_front_p2_side = ("مقدمه" in text or "مقدمة" in text) and ("جانب" in text or "الجانب" in text)

    if any(k in text for k in ["بالرجوع", "رجوع للخلف", "يرجع للخلف", "انحراف", "انحرفت", "دوران"]):
        p2_fault_flag = is_party2_at_fault(text, party1, party2, ["بالرجوع", "رجوع", "انحراف", "انحرفت", "دوران", "قامت"])
        p1_fault, p2_fault = (0, 100) if p2_fault_flag else (100, 0)
        fault_car = party2 if p2_fault == 100 else party1
        article_num = "المادة (50) - الفقرة (24/2) من نظام المرور ولائحته التنفيذية"
        article_text = "على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو الدوران إلى الخلف في الاتجاه المعاكس لخط سيره مراعاة التأكد من إمكان إجراء ذلك دون خطر وإعطاء الإشارات اللازمة."
        application_text = f"تتحمل المركبة ({fault_car}) التي قامت بالرجوع للخلف أو الانحراف دون التأكد من خلو الطريق المسؤولية الكاملة بنسبة (100%)."

    elif any(k in text for k in ["من الخلف", "مؤخرة", "في الخلفية"]):
        p2_fault_flag = is_party2_at_fault(text, party1, party2, ["اصطدمت", "صدمت", "ارتطمت"])
        p1_fault, p2_fault = (0, 100) if p2_fault_flag else (100, 0)
        fault_car = party2 if p2_fault == 100 else party1
        article_num = "المادة (50) - الفقرة (12/2) من نظام المرور ولائحته التنفيذية"
        article_text = "يجب على قائد المركبة ترك مسافة كافية بينه وبين المركبة التي أمامه، بحيث يمكنه التوقف بأمان في حال توقف المركبة الأمامية فجأة."
        application_text = f"تتحمل المركبة اللاحقة ({fault_car}) كامل المسؤولية النظامية بنسبة (100%) لعدم ترك المسافة النظامية الآمنة."

    elif any(k in text for k in ["عكس السير", "قاطع إشارة", "قطع إشارة", "الاشارة حمراء", "الإشارة حمراء"]):
        p2_fault_flag = is_party2_at_fault(text, party1, party2, ["عكس", "قاطع", "قطع", "تجاوز"])
        p1_fault, p2_fault = (0, 100) if p2_fault_flag else (100, 0)
        fault_car = party2 if p2_fault == 100 else party1
        article_num = "المادة (50) - جدول المخالفات رقم (6) من نظام المرور ولائحته التنفيذية"
        article_text = "يحظر على قائد المركبة السير بعكس اتجاه الحركة المقرر أو تجاوز الإشارة الضوئية أثناء الضوء الأحمر، ويلتزم بالتوقف التام قبل خط المشاة."
        application_text = f"تتحمل المركبة المخالفة ({fault_car}) كامل المسؤولية النظامية عن الحادث بنسبة (100%)."

    elif "تقاطع" in text or "التقاطع" in text:
        if (p1_wider or (p1_north_south and p2_east_west)) and (p1_front_p2_side or both_bumps):
            p1_fault = 25
            p2_fault = 75
            article_num = "المادة (50) - الفقرة (1/1/6) من نظام المرور ولائحته التنفيذية"
            article_text = "تكون الأفضلية في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، وعند تساوي الطرق تكون الأفضلية للقادم من جهة اليمين، مع التزام كافة المركبات بالتهدئة وأخذ الحيطة عند الاقتراب من التقاطعات والمطبات الصناعية."
            application_text = f"تتحمل المركبة ({party2}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية للمسار الأوسع والقادم من اليمين، وتتحمل المركبة ({party1}) نسبة (25%) لعدم التهدئة التامة عند المطب الصناعي والاصطدام بمقدمة كاملة في جانب المركبة الأخرى."
        elif p1_wider and not both_bumps:
            p1_fault = 0
            p2_fault = 100
            article_num = "المادة (50) - الفقرة (2/1/6) من نظام المرور ولائحته التنفيذية"
            article_text = "على قائد المركبة القادم من طريق فرعي أو أضيق التوقف والتأكد التام من خلو الطريق الرئيسي أو الأوسع وإعطاء الأفضلية للمركبات السائرة فيه قبل الدخول إلى منطقة التقاطع."
            application_text = f"تتحمل المركبة ({party2}) كامل المسؤولية بنسبة (100%) لدخولها التقاطع من طريق أضيق دون التأكد من خلو الطريق الأوسع."

    return party1, party2, p1_fault, p2_fault, article_num, article_text, application_text

st.title("🚓 برنامج خشم الذكي")
st.subheader("نظام التحليل الفني للحوادث المرورية وتقدير نسب المسؤولية")
st.success("✅ محرك التحليل الذكي: تحديد دقيق لنسب المسؤولية وفق نظام المرور السعودي ولائحته التنفيذية")
st.markdown("---")

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
        p1, p2, f1, f2, article_num, article_text, application_text = analyze_accident(accident_text)
        
        st.markdown("---")
        st.subheader("📋 التقرير النظامي المفصل للحادث")
        
        with st.expander("أولاً: التحليل الفني للحادث 🔍", expanded=True):
            st.write("تحليل معطيات النص الميداني وتحديد المركبة المتسببة بالفطرة بناءً على وصف حركة الأطراف.")
            law_html = f'<div class="law-box"><strong>⚖️ رقم المادة المستند إليها:</strong> {article_num}<br><br><strong>📜 نص المادة النظامي:</strong> "{article_text}"</div>'
            st.markdown(law_html, unsafe_allow_html=True)
            
        with st.expander("ثانياً: التكييف النظامي ونصوص المواد وتقسيماتها ⚖️", expanded=True):
            st.markdown("### السند القانوني الرسمي:")
            st.markdown(f"* **رقم المادة:** {article_num}")
            st.markdown("**النص النظامي المعتمد:**")
            st.markdown(f"* {article_text}")
            st.markdown(f"* {application_text}")
            
        with st.expander("ثالثاً: التقرير الرسمي المعتمد 📄", expanded=True):
            st.markdown("**موضوع التقرير:** معاينة حادث مروري وتحليل المسؤولية.")
            st.markdown(f"* **وصف الحادث:** {accident_text}")
            st.markdown("**النتيجة النهائية وتوزيع النسب:**")
            st.markdown(f"* **الطرف الأول ({p1}):** {f1}%")
            st.markdown(f"* **الطرف الثاني ({p2}):** {f2}%")
            st.markdown(f"* **السند النظامي المطبق (رقم المادة):** {article_num}")
            st.markdown(f"* **نص المادة المستند لها:** {article_text}")
            st.markdown(f"* **التطبيق النظامي على الحادث:** {application_text}")
            
        green_html = (
            f'<div class="green-box">'
            f'<h4 style="color: #4ade80; margin-bottom: 15px;">📌 النسب النظامية المعتمدة (المصححة):</h4>'
            f'<p style="color: white; font-size: 18px; font-weight: bold; margin: 5px 0;">🚗 الطرف الأول ({p1}): {f1}%</p>'
            f'<p style="color: #f87171; font-size: 18px; font-weight: bold; margin: 5px 0;">🚙 الطرف الثاني ({p2}): {f2}%</p>'
            f'<hr style="border-color: #15803d; margin: 12px 0;">'
            f'<p style="color: #bbf7d0; font-size: 15px; margin: 4px 0;"><strong>⚖️ السند النظامي:</strong> {article_num}</p>'
            f'<p style="color: #e2e8f0; font-size: 14px; margin: 4px 0;"><strong>📜 نص المادة:</strong> {article_text}</p>'
            f'</div>'
        )
        st.markdown(green_html, unsafe_allow_html=True)
        
        btn_html = '<button onclick="window.print()" class="print-btn">🖨️ طباعة التقرير الرسمي / حفظ كـ PDF</button>'
        st.markdown(btn_html, unsafe_allow_html=True)
