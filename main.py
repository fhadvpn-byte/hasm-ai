import streamlit as st
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="برنامج حَسْم الذكي", layout="centered")

css_style = (
    "<style>"
    ".stApp { direction: rtl; text-align: right; }"
    "p, div, h1, h2, h3, h4, span, label, textarea, li, th, td { text-align: right !important; direction: rtl !important; }"
    ".law-box { background-color: #1e293b; border-right: 4px solid #38bdf8; padding: 16px; border-radius: 8px; margin: 12px 0; color: #f8fafc; line-height: 1.7; }"
    ".green-box { background-color: #0d2e1e; border-right: 5px solid #00a859; padding: 20px; border-radius: 10px; margin-top: 15px; margin-bottom: 15px; }"
    ".official-table { width: 100%; border-collapse: collapse; margin: 15px 0; background-color: #111827; border-radius: 8px; overflow: hidden; }"
    ".official-table th { background-color: #1f2937; color: #38bdf8; padding: 10px; border: 1px solid #374151; }"
    ".official-table td { padding: 10px; border: 1px solid #374151; color: #e5e7eb; }"
    "@media print { .stButton, textarea, header, footer, .no-print { display: none !important; } }"
    "</style>"
)
st.markdown(css_style, unsafe_allow_html=True)

# توحيد الحروف وتحويل الأرقام الهندية (٥) إلى أرقام قياسية (5) لضمان دقة القراءة
def normalize_ar(text):
    arabic_nums = "٠١٢٣٤٥٦٧٨٩"
    english_nums = "0123456789"
    trans_table = str.maketrans(arabic_nums, english_nums)
    text = text.translate(trans_table)
    text = re.sub(r'[أإآ]', 'ا', text)
    text = re.sub(r'ة', 'ه', text)
    text = re.sub(r'ى', 'ي', text)
    text = text.replace("مؤحره", "مؤخره").replace("موحره", "مؤخره").replace("موخره", "مؤخره")
    return text

