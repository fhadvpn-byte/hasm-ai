import streamlit as st
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="برنامج حَسْم الذكي", layout="centered")

css_style = (
    "<style>"
    ".stApp { direction: rtl; text-align: right; }"
    "p, div, h1, h2, h3, h4, span, label, textarea, li { text-align: right !important; direction: rtl !important; }"
    ".law-box { background-color: #1e293b; border-right: 4px solid #38bdf8; padding: 15px; border-radius: 8px; margin: 10px 0; color: #f8fafc; }"
    ".green-box { background-color: #0d2e1e; border-right: 5px solid #00a859; padding: 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 15px; }"
    "@media print { .stButton, textarea, header, footer, .stSelectbox { display: none !important; } }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

def normalize_ar(text):
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    return text

# 1. استخراج أسماء المركبات بدقة
def extract_vehicles(text):
    cars_list = [
        "اف جي", "إف جي", "صالون", "كامري", "يارس", "هايلكس", "لاندكروزر", 
        "جيب", "شاص", "ربع", "كورولا", "أكسنت", "اكسنت", "النترا", "إلنترا", 
        "سوناتا", "أزيرا", "ازيرا", "تاهو", "يوكن", "سوبربان", "كابرس", 
        "فورد", "تورس", "اكسبلورر", "إكسبلورر", "اكسبدشن", "مازدا", "نيسان", 
        "باترول", "صني", "التيما", "ألتيما", "مكسيما", "ددسن", "كيا", "سيراتو", 
        "أوبتيما", "كي 5", "سبورتاج", "شانجان", "ايدو", "إيدو", "جايكو", 
        "هافال", "جيلي", "ام جي", "إم جي", "لكزس", "مرسيدس", "بي ام", 
        "شاحنة", "شاحنه", "دينا", "تريلا", "قلاب", "وايت", "باص", "حافلة", "دباب", "دراجة"
    ]
    
    found_cars = []
    for car in cars_list:
        for match in re.finditer(re.escape(car), text):
            found_cars.append((match.start(), car))
    
    found_cars.sort(key=lambda x: x[0])
    
    unique_cars = []
    for pos, car in found_cars:
        norm_c = normalize_ar(car)
        if not any(norm_c in normalize_ar(u) or normalize_ar(u) in norm_c for u in unique_cars):
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

# 2. فصل جمل كل مركبة لمنع تداخل الأوصاف ونقاط التصادم
def extract_party_clauses(text, p1, p2):
    norm_text = normalize_ar(text)
    norm_p1 = normalize_ar(p1)
    norm_p2 = normalize_ar(p2)
    
    markers = []
    for m in re.finditer(re.escape(norm_p1) + r'|الاولي|الطرف الاول', norm_text):
        markers.append((m.start(), 1))
    for m in re.finditer(re.escape(norm_p2) + r'|الثانيه|الطرف الثاني', norm_text):
        markers.append((m.start(), 2))
        
    markers.sort(key=lambda x: x[0])
    
    p1_chunks, p2_chunks = [], []
    for i, (pos, party_id) in enumerate(markers):
        end_pos = markers[i+1][0] if i + 1 < len(markers) else len(norm_text)
        chunk = norm_text[pos:end_pos]
        if party_id == 1:
            p1_chunks.append(chunk)
        else:
            p2_chunks.append(chunk)
            
    return " ".join(p1_chunks), " ".join(p2_chunks)

# 3. المحرك القانوني والهندسي الدقيق حسب مواد نظام المرور السعودي
def analyze_accident(text, manual_mode="تحليل آلي من النص", law_override="تحديد آلي للمادة النظامية"):
    party1, party2 = extract_vehicles(text)
    norm_all = normalize_ar(text)
    p1_ctx, p2_ctx = extract_party_clauses(text, party1, party2)

    def get_props(ctx):
        return {
            "stopped": any(w in ctx for w in ["وقوف", "متوقف", "واقف", "ثابت"]),
            "reversing": any(w in ctx for w in ["رجوع", "بالرجوع", "يرجع", "للخلف", "ريوس"]),
            "swerving": any(w in ctx for w in ["انحراف", "انحرفت", "دوران", "تغيير مسار", "انتقال", "لف"]),
            "overtaking": any(w in ctx for w in ["تجاوز", "يتجاوز", "تخطي"]),
            "wrong_way": any(w in ctx for w in ["عكس السير", "عكس الاتجاه", "معاكس"]),
            "red_light": any(w in ctx for w in ["قطع اشاره", "قاطع اشاره", "اشاره حمراء"]),
            "wider": any(w in ctx for w in ["اوسع", "رئيسي", "شارع عام", "مزدوج"]),
            "bump": "مطب" in ctx,
            "front": any(w in ctx for w in ["مقدمه", "الامام", "صدام امامي", "وجهيه", "ركن امامي"]),
            "side": any(w in ctx for w in ["جانب", "جنب", "باب", "رفرف"]),
            "rear": any(w in ctx for w in ["مؤخره", "خلفيه", "صدام خلفي", "من الخلف"]),
            "ns": ("شمال" in ctx and "جنوب" in ctx),
            "ew": ("شرق" in ctx and "غرب" in ctx),
        }

    f1 = get_props(p1_ctx)
    f2 = get_props(p2_ctx)

    # القيم الافتراضية (المادة 56 - تقاطع متكافئ)
    p1_fault, p2_fault = 50, 50
    article_num = "المادة (56) - اللائحة التنفيذية (56/1) والفقرة (60/1) من نظام المرور السعودي"
    article_text = "تحدد أولوية المرور في التقاطعات غير المنظمة وفقاً لقواعد الأفضلية (الطريق الرئيسي، ثم الأوسع، ثم القادم من اليمين). وفي حال التكافؤ وتعذر تحديد الأسبقية توزع المسؤولية مناصفة."
    application_text = "نظراً لتكافؤ الأفضلية في منطقة التقاطع وعدم ثبوت أسبقية تامة لأحد الطرفين، توزع نسبة المسؤولية مناصفة (50%) لكل طرف."
    tech_summary = f"تم فحص مسارات المركبة الأولى ({party1}) والمركبة الثانية ({party2}) وتطبيق قواعد الأفضلية في التقاطعات."

    # 1. الرجوع إلى الخلف (المادة 54 - الفقرة 2)
    if f1["reversing"] or f2["reversing"] or "بالرجوع" in norm_all or "رجوع للخلف" in norm_all:
        if f2["reversing"] or (f1["stopped"] and not f2["stopped"]):
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (54) - الفقرة (2) واللائحة (50/1/24) من نظام المرور السعودي"
        article_text = "لا يجوز لقائد المركبة الرجوع إلى الخلف في الطرق العامة إلا عند الضرورة القصوى وبمسافة قصيرة، وبعد التأكد التام من خلو الطريق وعدم تعريض مستخدميه للخطر."
        application_text = f"تتحمل المركبة ({fault_car}) التي قامت بعملية الرجوع للخلف دون التأكد من خلو الطريق المسؤولية الكاملة بنسبة (100%)، وتُعفى المركبة ({ok_car}) لسلامة موقفها النظامي (0%)."
        tech_summary = f"ثبت قيام المركبة ({fault_car}) بالرجوع إلى الخلف والاصطدام بالمركبة ({ok_car})."

    # 2. الانحراف أو تغيير المسار أو الدوران غير النظامي (المادة 50 - الفقرة 1)
    elif f1["swerving"] or f2["swerving"] or "انحراف" in norm_all or "تغيير مسار" in norm_all:
        if f2["swerving"] or (f1["stopped"] and not f2["stopped"]):
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (50) - الفقرة (1/50) واللائحة (24/2) من نظام المرور السعودي"
        article_text = "يجب على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو تغيير مساره أو الدوران، التأكد من إمكانية إجراء ذلك دون خطر على غيره من مستخدمي الطريق وإعطاء الإشارات التنبيهية اللازمة."
        application_text = f"تتحمل المركبة ({fault_car}) كامل المسؤولية النظامية بنسبة (100%) للانحراف المفاجئ أو تغيير المسار دون التأكد من خلو الطريق."
        tech_summary = f"انحراف غير آمن من قِبل المركبة ({fault_car}) أدى للاصطدام بالمركبة ({ok_car}) السائرة في مسارها الصحيح."

    # 3. التجاوز الخاطئ (المادة 57)
    elif f1["overtaking"] or f2["overtaking"] or "تجاوز خاطئ" in norm_all:
        if f2["overtaking"]:
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (57) - اللائحة التنفيذية (57/1) من نظام المرور السعودي"
        article_text = "يجب على قائد المركبة قبل الشروع في التجاوز التأكد من أن الطريق مكشوف لمسافة كافية وأن المسار المراد الانتقال إليه خالٍ تماماً من المركبات القادمة."
        application_text = f"تتحمل المركبة ({fault_car}) المسؤولية الكاملة بنسبة (100%) للشروع في تجاوز غير آمن والتسبب في وقوع الحادث."
        tech_summary = f"قيام المركبة ({fault_car}) بالتجاوز في ظروف غير آمنة والاصطدام بالمركبة ({ok_car})."

    # 4. عكس السير أو تجاوز الإشارة الضوئية الحمراء (المادة 50/4 وجدول المخالفات)
    elif f1["wrong_way"] or f2["wrong_way"] or f1["red_light"] or f2["red_light"]:
        if f2["wrong_way"] or f2["red_light"]:
            p1_fault, p2_fault = 0, 100
            fault_car = party2
        else:
            p1_fault, p2_fault = 100, 0
            fault_car = party1
            
        article_num = "المادة (50/4) والمادة (68) - جدول المخالفات رقم (6) من نظام المرور السعودي"
        article_text = "يجب على قائدي المركبات الالتزام التام بإشارات المرور الضوئية واتجاهات السير المحددة، ويحظر قطع الإشارة الحمراء أو السير بعكس اتجاه الحركة."
        application_text = f"تتحمل المركبة المخالفة ({fault_car}) كامل المسؤولية النظامية عن الحادث بنسبة (100%)."
        tech_summary = f"ثبت ارتكاب المركبة ({fault_car}) لمخالفة مرورية موجبة للمسؤولية الكاملة (قطع إشارة / عكس سير)."

    # 5. عدم ترك مسافة آمنة - الاصطدام من الخلف (المادة 55)
    elif (f1["rear"] or f2["rear"] or "من الخلف" in norm_all) and ("تقاطع" not in norm_all):
        if f1["rear"] or (f2["front"] and not f1["front"]):
            p1_fault, p2_fault = 0, 100
            fault_car, front_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, front_car = party1, party2
            
        article_num = "المادة (55) - اللائحة التنفيذية (55/1) من نظام المرور السعودي"
        article_text = "على قائد المركبة أن يترك بينه وبين المركبة التي أمامه مسافة كافية تمكنه من التوقف بأمان في حال تهدئة المركبة الأمامية لسرعتها أو توقفها المفاجئ."
        application_text = f"تتحمل المركبة اللاحقة ({fault_car}) كامل المسؤولية النظامية بنسبة (100%) لعدم ترك المسافة الآمنة والاصطدام بمؤخرة المركبة الأمامية ({front_car})."
        tech_summary = f"اصطدام مقدمة المركبة اللاحقة ({fault_car}) بمؤخرة المركبة الأمامية ({front_car}) أثناء السير في نفس الاتجاه."

    # 6. حوادث الدوار (المادة 56 - الفقرة 6)
    elif "دوار" in norm_all or "الدوار" in norm_all:
        p1_fault, p2_fault = 0, 100
        article_num = "المادة (56) - الفقرة (6) من نظام المرور السعودي (أولوية الدوار)"
        article_text = "تكون أولوية المرور في الدوار للمركبات المتحركة داخله، وعلى المركبات القادمة من الطرق المؤدية إليه التوقف وإفساح المجال."
        application_text = f"تتحمل المركبة الداخلة إلى الدوار المسؤولية النظامية لعدم إعطاء الأفضلية للمركبة السائرة داخل الدوار."
        tech_summary = "حادث مروري في منطقة دوار نتيجة عدم مراعاة أولوية السير للمركبات داخل الدوار."

    # 7. حوادث التقاطعات وأولوية المرور (المادة 56 واللائحة 56/1 + المادة 60 لتوزيع النسب)
    elif "تقاطع" in norm_all:
        both_bumps = norm_all.count("مطب") >= 2
        p1_priority = f1["wider"] or (f1["ns"] and f2["ew"])
        p2_priority = f2["wider"] or (f2["ns"] and f1["ew"])

        # الحالة أ: الطرف الأول له أفضلية (طريق أوسع أو يمين) مع وجود مطبات أو اصطدام بمقدمته في جانب الثاني (25% - 75%)
        if p1_priority and (both_bumps or (f1["front"] and f2["side"])):
            p1_fault, p2_fault = 25, 75
            article_num = "المادة (56) - اللائحة (56/1) والمادة (60) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات غير المنظمة للمركبات في الطريق الرئيسي فالطريق الأوسع ثم للقادم من اليمين، مع وجوب التهدئة وأخذ الحيطة والحذر عند الاقتراب من التقاطعات والمطبات الصناعية."
            application_text = f"تتحمل المركبة ({party2}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية للمسار الأوسع والقادم من اليمين، وتتحمل المركبة ({party1}) نسبة (25%) للاشتراك في الخطأ لعدم التهدئة التامة عند المطب الصناعي والاصطدام بمقدمتها في جانب المركبة الأخرى."
            tech_summary = f"المركبة ({party1}) تسير في المسار ذي الأفضلية (الأوسع/اليمين) واصطدمت بمقدمتها في جانب المركبة ({party2}) بمنتصف التقاطع مع وجود مطبات صناعية."

        elif p2_priority and (both_bumps or (f2["front"] and f1["side"])):
            p1_fault, p2_fault = 75, 25
            article_num = "المادة (56) - اللائحة (56/1) والمادة (60) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات غير المنظمة للمركبات في الطريق الرئيسي فالطريق الأوسع ثم للقادم من اليمين، مع وجوب التهدئة وأخذ الحيطة والحذر عند الاقتراب من التقاطعات."
            application_text = f"تتحمل المركبة ({party1}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية، وتتحمل المركبة ({party2}) نسبة (25%) للاشتراك في الخطأ لعدم التهدئة الكافية."
            tech_summary = f"المركبة ({party2}) في المسار ذي الأفضلية مع وجود اشتراك جزئي في الخطأ عند منطقة التقاطع."

        elif p1_priority and not both_bumps:
            p1_fault, p2_fault = 0, 100
            article_num = "المادة (56) - الفقرة (2 و 4) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، ويجب على القادم من طريق فرعي أو أضيق التوقف التام وإفساح المجال."
            application_text = f"تتحمل المركبة ({party2}) كامل المسؤولية بنسبة (100%) لدخولها التقاطع من طريق أضيق دون التأكد من خلو الطريق الأوسع."
            tech_summary = f"دخول المركبة ({party2}) من طريق أضيق/فرعي أمام المركبة ({party1}) صاحبة الأفضلية المطلقة."

        elif p2_priority and not both_bumps:
            p1_fault, p2_fault = 100, 0
            article_num = "المادة (56) - الفقرة (2 و 4) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، ويجب على القادم من طريق فرعي أو أضيق التوقف التام وإفساح المجال."
            application_text = f"تتحمل المركبة ({party1}) كامل المسؤولية بنسبة (100%) لدخولها التقاطع دون إفساح المجال للمسار ذي الأفضلية."
            tech_summary = f"دخول المركبة ({party1}) أمام المركبة ({party2}) السائرة في الطريق الرئيسي/الأوسع."

        elif f1["front"] and f2["side"]:
            p1_fault, p2_fault = 75, 25
            article_num = "المادة (56) - اللائحة (56/1) من نظام المرور السعودي (أسبقية الدخول للتقاطع)"
            article_text = "في التقاطعات المتكافئة تكون الأولوية للمركبة التي سبقت بالدخول إلى منطقة التقاطع، ويجب على المركبات الأخرى التهدئة وإفساح المجال لها لإخلاء التقاطع."
            application_text = f"تتحمل المركبة ({party1}) نسبة (75%) لاصطدامها بمقدمتها في جانب المركبة ({party2}) التي سبقتها بالدخول واجتياز منتصف التقاطع، وتتحمل ({party2}) نسبة (25%) لعدم الحذر التام."
            tech_summary = f"نقطة التصادم (مقدمة {party1} في جانب {party2}) تثبت أسبقية دخول المركبة ({party2}) لمنطقة التقاطع."

    # تطبيق اختيار المادة اليدوي إذا حدده المباشر
    law_dict = {
        "المادة (56) - أفضلية التقاطعات والطرق الرئيسية": (
            "المادة (56) - اللائحة التنفيذية (56/1) من نظام المرور السعودي",
            "تكون أولوية المرور في التقاطعات غير المنظمة للمركبات في الطريق الرئيسي، فالطريق الأوسع، ثم للقادم من اليمين، مع مراعاة أسبقية الدخول للتقاطع ووجوب التهدئة عند المطبات الصناعية."
        ),
        "المادة (54) - الرجوع إلى الخلف": (
            "المادة (54) - الفقرة (2) من نظام المرور السعودي",
            "لا يجوز لقائد المركبة الرجوع إلى الخلف في الطرق العامة إلا عند الضرورة وبمسافة قصيرة وبعد التأكد التام من خلو الطريق."
        ),
        "المادة (50) - الانحراف وتغيير المسار والدوران": (
            "المادة (50) - الفقرة (1/50) واللائحة (24/2) من نظام المرور السعودي",
            "على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو الدوران أو تغيير المسار التأكد من إمكان إجراء ذلك دون خطر وإعطاء الإشارات اللازمة."
        ),
        "المادة (55) - عدم ترك مسافة آمنة (الاصطدام من الخلف)": (
            "المادة (55) - اللائحة التنفيذية (55/1) من نظام المرور السعودي",
            "يجب على قائد المركبة ترك مسافة كافية بينه وبين المركبة التي أمامه تمكنه من التوقف بأمان في حال توقف المركبة الأمامية فجأة."
        ),
        "المادة (57) - التجاوز الخاطئ": (
            "المادة (57) - اللائحة التنفيذية (57/1) من نظام المرور السعودي",
            "يجب على قائد المركبة قبل الشروع في التجاوز التأكد من خلو المسار وعدم تعريض المركبات القادمة أو المتجاوزة للخطر."
        ),
        "المادة (50/4) - قطع الإشارة الضوئية أو عكس السير": (
            "المادة (50/4) والمادة (68) - جدول المخالفات رقم (6) من نظام المرور السعودي",
            "يحظر على قائد المركبة تجاوز الإشارة الضوئية الحمراء أو السير بعكس اتجاه الحركة المقرر في الطريق."
        )
    }
    
    if law_override != "تحديد آلي للمادة النظامية":
        article_num, article_text = law_dict[law_override]

    if manual_mode != "تحليل آلي من النص":
        Map_Manual = {
            "الطرف الأول (0%) - الطرف الثاني (100%)": (0, 100),
            "الطرف الأول (25%) - الطرف الثاني (75%)": (25, 75),
            "الطرف الأول (50%) - الطرف الثاني (50%)": (50, 50),
            "الطرف الأول (75%) - الطرف الثاني (25%)": (75, 25),
            "الطرف الأول (100%) - الطرف الثاني (0%)": (100, 0),
        }
        p1_fault, p2_fault = Map_Manual[manual_mode]
        application_text = f"بناءً على المعاينة الفنية الميدانية وتطبيق {article_num}، تتحمل المركبة الأولى ({party1}) نسبة ({p1_fault}%)، وتتحمل المركبة الثانية ({party2}) نسبة ({p2_fault}%)."

    return party1, party2, p1_fault, p2_fault, article_num, article_text, application_text, tech_summary

# ---------------------------------------------------------
# واجهة المستخدم
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
    height=150
)

