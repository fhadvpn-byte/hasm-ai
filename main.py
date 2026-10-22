import streamlit as st

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم الذكي")
st.subheader("نظام تحليل الحوادث المرورية (نسخة نظام المرور المحدثة)")

st.success("✅ تم تفعيل النظام النصي المرن لتحديث النسخ النظامية بكل سهولة")

# --- 2. قاعدة بيانات المواد النظامية (يمكنك تعديلها أو تحديث نسختها في أي وقت) ---
TRAFFIC_RULES = {
    "رجوع": {
        "keyword": "رجوع",
        "article": "المادة (41) من اللائحة التنفيذية لنظام المرور",
        "subdivisions": """
**نص المادة وتقسيماتها الرسمية:**
* **الفقرة (أ):** يحظر على قائد المركبة الرجوع بها إلى الخلف إلا إذا كان ذلك ضرورياً لمسافة قصيرة جداً، وبشرط ألا يشكل خطراً على حركة المرور.
* **الفقرة (ب):** يجب على السائق قبل البدء في الرجوع التأكد التام من خلو الطريق خلفه وتحمل المسؤولية الكاملة في حال وقوع أي اصطدام.
        """,
        "default_p1": "100٪",
        "default_p2": "0٪"
    },
    "انحراف": {
        "keyword": "انحراف",
        "article": "المادة (40) من اللائحة التنفيذية لنظام المرور",
        "subdivisions": """
**نص المادة وتقسيماتها الرسمية:**
* **الفقرة (أ):** لا يجوز لقائد المركبة الانتقال من مسار إلى آخر إلا بعد التأكد من إمكانية القيام بذلك بأمان تام.
* **الفقرة (ب):** يجب إعطاء إشارة تنبيه كافية (المؤشر الضوئي) قبل الانتقال بزق كافٍ ومسافة آمنة.
        """,
        "default_p1": "75٪",
        "default_p2": "25٪"
    },
    "خلف": {
        "keyword": "خلف",
        "article": "المادة (35) من نظام المرور",
        "subdivisions": """
**نص المادة وتقسيماتها الرسمية:**
* **الفقرة (أ):** يجب على قائد المركبة أن يترك بينه وبين المركبة التي أمامه مسافة كافية تتيح له الوقوف في جميع الظروف.
* **الفقرة (ب):** تعتبر المركبة اللاحقة (الصادمة من الخلف) هي المسؤولة كلياً لعدم التزامها بترك مسافة أمان كافية.
        """,
        "default_p1": "100٪",
        "default_p2": "0٪"
    },
    "تقاطع": {
        "keyword": "تقاطع",
        "article": "المادة (55) من نظام المرور",
        "subdivisions": """
**نص المادة وتقسيماتها الرسمية:**
* **الفقرة (أ):** تحديد أولوية المرور في التقاطعات وفقاً للوحات التنظيمية أو القواعد العامة لأسبقية الوصول.
* **الفقرة (ب):** في حال التقاطعات المكافئة وغير المنظمة، توزع المسؤولية مناصفة في حال تكافؤ الأخطاء.
        """,
        "default_p1": "50٪",
        "default_p2": "50٪"
    },
    "دوار": {
        "keyword": "دوار",
        "article": "المادة (54) من نظام المرور",
        "subdivisions": """
**نص المادة وتقسيماتها الرسمية:**
* **الفقرة (أ):** تكون الأولوية للمركبات التي تسير داخل الدوار (التقاطع الدائري) على المركبات التي ترغب في الدخول إليه.
* **الفقرة (ب):** يلتزم قائد المركبة الراغب في دخول الدوار بالتهدئة وإعطاء الأفضلية المطلقة لمن بداخل الدوار.
        """,
        "default_p1": "100٪",
        "default_p2": "0٪"
    }
}

# --- 3. تهيئة حالة الجلسة ---
if 'accident_desc' not in st.session_state:
    st.session_state['accident_desc'] = ""
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_text():
    st.session_state['accident_desc'] = ""
    st.session_state['accident_desc_input'] = ""
    st.session_state['report_ready'] = False

# --- 4. واجهة إدخال الحادث النصية ---
st.markdown("---")
accident_desc = st.text_area(
    "📝 أدخل تفاصيل الحادث (بين حركة الطرف الأول والطرف الثاني بوضوح):", 
    value=st.session_state['accident_desc'],
    key='accident_desc_input',
    height=150
)

