import streamlit as st
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="برنامج حَسْم الذكي", layout="centered")

# تنسيق الواجهة وإعدادات الطباعة الرسمية
css_style = (
    "<style>"
    ".stApp { direction: rtl; text-align: right; }"
    "p, div, h1, h2, h3, h4, span, label, textarea, li { text-align: right !important; direction: rtl !important; }"
    ".law-box { background-color: #1e293b; border-right: 4px solid #38bdf8; padding: 15px; border-radius: 8px; margin: 10px 0; color: #f8fafc; }"
    ".green-box { background-color: #0d2e1e; border-right: 5px solid #00a859; padding: 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 15px; }"
    "@media print { .stButton, textarea, header, footer { display: none !important; } }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. دالة استخراج المركبات وفصل سياق كل طرف بدقة
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

# ---------------------------------------------------------
# 2. محرك التحليل السياقي الذكي (يربط الفعل والضرر بصاحبه الفعلي)
# ---------------------------------------------------------
def get_party_context(text, party_name, party_order):
    # جمع كل الجمل أو المقاطع التي تتحدث عن هذا الطرف تحديداً
    order_words = ["الأولى", "الاولى", "الطرف الأول", "الطرف الاول"] if party_order == 1 else ["الثانية", "الثانيه", "الطرف الثاني"]
    other_words = ["الثانية", "الثانيه", "الطرف الثاني"] if party_order == 1 else ["الأولى", "الاولى", "الطرف الأول", "الطرف الاول"]
    
    # تقسيم النص إلى جمل وأسطر لتحليل دقيق
    segments = re.split(r'[\n.،؛]', text)
    party_segments = []
    
    current_owner = 0
    for seg in segments:
        has_self = party_name in seg or any(w in seg for w in order_words)
        has_other = any(w in seg for w in other_words)
        
        if has_self and not has_other:
            current_owner = party_order
            party_segments.append(seg)
        elif has_self and has_other:
            # إذا الجملة فيها الطرفين، نأخذ الجزء الأقرب لاسم المركبة
            party_segments.append(seg)
        elif current_owner == party_order and not has_other:
            party_segments.append(seg)
            
    return " ".join(party_segments)

def analyze_accident(text):
    party1, party2 = extract_vehicles(text)
    
    ctx1 = get_party_context(text, party1, 1)
    ctx2 = get_party_context(text, party2, 2)

    # تحليل خصائص كل مركبة على حدة
    def parse_features(ctx, car_name):
        # البحث أيضاً في النطاق القريب من اسم السيارة في النص الأصلي لضمان عدم ضياع نقطة التصادم
        near_matches = re.findall(rf'.{{0,35}}{re.escape(car_name)}.{{0,45}}', text)
        combined = ctx + " " + " ".join(near_matches)
        
        return {
            "stopped": any(w in combined for w in ["وقوف", "متوقف", "واقف", "ثابت"]),
            "reversing": any(w in combined for w in ["رجوع", "بالرجوع", "يرجع", "للخلف"]),
            "swerving": any(w in combined for w in ["انحراف", "انحرفت", "دوران", "تغيير مسار", "تجاوز خاطئ"]),
            "wrong_way": any(w in combined for w in ["عكس السير", "عكس الاتجاه", "معاكس"]),
            "red_light": any(w in combined for w in ["قطع إشارة", "قاطع إشارة", "إشارة حمراء", "الاشارة حمراء"]),
            "wider_road": any(w in combined for w in ["اوسع", "أوسع", "رئيسي", "شارع عام"]),
            "narrow_road": any(w in combined for w in ["اضيق", "أضيق", "فرعي"]),
            "has_bump": "مطب" in combined,
            "hit_front": any(w in combined for w in ["مقدمه", "مقدمة", "الامام", "الأمام", "صدام امامي"]),
            "hit_side": any(w in combined for w in ["جانب", "الجانب", "جنب", "باب", "رفرف"]),
            "hit_rear": any(w in combined for w in ["مؤخرة", "مؤخره", "خلفية", "خلفيه", "صدام خلفي", "من الخلف"]),
            "dir_ns": ("شمال" in combined and "جنوب" in combined),
            "dir_ew": ("شرق" in combined and "غرب" in combined),
        }

    f1_feat = parse_features(ctx1, party1)
    f2_feat = parse_features(ctx2, party2)

    # القيم الافتراضية
    p1_fault, p2_fault = 50, 50
    article_num = "المادة (50) - الفقرة (1/1/6) من نظام المرور ولائحته التنفيذية"
    article_text = "تحدد أولوية المرور في التقاطعات غير المنظمة بإشارات أو لوحات مرورية وفقاً لقواعد الأفضلية العامة وأسبقية الوصول."
    application_text = "في حال التكافؤ في أولوية الطريق وعدم إمكانية تحديد أسبقية الدخول للتقاطع، توزع المسؤولية مناصفة بنسبة (50%) لكل طرف."
    technical_summary = f"تم رصد تعادل في المعطيات الميدانية بين المركبة الأولى ({party1}) والمركبة الثانية ({party2})."

    # 1. فحص حالات الوقوف التام أو الرجوع للخلف أو الانحراف (المادة 50 - فقرة 24/2)
    if f1_feat["reversing"] or f2_feat["reversing"] or f1_feat["swerving"] or f2_feat["swerving"] or f1_feat["stopped"] or f2_feat["stopped"]:
        if f2_feat["reversing"] or f2_feat["swerving"] or (f1_feat["stopped"] and not f2_feat["stopped"]):
            p1_fault, p2_fault = 0, 100
            fault_car, innocent_car = party2, party1
        elif f1_feat["reversing"] or f1_feat["swerving"] or (f2_feat["stopped"] and not f1_feat["stopped"]):
            p1_fault, p2_fault = 100, 0
            fault_car, innocent_car = party1, party2
        else:
            p1_fault, p2_fault = 0, 100
            fault_car, innocent_car = party2, party1

        article_num = "المادة (50) - الفقرة (24/2) من نظام المرور ولائحته التنفيذية"
        article_text = "على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو الدوران إلى الخلف في الاتجاه المعاكس لخط سيره مراعاة التأكد من إمكان إجراء ذلك دون خطر وإعطاء الإشارات اللازمة."
        application_text = f"تتحمل المركبة ({fault_car}) التي قامت بالحركة المتسببة (الرجوع للخلف / الانحراف) دون التأكد من خلو الطريق المسؤولية الكاملة بنسبة (100%)، بينما تعفى المركبة ({innocent_car}) لسلامة موقفها النظامي (0%)."
        technical_summary = f"ثبت من تحليل النص أن المركبة ({innocent_car}) كانت في وضع نظامي سليم، بينما قامت المركبة ({fault_car}) بحركة رجوع أو انحراف خاطئ أدى لوقوع الاصطدام."

    # 2. فحص قطع الإشارة أو عكس السير (100%)
    elif f1_feat["wrong_way"] or f2_feat["wrong_way"] or f1_feat["red_light"] or f2_feat["red_light"]:
        if f2_feat["wrong_way"] or f2_feat["red_light"]:
            p1_fault, p2_fault = 0, 100
            fault_car = party2
        else:
            p1_fault, p2_fault = 100, 0
            fault_car = party1

        article_num = "المادة (50) - جدول المخالفات رقم (6) من نظام المرور ولائحته التنفيذية"
        article_text = "يحظر على قائد المركبة السير بعكس اتجاه الحركة المقرر أو تجاوز الإشارة الضوئية أثناء الضوء الأحمر، ويلتزم بالتوقف التام قبل خط المشاة."
        application_text = f"تتحمل المركبة المخالفة ({fault_car}) كامل المسؤولية النظامية عن الحادث بنسبة (100%)."
        technical_summary = f"ثبت ارتكاب المركبة ({fault_car}) لمخالفة مرورية جسيمة (عكس السير / تجاوز الإشارة الحمراء) مما تسبب مباشرة في وقوع الحادث."

    # 3. فحص الاصطدام من الخلف - عدم ترك مسافة آمنة (المادة 50 - فقرة 12/2)
    elif ("من الخلف" in text or "مؤخرة" in text or "خلفي" in text) and not ("تقاطع" in text):
        if f1_feat["hit_rear"] or f2_feat["hit_front"]:
            p1_fault, p2_fault = 0, 100
            fault_car, front_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, front_car = party1, party2

        article_num = "المادة (50) - الفقرة (12/2) من نظام المرور ولائحته التنفيذية"
        article_text = "يجب على قائد المركبة ترك مسافة كافية بينه وبين المركبة التي أمامه، بحيث يمكنه التوقف بأمان في حال توقف المركبة الأمامية فجأة."
        application_text = f"تتحمل المركبة اللاحقة ({fault_car}) كامل المسؤولية النظامية بنسبة (100%) لعدم ترك المسافة النظامية الآمنة والاصطدام بمؤخرة المركبة الأمامية ({front_car})."
        technical_summary = f"اصطدام بمؤخرة المركبة الأمامية ({front_car}) نتيجة عدم ترك مسافة كافية من قِبل قائد المركبة اللاحقة ({fault_car})."

    # 4. التحليل الهندسي الدقيق لحوادث التقاطعات (100%، 75%، 50%، 25%)
    elif "تقاطع" in text or "التقاطع" in text:
        both_have_bumps = text.count("مطب") >= 2
        
        # تحديد من له أفضلية الطريق (أوسع / رئيسي / قادم من اليمين)
        p1_has_priority = f1_feat["wider_road"] or (f1_feat["dir_ns"] and f2_feat["dir_ew"])
        p2_has_priority = f2_feat["wider_road"] or (f2_feat["dir_ns"] and f1_feat["dir_ew"])

        # الحالة أ: الطرف الأول له الأفضلية (طريقه أوسع أو قادم من اليمين) ولكن يوجد مطبات أو صدم الطرف الثاني في جانبه (75% على الثاني و 25% على الأول)
        if p1_has_priority and (both_have_bumps or (f1_feat["hit_front"] and f2_feat["hit_side"])):
            p1_fault, p2_fault = 25, 75
            article_num = "المادة (50) - الفقرة (1/1/6) من نظام المرور ولائحته التنفيذية"
            article_text = "تكون الأفضلية في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، وعند تساوي الطرق تكون الأفضلية للقادم من جهة اليمين، مع التزام كافة المركبات بالتهدئة وأخذ الحيطة عند الاقتراب من التقاطعات والمطبات الصناعية."
            application_text = f"تتحمل المركبة ({party2}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية للمسار الأوسع والقادم من اليمين، وتتحمل المركبة ({party1}) نسبة (25%) لعدم التهدئة التامة عند المطب الصناعي والاصطدام بمقدمة كاملة في جانب المركبة الأخرى."
            technical_summary = f"المركبة ({party1}) تسير في المسار ذي الأفضلية (الأوسع/اليمين) واصطدمت بمقدمتها في جانب المركبة ({party2}) في منتصف التقاطع مع وجود مطبات تهدئة للطرفين."

        # الحالة ب: العكس - الطرف الثاني له الأفضلية مع اشتراك بنسبة 25%
        elif p2_has_priority and (both_have_bumps or (f2_feat["hit_front"] and f1_feat["hit_side"])):
            p1_fault, p2_fault = 75, 25
            article_num = "المادة (50) - الفقرة (1/1/6) من نظام المرور ولائحته التنفيذية"
            article_text = "تكون الأفضلية في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، وعند تساوي الطرق تكون الأفضلية للقادم من جهة اليمين، مع التزام كافة المركبات بالتهدئة وأخذ الحيطة عند الاقتراب من التقاطعات والمطبات الصناعية."
            application_text = f"تتحمل المركبة ({party1}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية، وتتحمل المركبة ({party2}) نسبة (25%) لعدم التهدئة التامة عند المطب الصناعي."
            technical_summary = f"المركبة ({party2}) تسير في المسار ذي الأفضلية مع وجود اشتراك جزئي في الخطأ لعدم التهدئة الكافية عند منطقة التقاطع."

        # الحالة ج: طريق رئيسي/أوسع واضح بدون مطبات للطرف الأول (100% على الطرف الثاني)
        elif p1_has_priority and not both_have_bumps:
            p1_fault, p2_fault = 0, 100
            article_num = "المادة (50) - الفقرة (2/1/6) من نظام المرور ولائحته التنفيذية"
            article_text = "على قائد المركبة القادم من طريق فرعي أو أضيق التوقف والتأكد التام من خلو الطريق الرئيسي أو الأوسع وإعطاء الأفضلية للمركبات السائرة فيه قبل الدخول إلى منطقة التقاطع."
            application_text = f"تتحمل المركبة ({party2}) كامل المسؤولية بنسبة (100%) لدخولها التقاطع من طريق أضيق دون التأكد من خلو الطريق الأوسع."
            technical_summary = f"المركبة ({party1}) تسير في طريق رئيسي/أوسع متمتعة بكامل الأفضلية النظامية، ودخلت عليها المركبة ({party2}) دون توقف."

        # الحالة د: تقاطع متساوي ولكن أحد الأطراف اجتاز التقاطع وانصدم في الجانب أو الخلفية (75% على الصادم بالمقدمة)
        elif f1_feat["hit_front"] and f2_feat["hit_side"] and not p1_has_priority:
            p1_fault, p2_fault = 75, 25
            article_num = "المادة (50) - الفقرة (1/1/6) من نظام المرور ولائحته التنفيذية (أسبقية الوصول للتقاطع)"
            article_text = "تكون الأولوية في التقاطعات المتساوية للمركبة التي سبقت بالدخول إلى منطقة التقاطع، ويجب على المركبات الأخرى التهدئة وإفساح المجال لها لإخلاء التقاطع."
            application_text = f"تتحمل المركبة ({party1}) نسبة (75%) لاصطدامها بمقدمتها في جانب المركبة ({party2}) التي سبقتها بالدخول للتقاطع، وتتحمل ({party2}) نسبة (25%) لعدم الحذر التام."
            technical_summary = f"تدل نقطة التصادم (مقدمة {party1} في جانب {party2}) على أسبقية دخول المركبة ({party2}) لمنطقة التقاطع."

    return party1, party2, p1_fault, p2_fault, article_num, article_text, application_text, technical_summary

# ---------------------------------------------------------
# 3. واجهة المستخدم (Streamlit UI)
# ---------------------------------------------------------
st.title("🚓 برنامج حَسْم الذكي")
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
        p1, p2, f1, f2, article_num, article_text, application_text, tech_summary = analyze_accident(accident_text)
        
        st.markdown("---")
        st.subheader("📋 التقرير النظامي المفصل للحادث")
        
        with st.expander("أولاً: التحليل الفني للحادث 🔍", expanded=True):
            st.write(f"**خلاصة الفحص الميداني:** {tech_summary}")
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
        
        # زر الطباعة الفعال عبر Streamlit Components (يستجيب فوراً على الجوال والكمبيوتر)
        components.html(
            """
            <script>
            function printReport() {
                window.parent.print();
            }
            </script>
            <button onclick="printReport()" style="
                background-color: #15803d;
                color: white;
                padding: 12px;
                text-align: center;
                border-radius: 8px;
                font-weight: bold;
                font-family: sans-serif;
                font-size: 16px;
                display: block;
                width: 100%;
                border: none;
                cursor: pointer;
            ">
                🖨️ طباعة التقرير الرسمي / حفظ كـ PDF
            </button>
            """,
            height=60
        )