def extract_vehicles(text):
    cars_list = [
        "اف جي", "إف جي", "صالون", "كامري", "يارس", "هايلكس", "لاندكروزر", 
        "جيب", "شاص", "ربع", "كورولا", "أكسنت", "اكسنت", "النترا", "إلنترا", 
        "سوناتا", "أزيرا", "ازيرا", "تاهو", "يوكن", "سوبربان", "كابرس", 
        "فورد", "تورس", "اكسبلورر", "إكسبلورر", "اكسبدشن", "مازدا", "نيسان", 
        "باترول", "صني", "التيما", "ألتيما", "مكسيما", "ددسن", "كيا", "سيراتو", 
        "أوبتيما", "كي 5", "سبورتاج", "شانجان", "ايدو", "إيدو", "جايكو", 
        "هافال", "جيلي", "ام جي", "إم جي", "لكزس", "مرسيدس", "بي ام", 
        "شاحنة", "شاحنه", "دينا", "تريلا", "قلاب", "وايت", "باص", "حافلة", 
        "دباب", "دراجة", "بيك اب", "ونيت", "سيدان"
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
        p1 = match1.group(1).strip() if match1 else "المركبة الأولى (الأمامية)"
        p2 = match2.group(1).strip() if match2 else "المركبة الثانية (اللاحقة)"
        return p1, p2

def extract_party_clauses(text, p1, p2):
    norm_text = normalize_ar(text)
    norm_p1 = normalize_ar(p1.split()[0])
    norm_p2 = normalize_ar(p2.split()[0])
    
    markers = []
    for m in re.finditer(re.escape(norm_p1) + r'|الاولي|الطرف الاول|الاماميه|الامامي', norm_text):
        markers.append((m.start(), 1))
    for m in re.finditer(re.escape(norm_p2) + r'|الثانيه|الطرف الثاني|الخلفيه|اللاحقه', norm_text):
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

def get_damage_desc(ctx):
    if "مقدمه سليمه" in ctx or "مقدمتها سليمه" in ctx:
        return "المؤخرة فقط (المقدمة سليمة)"
    elif "مقدمه كامله" in ctx:
        return "المقدمة الكاملة"
    elif "مقدمه" in ctx or "الامام" in ctx or "صدام امامي" in ctx:
        return "المقدمة الأمامية"
    elif "الجانب الايمن" in ctx or "جنب ايمن" in ctx or ("يمين" in ctx and "جانب" in ctx):
        return "الجانب الأيمن"
    elif "الجانب الايسر" in ctx or "جنب ايسر" in ctx or ("يسار" in ctx and "جانب" in ctx):
        return "الجانب الأيسر"
    elif "جانب" in ctx or "جنب" in ctx or "باب" in ctx or "رفرف" in ctx:
        return "الجانب"
    elif "مؤخره" in ctx or "خلفيه" in ctx or "من الخلف" in ctx:
        return "المؤخرة الخلفية"
    return "حسب المعاينة الميدانية"

# استخراج أرقام المركبات المستثناة في حوادث التتابع (التي تركت مسافة آمنة واندفعت قسراً)
def extract_pushed_vehicles(norm_text, total_vehicles):
    pushed_list = []
    # البحث عن نمط: (المركبه رقم 5 ... مسافه امنه / قوه الاندفاع / متوقفه)
    matches = re.finditer(r'(?:المركبه|مركبه|السياره|سياره|الطرف|رقم)\s*(?:رقم\s*)?(\d+)', norm_text)
    for m in matches:
        v_num = int(m.group(1))
        if 1 < v_num <= total_vehicles:
            # فحص النص القريب من رقم المركبة
            start_idx = max(0, m.start() - 20)
            end_idx = min(len(norm_text), m.end() + 90)
            window = norm_text[start_idx:end_idx]
            if any(w in window for w in ["مسافه امنه", "الاندفاع", "اندفاع", "دفعت", "متوقفه", "واقفه", "نظاميه"]):
                if v_num not in pushed_list:
                    pushed_list.append(v_num)
    return pushed_list

def analyze_accident(text, manual_mode="آلي", law_override="آلي"):
    norm_all = normalize_ar(text)
    
    # فحص هل الحادث "تتابع مركبات"
    num_match = re.search(r'(\d+)\s*(?:مركبات|سيارات|اطراف|مركبه|سياره)', norm_all)
    num_vehicles = int(num_match.group(1)) if num_match else 2
    is_chain_accident = any(w in norm_all for w in ["تتابع", "متتاليه", "التي امامه", "التي امامها", "كل مركبه"]) or num_vehicles > 2

    # ---------------------------------------------------------
    # أولاً: معالجة حوادث التتابع (مع دعم استثناء المركبات المندفعة قسراً)
    # ---------------------------------------------------------
    if is_chain_accident and "تقاطع" not in norm_all:
        pushed_cars = extract_pushed_vehicles(norm_all, num_vehicles)
        
        if pushed_cars:
            exempt_str = "، والمركبة رقم (" + ") ورقم (".join(map(str, pushed_cars)) + ")"
            party1 = f"المركبة رقم (1){exempt_str} - (مُعفاة)"
            faulty_nums = [str(i) for i in range(2, num_vehicles + 1) if i not in pushed_cars]
            party2 = f"المركبات المتسببة رقم ({'، '.join(faulty_nums)})"
            
            article_num = "المادة (55) - اللائحة (55/1) والمادة (60) من نظام المرور السعودي (قاعدة التتابع والاندفاع القسري)"
            article_text = "على قائد المركبة ترك مسافة كافية بينه وبين المركبة التي أمامه تمكنه من التوقف بأمان. وفي حوادث التتابع يتحمل كل سائق مسؤولية ما أحدثه من أضرار في المركبة التي أمامه، ويُستثنى من ذلك المركبة التي يثبت توقفها النظامي وتركها مسافة آمنة حيث تنتقل مسؤولية اندفاعها القسري على المركبة الصادمة لها من الخلف."
            
            pushed_details = []
            for pc in pushed_cars:
                pusher = pc + 1 if pc + 1 <= num_vehicles else pc
                front_target = pc - 1
                pushed_details.append(
                    f"تُعفى المركبة رقم ({pc}) من المسؤولية بنسبة (0%) لثبوت تركها مسافة آمنة واندفاعها قسراً، وتتحمل المركبة رقم ({pusher}) كامل المسؤولية (100%) عن أضرار المركبة ({pc}) وما نتج عن اندفاعها من صدم لمؤخرة المركبة رقم ({front_target})"
                )
            pushed_Rule_str = "، كما ".join(pushed_details) + "."
            
            application_text = (
                f"تُعفى المركبة الأمامية رقم (1) بنسبة (0%) لسلامة موقفها، {pushed_Rule_str} "
                f"بينما تتحمل بقية المركبات اللاحقة نسبة (100%) لكل مركبة عما أحدثته من تلفيات في مؤخرة المركبة التي أمامها مباشرة."
            )
            tech_summary = (
                f"حادث تصادم متتالي مكون من ({num_vehicles}) مركبات؛ ثبت فنياً سلامة موقف المركبة الأولى رقم (1)، "
                f"وثبت أن المركبة رقم ({'، '.join(map(str, pushed_cars))}) كانت متوقفة بمسافة آمنة واندفعت قسراً بفعل الاصطدام الخلفي المباشر."
            )
        else:
            party1 = "المركبة رقم (1) - الأمامية"
            party2 = f"المركبات اللاحقة من (2) إلى ({num_vehicles})" if num_vehicles > 2 else "المركبة رقم (2) - الخلفية"
            article_num = "المادة (55) - اللائحة التنفيذية (55/1) والمادة (60) من نظام المرور السعودي"
            article_text = "على قائد المركبة أن يترك بينه وبين المركبة التي أمامه مسافة كافية تمكنه من التوقف بأمان في حال تهدئة المركبة الأمامية لسرعتها أو توقفها المفاجئ، وفي حوادث التتابع يتحمل قائد كل مركبة لاحقة مسؤولية الاصطدام بمؤخرة المركبة التي أمامه."
            application_text = (
                f"تُعفى المركبة الأمامية الأولى رقم (1) من المسؤولية تماماً بنسبة (0%) لسلامة مقدمتها وثبات مسارها، "
                f"بينما تتحمل كل مركبة من المركبات اللاحقة (من المركبة 2 إلى المركبة {num_vehicles}) نسبة (100%) عن الأضرار التي أحدثتها بمقدمتها في مؤخرة المركبة التي أمامها مباشرة لعدم ترك المسافة النظامية الآمنة."
            )
            tech_summary = f"حادث تصادم متتالي (تتابع) مكون من ({num_vehicles}) مركبات في مسار واحد؛ ثبت فيه سلامة مقدمة المركبة الأولى، واصطدام كل مركبة لاحقة بمؤخرة المركبة التي أمامها نتيجة عدم ترك المسافة الآمنة."

        p1_fault = 0
        p2_fault = 100
        dmg1 = "المؤخرة الخلفية (المقدمة سليمة)"
        dmg2 = "المقدمة الأمامية (والمؤخرة لما تلاها)"
        
        return party1, party2, p1_fault, p2_fault, article_num, article_text, application_text, tech_summary, dmg1, dmg2, num_vehicles, True, pushed_cars

    # ---------------------------------------------------------
    # ثانياً: معالجة الحوادث الثنائية المعتادة
    # ---------------------------------------------------------
    party1, party2 = extract_vehicles(text)
    p1_ctx, p2_ctx = extract_party_clauses(text, party1, party2)

    def get_props(ctx):
        return {
            "stopped": any(w in ctx for w in ["وقوف", "متوقف", "واقف", "ثابت", "سليمه"]),
            "reversing": any(w in ctx for w in ["رجوع", "بالرجوع", "يرجع", "للخلف", "ريوس"]),
            "swerving": any(w in ctx for w in ["انحراف", "انحرفت", "دوران", "تغيير مسار", "انتقال", "لف"]),
            "overtaking": any(w in ctx for w in ["تجاوز", "يتجاوز", "تخطي"]),
            "wrong_way": any(w in ctx for w in ["عكس السير", "عكس الاتجاه", "معاكس"]),
            "red_light": any(w in ctx for w in ["قطع اشاره", "قاطع اشاره", "اشاره حمراء"]),
            "wider": any(w in ctx for w in ["اوسع", "رئيسي", "شارع عام", "مزدوج"]),
            "narrow": any(w in ctx for w in ["اضيق", "فرعي"]),
            "bump": "مطب" in ctx,
            "front": any(w in ctx for w in ["مقدمه", "الامام", "صدام امامي", "وجهيه", "ركن امامي"]),
            "side": any(w in ctx for w in ["جانب", "جنب", "باب", "رفرف"]),
            "rear": any(w in ctx for w in ["مؤخره", "خلفيه", "صدام خلفي", "من الخلف"]),
            "ns": ("شمال" in ctx and "جنوب" in ctx),
            "ew": ("شرق" in ctx and "غرب" in ctx),
            "damage": get_damage_desc(ctx)
        }

    f1 = get_props(p1_ctx)
    f2 = get_props(p2_ctx)

    p1_fault, p2_fault = 50, 50
    article_num = "المادة (56) - اللائحة التنفيذية (56/1) والمادة (60/1) من نظام المرور السعودي"
    article_text = "تحدد أولوية المرور في التقاطعات غير المنظمة وفقاً لقواعد الأفضلية الرسمية (الطريق الرئيسي، ثم الطريق الأوسع، ثم القادم من جهة اليمين). وفي حال تكافؤ الأفضلية وتعذر تحديد أسبقية الدخول توزع المسؤولية مناصفة."
    application_text = "نظراً لتكافؤ الأفضلية وعدم ثبوت أسبقية تامة لأحد الطرفين، توزع نسبة المسؤولية مناصفة (50%) لكل طرف عملاً بالمادة (60) من النظام."
    tech_summary = f"تم فحص مسارات المركبة الأولى ({party1}) والمركبة الثانية ({party2}) ومطابقة نقاط التصادم."

    # 1. الاصطدام من الخلف - عدم ترك مسافة آمنة (المادة 55)
    if any(w in norm_all for w in ["مؤخره", "خلفيه", "من الخلف", "صدام خلفي", "الاماميه", "امامه", "امامها", "مسافه امنه"]) and ("تقاطع" not in norm_all) and not (f1["reversing"] or f2["reversing"] or "رجوع" in norm_all):
        if f2["rear"] and f1["front"] and not f1["rear"]:
            p1_fault, p2_fault = 100, 0
            fault_car, front_car = party1, party2
            f1["damage"], f2["damage"] = "المقدمة الأمامية", "المؤخرة الخلفية"
        else:
            p1_fault, p2_fault = 0, 100
            fault_car, front_car = party2, party1
            if f1["damage"] == "حسب المعاينة الميدانية": f1["damage"] = "المؤخرة الخلفية (المقدمة سليمة)"
            if f2["damage"] == "حسب المعاينة الميدانية": f2["damage"] = "المقدمة الأمامية"
            
        article_num = "المادة (55) - اللائحة التنفيذية (55/1) والمادة (60) من نظام المرور السعودي"
        article_text = "على قائد المركبة أن يترك بينه وبين المركبة التي أمامه مسافة كافية تمكنه من التوقف بأمان في حال تهدئة المركبة الأمامية لسرعتها أو توقفها المفاجئ."
        application_text = f"تُعفى المركبة الأمامية ({front_car}) من المسؤولية تماماً بنسبة (0%)، وتتحمل المركبة اللاحقة ({fault_car}) كامل المسؤولية النظامية بنسبة (100%) لعدم ترك المسافة النظامية الآمنة والاصطدام بمؤخرة المركبة التي أمامها."
        tech_summary = f"اصطدام مقدمة المركبة اللاحقة ({fault_car}) بمؤخرة المركبة الأمامية ({front_car}) أثناء السير في ذات المسار نتيجة عدم ترك مسافة آمنة."

    # 2. الرجوع إلى الخلف (المادة 54 - الفقرة 2)
    elif f1["reversing"] or f2["reversing"] or "بالرجوع" in norm_all or "رجوع للخلف" in norm_all:
        if f2["reversing"] or (f1["stopped"] and not f2["stopped"]):
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (54) - الفقرة (2) واللائحة (50/1/24) والمادة (60) من نظام المرور السعودي"
        article_text = "لا يجوز لقائد المركبة الرجوع إلى الخلف في الطرق العامة إلا عند الضرورة القصوى وبمسافة قصيرة، وبعد التأكد التام من خلو الطريق وعدم تعريض مستخدميه للخطر."
        application_text = f"تتحمل المركبة ({fault_car}) التي قامت بعملية الرجوع للخلف دون التأكد من خلو الطريق المسؤولية الكاملة بنسبة (100%)، وتُعفى المركبة ({ok_car}) لسلامة موقفها النظامي (0%)."
        tech_summary = f"ثبت من المعاينة الفنية أن المركبة ({ok_car}) كانت في وضع نظامي سليم، بينما قامت المركبة ({fault_car}) بالرجوع إلى الخلف والاصطدام بها."

    # 3. الانحراف أو تغيير المسار أو الدوران (المادة 50 - الفقرة 1)
    elif f1["swerving"] or f2["swerving"] or "انحراف" in norm_all or "تغيير مسار" in norm_all:
        if f2["swerving"] or (f1["stopped"] and not f2["stopped"]):
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (50) - الفقرة (1/50) واللائحة (24/2) والمادة (60) من نظام المرور السعودي"
        article_text = "يجب على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو تغيير مساره أو الدوران إلى الخلف، التأكد من إمكانية إجراء ذلك دون خطر على غيره من مستخدمي الطريق وإعطاء الإشارات التنبيهية اللازمة."
        application_text = f"تتحمل المركبة ({fault_car}) كامل المسؤولية النظامية بنسبة (100%) للانحراف أو تغيير المسار دون التأكد من خلو الطريق، وتعفى المركبة ({ok_car}) بنسبة (0%)."
        tech_summary = f"انحراف غير آمن من قِبل المركبة ({fault_car}) أدى لقطع مسار المركبة ({ok_car}) ووقوع الاصطدام."

    # 4. التجاوز الخاطئ (المادة 57)
    elif f1["overtaking"] or f2["overtaking"] or "تجاوز خاطئ" in norm_all:
        if f2["overtaking"]:
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (57) - اللائحة التنفيذية (57/1) والمادة (60) من نظام المرور السعودي"
        article_text = "يجب على قائد المركبة قبل الشروع في التجاوز التأكد من أن الطريق مكشوف لمسافة كافية وأن المسار المراد الانتقال إليه خالٍ تماماً من المركبات القادمة."
        application_text = f"تتحمل المركبة ({fault_car}) المسؤولية الكاملة بنسبة (100%) للشروع في تجاوز غير آمن والتسبب المباشر في وقوع الحادث."
        tech_summary = f"قيام المركبة ({fault_car}) بالتجاوز الخاطئ في ظروف غير آمنة والاصطدام بالمركبة ({ok_car})."

    # 5. عكس السير أو قطع الإشارة الحمراء (المادة 50/4 والمادة 68)
    elif f1["wrong_way"] or f2["wrong_way"] or f1["red_light"] or f2["red_light"] or "عكس السير" in norm_all or "قطع اشاره" in norm_all:
        if f2["wrong_way"] or f2["red_light"]:
            p1_fault, p2_fault = 0, 100
            fault_car, ok_car = party2, party1
        else:
            p1_fault, p2_fault = 100, 0
            fault_car, ok_car = party1, party2
            
        article_num = "المادة (50/4) والمادة (68) - جدول المخالفات رقم (6) من نظام المرور السعودي"
        article_text = "يجب على قائدي المركبات الالتزام التام بإشارات المرور الضوئية واتجاهات السير المحددة، ويحظر قطع الإشارة الحمراء أو السير بعكس اتجاه الحركة المقرر."
        application_text = f"تتحمل المركبة المخالفة ({fault_car}) كامل المسؤولية النظامية عن الحادث بنسبة (100%)، وتعفى المركبة ({ok_car}) بنسبة (0%)."
        tech_summary = f"ثبت ارتكاب المركبة ({fault_car}) لمخالفة مرورية جسيمة (قطع إشارة حمراء / عكس سير) تسببت في الحادث."

    # 6. حوادث الدوار (المادة 56 - الفقرة 6)
    elif "دوار" in norm_all or "الدوار" in norm_all:
        p1_fault, p2_fault = 0, 100
        article_num = "المادة (56) - الفقرة (6) من نظام المرور السعودي (أولوية السير في الدوار)"
        article_text = "تكون أولوية المرور في الدوار للمركبات المتحركة داخله، وعلى المركبات القادمة من الطرق الفرعية أو المؤدية إليه التوقف التام وإفساح المجال."
        application_text = "تتحمل المركبة الداخلة إلى الدوار دون إفساح المجال المسؤولية النظامية الكاملة (100%)."
        tech_summary = "حادث مروري في منطقة دوار نتيجة عدم مراعاة أولوية السير للمركبات المتحركة داخل الدوار."

    # 7. حوادث التقاطعات (المادة 56 واللائحة 56/1 + المادة 60)
    elif "تقاطع" in norm_all:
        both_bumps = norm_all.count("مطب") >= 2
        p1_priority = f1["wider"] or f2["narrow"] or (f1["ns"] and f2["ew"])
        p2_priority = f2["wider"] or f1["narrow"] or (f2["ns"] and f1["ew"])

        if p1_priority and (both_bumps or (f1["front"] and f2["side"])):
            p1_fault, p2_fault = 25, 75
            article_num = "المادة (56) - اللائحة التنفيذية (56/1) والمادة (60/1) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات غير المنظمة للمركبات السائرة في الطريق الرئيسي، فالطريق الأوسع، ثم للقادم من جهة اليمين، مع وجوب التهدئة وأخذ الحيطة والحذر التام عند الاقتراب من التقاطعات والمطبات الصناعية."
            application_text = f"استناداً للمادة (56) والمادة (60)، تتحمل المركبة ({party2}) نسبة (75%) لدخولها منطقة التقاطع دون إعطاء الأفضلية للمركبة السائرة في الطريق الأوسع والقادمة من اليمين، وتتحمل المركبة ({party1}) نسبة (25%) للاشتراك في الخطأ لعدم التهدئة التامة عند المطب الصناعي والاصطدام بـ ({f1['damage']}) في ({f2['damage']}) للمركبة الأخرى."
            tech_summary = f"المركبة الأولى ({party1}) تسير في المسار ذي الأفضلية النظامية (الأوسع/اليمين) واصطدمت بـ ({f1['damage']}) في ({f2['damage']}) للمركبة الثانية ({party2}) في منتصف التقاطع مع وجود مطبات تهدئة للطرفين."

        elif p2_priority and (both_bumps or (f2["front"] and f1["side"])):
            p1_fault, p2_fault = 75, 25
            article_num = "المادة (56) - اللائحة التنفيذية (56/1) والمادة (60/1) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات غير المنظمة للمركبات السائرة في الطريق الرئيسي، فالطريق الأوسع، ثم للقادم من جهة اليمين، مع وجوب التهدئة وأخذ الحيطة والحذر عند الاقتراب من التقاطعات."
            application_text = f"استناداً للمادة (56) والمادة (60)، تتحمل المركبة ({party1}) نسبة (75%) لدخولها التقاطع دون إعطاء الأفضلية النظامية، وتتحمل المركبة ({party2}) نسبة (25%) للاشتراك في الخطأ لعدم التهدئة الكافية عند التقاطع."
            tech_summary = f"المركبة الثانية ({party2}) تسير في المسار ذي الأفضلية النظامية واصطدمت بـ ({f2['damage']}) في ({f1['damage']}) للمركبة الأولى ({party1})."

        elif p1_priority and not both_bumps:
            p1_fault, p2_fault = 0, 100
            article_num = "المادة (56) - الفقرة (2 و 4) والمادة (60) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، ويجب على القادم من طريق فرعي أو أضيق التوقف التام والتأكد من خلو التقاطع قبل الدخول إليه."
            application_text = f"تتحمل المركبة ({party2}) كامل المسؤولية بنسبة (100%) لدخولها التقاطع من طريق أضيق دون إفساح المجال، وتعفى المركبة ({party1}) بنسبة (0%)."
            tech_summary = f"دخول المركبة ({party2}) من مسار أضيق/فرعي أمام المركبة ({party1}) المتمتعة بكامل الأفضلية النظامية."

        elif p2_priority and not both_bumps:
            p1_fault, p2_fault = 100, 0
            article_num = "المادة (56) - الفقرة (2 و 4) والمادة (60) من نظام المرور السعودي"
            article_text = "تكون أولوية المرور في التقاطعات للمركبات السائرة في الطريق الرئيسي أو الأوسع، ويجب على القادم من طريق فرعي أو أضيق التوقف التام وإفساح المجال."
            application_text = f"تتحمل المركبة ({party1}) كامل المسؤولية بنسبة (100%) لدخولها التقاطع دون إفساح المجال للمسار ذي الأفضلية."
            tech_summary = f"دخول المركبة ({party1}) أمام المركبة ({party2}) السائرة في الطريق الرئيسي/الأوسع."

        elif f1["front"] and f2["side"]:
            p1_fault, p2_fault = 75, 25
            article_num = "المادة (56) - اللائحة التنفيذية (56/1) والمادة (60) من نظام المرور السعودي (أسبقية الدخول)"
            article_text = "في التقاطعات المتكافئة تكون الأولوية للمركبة التي سبقت بالدخول إلى منطقة التقاطع، ويجب على المركبات الأخرى التهدئة وإفساح المجال لها لإخلاء التقاطع بأمان."
            application_text = f"تتحمل المركبة ({party1}) نسبة (75%) لاصطدامها بـ ({f1['damage']}) في ({f2['damage']}) للمركبة ({party2}) التي سبقتها بالدخول واجتياز منتصف التقاطع، وتتحمل ({party2}) نسبة (25%) لعدم الحذر التام."
            tech_summary = f"نقطة التصادم ({f1['damage']} للمركبة {party1} في {f2['damage']} للمركبة {party2}) تثبت فنياً أسبقية دخول المركبة ({party2}) لمنطقة التقاطع."

    law_dict = {
        "المادة (55) - عدم ترك مسافة آمنة (الاصطدام من الخلف / التتابع)": (
            "المادة (55) - اللائحة التنفيذية (55/1) والمادة (60) من نظام المرور السعودي",
            "يجب على قائد المركبة ترك مسافة كافية بينه وبين المركبة التي أمامه تمكنه من التوقف بأمان في حال توقف المركبة الأمامية فجأة."
        ),
        "المادة (56) - أفضلية التقاطعات والطرق الرئيسية": (
            "المادة (56) - اللائحة التنفيذية (56/1) والمادة (60) من نظام المرور السعودي",
            "تكون أولوية المرور في التقاطعات غير المنظمة للمركبات في الطريق الرئيسي، فالطريق الأوسع، ثم للقادم من اليمين، مع مراعاة أسبقية الدخول للتقاطع ووجوب التهدئة عند المطبات الصناعية."
        ),
        "المادة (54) - الرجوع إلى الخلف": (
            "المادة (54) - الفقرة (2) والمادة (60) من نظام المرور السعودي",
            "لا يجوز لقائد المركبة الرجوع إلى الخلف في الطرق العامة إلا عند الضرورة وبمسافة قصيرة وبعد التأكد التام من خلو الطريق."
        ),
        "المادة (50) - الانحراف وتغيير المسار والدوران": (
            "المادة (50) - الفقرة (1/50) واللائحة (24/2) من نظام المرور السعودي",
            "على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو الدوران أو تغيير المسار التأكد من إمكان إجراء ذلك دون خطر وإعطاء الإشارات اللازمة."
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
    
    if law_override != "آلي":
        article_num, article_text = law_dict[law_override]

    if manual_mode != "آلي":
        Map_Manual = {
            "الطرف الأول (0%) - الطرف الثاني (100%)": (0, 100),
            "الطرف الأول (25%) - الطرف الثاني (75%)": (25, 75),
            "الطرف الأول (50%) - الطرف الثاني (50%)": (50, 50),
            "الطرف الأول (75%) - الطرف الثاني (25%)": (75, 25),
            "الطرف الأول (100%) - الطرف الثاني (0%)": (100, 0),
        }
        p1_fault, p2_fault = Map_Manual[manual_mode]
        application_text = f"بناءً على المعاينة الفنية الميدانية وتطبيق {article_num}، تتحمل المركبة الأولى ({party1}) نسبة ({p1_fault}%)، وتتحمل المركبة الثانية ({party2}) نسبة ({p2_fault}%)."

    return party1, party2, p1_fault, p2_fault, article_num, article_text, application_text, tech_summary, f1["damage"], f2["damage"], 2, False, []

# ---------------------------------------------------------
# واجهة المستخدم الرسمية
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
    height=155
)

with st.expander("⚙️ خيارات التحكم المتقدم للمحقق (اختياري - يترك على الوضع الآلي)"):
    col1, col2 = st.columns(2)
    with col1:
        manual_override = st.selectbox(
            "📊 تحديد النسب:",
            [
                "آلي",
                "الطرف الأول (0%) - الطرف الثاني (100%)",
                "الطرف الأول (25%) - الطرف الثاني (75%)",
                "الطرف الأول (50%) - الطرف الثاني (50%)",
                "الطرف الأول (75%) - الطرف الثاني (25%)",
                "الطرف الأول (100%) - الطرف الثاني (0%)"
            ]
        )
    with col2:
        law_override = st.selectbox(
            "⚖️ تحديد المادة النظامية:",
            [
                "آلي",
                "المادة (55) - عدم ترك مسافة آمنة (الاصطدام من الخلف / التتابع)",
                "المادة (56) - أفضلية التقاطعات والطرق الرئيسية",
                "المادة (54) - الرجوع إلى الخلف",
                "المادة (50) - الانحراف وتغيير المسار والدوران",
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
        p1, p2, f1, f2, article_num, article_text, application_text, tech_summary, dmg1, dmg2, num_v, is_chain, pushed_cars = analyze_accident(accident_text, manual_override, law_override)
        
        st.markdown("---")
        st.subheader("📋 التقرير النظامي المفصل للحادث")
        
        with st.expander("أولاً: التحليل الفني للحادث 🔍", expanded=True):
            st.write(f"**خلاصة الفحص الميداني:** {tech_summary}")
            
            # بناء جدول التتابع الذكي (يميز المركبة المندفعة قسراً باللون الأخضر 0% ويحمل التي خلفها المسؤولية)
            if is_chain and num_v > 2:
                rows_html = '<tr><td>الطرف رقم (1)</td><td>المركبة الأمامية الأولى</td><td>المؤخرة الخلفية (المقدمة سليمة)</td><td><strong style="color:#4ade80;">0% (مُعفاة - مسار نظامي)</strong></td></tr>'
                for i in range(2, min(num_v + 1, 25)):
                    dmg_desc = "المقدمة الأمامية والمؤخرة الخلفية" if i < num_v else "المقدمة الأمامية فقط (المركبة الأخيرة)"
                    if i in pushed_cars:
                        rows_html += f'<tr><td>الطرف رقم ({i})</td><td>المركبة رقم ({i}) - مندفعة قسراً</td><td>{dmg_desc} (بعد توقف آمن)</td><td><strong style="color:#4ade80;">0% (مُعفاة - اندفاع قسري)</strong></td></tr>'
                    elif (i - 1) in pushed_cars:
                        rows_html += f'<tr><td>الطرف رقم ({i})</td><td>المركبة اللاحقة ({i})</td><td>{dmg_desc}</td><td><strong style="color:#f87171;">100% (شاملة أضرار دفع المركبة {i-1} للأمام)</strong></td></tr>'
                    else:
                        rows_html += f'<tr><td>الطرف رقم ({i})</td><td>المركبة اللاحقة ({i})</td><td>{dmg_desc}</td><td><strong style="color:#f87171;">100% (عما أمامها - مركبة {i-1})</strong></td></tr>'
                table_html = f'<table class="official-table"><tr><th>الطرف</th><th>وصف المركبة</th><th>موضع التصادم</th><th>نسبة المسؤولية (المادة 55)</th></tr>{rows_html}</table>'
            else:
                table_html = (
                    f'<table class="official-table">'
                    f'<tr><th>الطرف</th><th>نوع المركبة</th><th>موضع التصادم</th><th>نسبة المسؤولية</th></tr>'
                    f'<tr><td>الطرف الأول</td><td>{p1}</td><td>{dmg1}</td><td><strong>{f1}%</strong></td></tr>'
                    f'<tr><td>الطرف الثاني</td><td>{p2}</td><td>{dmg2}</td><td><strong>{f2}%</strong></td></tr>'
                    f'</table>'
                )
            st.markdown(table_html, unsafe_allow_html=True)
            
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
            st.markdown(f"* **{p1}:** {f1}% (نقطة التصادم: {dmg1})")
            st.markdown(f"* **{p2}:** {f2}% (نقطة التصادم: {dmg2})")
            st.markdown(f"* **السند النظامي المطبق (رقم المادة):** {article_num}")
            st.markdown(f"* **نص المادة المستند لها:** {article_text}")
            st.markdown(f"* **التطبيق النظامي على الحادث:** {application_text}")
            
        green_html = (
            f'<div class="green-box">'
            f'<h4 style="color: #4ade80; margin-bottom: 15px;">📌 النسب النظامية المعتمدة (المصححة):</h4>'
            f'<p style="color: white; font-size: 18px; font-weight: bold; margin: 5px 0;">🚗 {p1}: {f1}%</p>'
            f'<p style="color: #f87171; font-size: 18px; font-weight: bold; margin: 5px 0;">🚙 {p2}: {f2}%</p>'
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
