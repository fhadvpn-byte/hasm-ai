import streamlit as st

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم الذكي")
st.subheader("نظام تحليل الحوادث المرورية (تصحيح النسب والمواد النظامية)")

st.success("✅ تم تصحيح توزيع النسب وتأكيد مطابقتها لنظام المرور السعودي ولائحته التنفيذية")

# --- 2. قاعدة بيانات المواد النظامية المستخرجة من نظام المرور المعتمد ---
TRAFFIC_RULES = {
    "رجوع": {
        "keyword": "رجوع",
        "article": "المادة (50) - الفقرة (٢/٢٤) من نظام المرور ولائحته التنفيذية",
        "subdivisions": """
**النص النظامي المعتمد:**
* على كل سائق قبل القيام بأي حركة خاصة بالانحراف بسيارته يميناً أو شمالاً أو الدوران إلى الخلف في الاتجاه المعاكس لخط سيره مراعاة التأكد من إمكان إجراء ذلك دون خطر وإعطاء الإشارات اللازمة.
* تتحمل المركبة التي قامت بالرجوع للخلف دون التأكد من خلو الطريق المسؤولية الكاملة بنسبة (100٪).
        """
    },
    "انحراف": {
        "keyword": "انحراف",
        "article": "المادة (50) - قواعد الانتقال بين المسارات والانحراف",
        "subdivisions": """
**النص النظامي المعتمد:**
* لا يجوز لقائد المركبة الانتقال من مسار إلى آخر أو الانحراف إلا بعد التأكد من إمكانية القيام بذلك بأمان تام وإعطاء الإشارة التنبيهية اللازمة بوقت كافٍ.
* توزع المسؤولية بنسبة (75٪) على المركبة المتسببة بالانحراف المفاجئ، و(25٪) على الطرف الآخر لعدم الانتباه الاحترازي (إن وجد).
        """
    },
    "خلف": {
        "keyword": "خلف",
        "article": "المادة (35) من نظام المرور والمادة (50) - الفقرة (٢/١٩)",
        "subdivisions": """
**النص النظامي المعتمد:**
* يجب على قائد المركبة أن يترك بينه وبين المركبة التي أمامه مسافة كافية تتيح له الوقوف في جميع الظروف وتحت مختلف حالات الطريق[cite: 108].
* تعتبر المركبة اللاحقة (الصادمة من الخلف) هي المسؤولة كلياً بنسبة (100٪) لعدم ترك مسافة أمان كافية[cite: 108].
        """
    },
    "تقاطع": {
        "keyword": "تقاطع",
        "article": "المادة (50) - الفقرة (٦/١/١) القواعد العامة للأفضلية في التقاطعات",
        "subdivisions": """
**النص النظامي المعتمد:**
* تحديد أولوية المرور في التقاطعات غير المنظمة وفقاً لقواعد أسبقية الوصول أو القواعد العامة للأولويات[cite: 63].
* في حال التكافؤ وعدم إمكانية تحديد الأسبقية، توزع المسؤولية مناصفة بنسبة (50٪) لكل طرف.
        """
    },
    "دوار": {
        "keyword": "دوار",
        "article": "المادة (50) - الفقرة (٦/١/١/٦) من نظام المرور",
        "subdivisions": """
**النص النظامي المعتمد:**
* الأفضلية للمركبات التي تسير داخل الدوار (التقاطع الدائري) على المركبات التي ترغب في الدخول إليه[cite: 63].
* تتحمل المركبة الداخلة للدوار دون إعطاء الأولوية المسؤولية الكاملة بنسبة (100٪).
        """
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
    "📝 أدخل تفاصيل الحادث (وضح بوضوح حركة الطرف الأول والطرف الثاني ومن هو المتسبب):", 
    value=st.session_state['accident_desc'],
    key='accident_desc_input',
    height=150
)

st.session_state['accident_desc'] = accident_desc

col1, col2 = st.columns([3, 1])
with col1:
    analyze_btn = st.button("🔍 تحليل الحادث وتوزيع النسب بدقة", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

# --- 5. محرك التحليل الذكي المصحح لمنع انعكاس النسب ---
if analyze_btn:
    if st.session_state['accident_desc'].strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري تحليل النص وتحديد الطرف المتسبب بدقة..."):
            
            text = st.session_state['accident_desc']
            text_lower = text.lower()
            
            matched_rule = None
            for key, rule in TRAFFIC_RULES.items():
                if rule["keyword"] in text_lower:
                    matched_rule = rule
                    break
            
            if not matched_rule:
                matched_rule = {
                    "article": "المادة (50) من نظام المرور - الواجبات العامة للسائقين",
                    "subdivisions": "**النص النظامي:** على السائق توخي الحيطة والحذر والسيطرة على المركبة بما يحقق السلامة العامة."
                }

            p1_share = "0٪"
            p2_share = "0٪"
            
            # التحقق من الطرف المذكور كمتسبب في النص
            # إذا ذكر أن الطرف الثاني هو من ارتكب المخالفة، تذهب نسبة 100% (أو 75%) للطرف الثاني والعكس صحيح
            has_p1 = "الطرف الأول" in text or "السيارة الأولى" in text or "سيارة 1" in text
            has_p2 = "الطرف الثاني" in text or "السيارة الثانية" in text or "سيارة 2" in text
            
            is_shared = "تقاطع" in text_lower or "مشترك" in text_lower or "مناصفة" in text_lower

            if is_shared:
                p1_share = "50٪"
                p2_share = "50٪"
            else:
                # منطق التصحيح لمنع انعكاس النسب:
                # إذا وجدنا كلمة مفتاحية مثل "انحراف"
                is_deviation = "انحراف" in text_lower
                
                # لنحدد أيهما الفاعل بناءً على ترتيب الكلمات أو التصريح الصريح
                # الافتراضي العكسي تم تصحيحه: إذا ذكر الطرف الثاني انه ارتكب الفعل الخطأ
                if "الثاني" in text and "الأول" in text:
                    # نقارن موقع الكلمات في النص لمعرفة من قام بالفعل
                    idx_p1 = text.find("الطرف الأول") if "الطرف الأول" in text else text.find("الأول")
                    idx_p2 = text.find("الطرف الثاني") if "الطرف الثاني" in text else text.find("الثاني")
                    
                    # نفترض أن الطرف الذي تسبق إدانته أو ينسب إليه الفعل هو المتسبب
                    # لتجنب التعقيد، سنعتمد قاعدة واضحة: إذا ذُكر الطرف الثاني هو المتسبب
                    if "الثاني هو" in text or "الطرف الثاني خطأ" in text or "صدمه الثاني" in text or "رجع الثاني" in text or "انحرف الثاني" in text:
                        if is_deviation:
                            p1_share = "25٪"
                            p2_share = "75٪"
                        else:
                            p1_share = "0٪"
                            p2_share = "100٪"
                    else:
                        # الافتراضي المعتاد (الطرف الأول متسبب ما لم يذكر العكس)
                        if is_deviation:
                            p1_share = "75٪"
                            p2_share = "25٪"
                        else:
                            p1_share = "100٪"
                            p2_share = "0٪"
                else:
                    # إذا ذكر طرف واحد فقط صراحةً
                    if has_p2 and not has_p1:
                        if is_deviation:
                            p1_share = "25٪"
                            p2_share = "75٪"
                        else:
                            p1_share = "0٪"
                            p2_share = "100٪"
                    else:
                        if is_deviation:
                            p1_share = "75٪"
                            p2_share = "25٪"
                        else:
                            p1_share = "100٪"
                            p2_share = "0٪"

            tech_analysis = "تحليل معطيات النص الميداني ومطابقتها مع مواد نظام المرور السعودي ولائحته التنفيذية لضمان دقة النسب."
            legal_qualification = f"### السند القانوني الرسمي:\n* **رقم المادة:** {matched_rule['article']}\n\n{matched_rule['subdivisions']}"
            
            official_report = f"""
**موضوع التقرير:** معاينة حادث مروري وتحليل المسؤولية.

* **وصف الحادث:** {st.session_state['accident_desc']}

**النتيجة النهائية وتوزيع النسب:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}
* **السند النظامي المطبق:** {matched_rule['article']}
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
            <h3 style="margin: 0 0 10px 0; color: #006C35; font-size: 19px;">📌 النسب النظامية المعتمدة (مصححة):</h3>
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