col1, col2 = st.columns(2)
with col1:
    manual_override = st.selectbox(
        "📊 تقدير النسب (آلي أو يدوي):",
        [
            "تحليل آلي من النص",
            "الطرف الأول (25%) - الطرف الثاني (75%)",
            "الطرف الأول (0%) - الطرف الثاني (100%)",
            "الطرف الأول (50%) - الطرف الثاني (50%)",
            "الطرف الأول (75%) - الطرف الثاني (25%)",
            "الطرف الأول (100%) - الطرف الثاني (0%)"
        ]
    )
with col2:
    law_override = st.selectbox(
        "⚖️ السند النظامي (آلي أو يدوي):",
        [
            "تحديد آلي للمادة النظامية",
            "المادة (56) - أفضلية التقاطعات والطرق الرئيسية",
            "المادة (54) - الرجوع إلى الخلف",
            "المادة (50) - الانحراف وتغيير المسار والدوران",
            "المادة (55) - عدم ترك مسافة آمنة (الاصطدام من الخلف)",
            "المادة (57) - التجاوز الخاطئ",
            "المادة (50/4) - قطع الإشارة الضوئية أو عكس السير"
        ]
    )

analyze_btn = st.button("🔍 تحليل الحادث وتوزيع النسب بدقة", use_container_width=True)
clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

if analyze_btn:
    if accident_text.strip() == "":
        st.warning("يرجى إدخال تفاصيل الحادث أولاً.")
    else:
        p1, p2, f1, f2, article_num, article_text, application_text, tech_summary = analyze_accident(accident_text, manual_override, law_override)
        
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