st.session_state['accident_desc'] = accident_desc

col1, col2 = st.columns([3, 1])
with col1:
    analyze_btn = st.button("🔍 تحليل الحادث وفق النسخة النظامية المعتمدة", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

# --- 5. محرك التحليل الذكي المطابق للقاعدة ---
if analyze_btn:
    if st.session_state['accident_desc'].strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري مطابقة النص مع قاعدة بيانات نظام المرور..."):
            
            text = st.session_state['accident_desc']
            text_lower = text.lower()
            
            matched_rule = None
            for key, rule in TRAFFIC_RULES.items():
                if rule["keyword"] in text_lower:
                    matched_rule = rule
                    break
            
            # إذا لم يتم العثور على كلمة مفتاحية، نستخدم القاعدة العامة
            if not matched_rule:
                matched_rule = {
                    "article": "المادة (33) من نظام المرور",
                    "subdivisions": "**نص المادة:** يجب على قائد المركبة توخي الحيطة والحذر والسيطرة التامة على المركبة في جميع الأوقات.",
                    "default_p1": "0٪",
                    "default_p2": "100٪"
                }

            # تحديد الطرف المتسبب لمنع انعكاس النسب
            if "الأولى" in text or "الطرف الأول" in text or "سيارة 1" in text:
                if matched_rule["default_p1"] == "100٪" or matched_rule["default_p1"] == "75٪":
                    p1_share = matched_rule["default_p1"]
                    p2_share = matched_rule["default_p2"]
                else:
                    p1_share = matched_rule["default_p2"]
                    p2_share = matched_rule["default_p1"]
            else:
                p1_share = matched_rule["default_p1"]
                p2_share = matched_rule["default_p2"]

            tech_analysis = "تحليل معطيات النص الميداني ومطابقتها مع النسخة المعتمدة لنظام المرور."
            legal_qualification = f"### السند القانوني الرسمي:\n* **رقم المادة:** {matched_rule['article']}\n\n{matched_rule['subdivisions']}"
            
            official_report = f"""
**موضوع التقرير:** معاينة حادث مروري.

* **وصف الحادث:** {st.session_state['accident_desc']}

**النتيجة النهائية وتوزيع النسب:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}
* **السند النظامي:** {matched_rule['article']}
            """

            st.session_state['report_ready'] = True
            st.session_state['p1_share'] = p1_share
            st.session_state['p2_share'] = p2_share
            st.session_state['tech_analysis'] = tech_analysis
            st.session_state['legal_qualification'] = legal_qualification
            st.session_state['official_report'] = official_report

# عرض التقرير إذا كان جاهزاً
if st.session_state.get('report_ready', False):
    st.markdown("---")
    st.markdown("### 📋 التقرير النظامي المفصل للحادث")
    
    with st.expander("🔍 أولاً: التحليل الفني للحادث", expanded=True):
        st.markdown(st.session_state['tech_analysis'])
        
    with st.expander("📜 ثانياً: التكييف النظامي ونصوص المواد وتقسيماتها", expanded=True):
        st.markdown(st.session_state['legal_qualification'])
        
    with st.expander("📄 ثالثاً: التقرير الرسمي المعتمد", expanded=True):
        st.markdown(st.session_state['official_report'])
    
    st.markdown(f"""
        <div style="padding: 20px; border-radius: 12px; border-right: 6px solid #006C35; margin-top: 20px; background: rgba(0,108,53,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #006C35; font-size: 19px;">📌 النسب النظامية المعتمدة:</h3>
            <p style="margin: 6px 0; font-size: 18px; font-weight: bold;">🚗 الطرف الأول: {st.session_state['p1_share']}</p>
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #ff4b4b;">🚙 الطرف الثاني: {st.session_state['p2_share']}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    print_html = f"""
    <script>
    function printReport() {{
        window.print();
    }}
    </script>
    <button onclick="printReport()" style="
        background-color: #006C35;
        color: white;
        padding: 14px 20px;
        border: none;
        border-radius: 10px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;">
        🖨️ طباعة التقرير الرسمي / حفظ كـ PDF
    </button>
    """
    st.components.v1.html(print_html, height=70)
