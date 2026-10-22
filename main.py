import streamlit as st

# --- 1. إعداد واجهة البرنامج (متوافقة تلقائياً مع Light & Dark Mode) ---
st.set_page_config(page_title="برنامج حَسْم - معاينة مسرح الحادث", page_icon="🚓", layout="centered")

st.markdown("""
    <div style="padding: 22px; border-radius: 15px; text-align: center; margin-bottom: 25px; border: 1px solid rgba(0,108,53,0.3); background: rgba(0,108,53,0.1);">
        <h1 style="margin: 0; font-size: 28px; color: #006C35;">🚓 برنامج حَسْم الذكي</h1>
        <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.9;">النظام الميداني المعتمد لتحليل وتوثيق الحوادث المرورية</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. تهيئة حالة الجلسة ---
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_inputs():
    st.session_state['report_ready'] = False

# --- 3. قائمة الحركات المحايدة والمهنية بالكامل ---
motion_options = [
    "اختر حركة أو وضعية الطرف...",
    "سير نظامي ومستقيم في المسار المخصص",
    "وقوف تام ونظامي",
    "تهدئة السرعة والاستعداد للوقوف",
    "استقرار داخل المسار أو الدوار",
    "انحراف وتغيير مسار غير آمن",
    "رجوع للخلف دون التأكد من خلو الطريق",
    "عدم ترك مسافة أمان كافية (صدم من الخلف)",
    "دخول مفاجئ للتقاطع أو الدوار دون إعطاء الأولوية",
    "عبور الشارع من غير الأماكن المخصصة للمشاة",
    "عبور الشارع من الممر المخصص للمشاة (نظامي)",
    "تجاوز إشارة ضوئية حمراء"
]

# --- 4. الواجهة المنظمة (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📍 1. الموقع والبيئة والنتائج", "🚗 2. أطراف الحادث", "💥 3. الاصطدام والتلفيات"])

with tab1:
    st.markdown("### 🛣️ بيانات الطريق، التنظيم، والآثار المادية والبشرية")
    
    accident_category = st.selectbox(
        "🚨 التصنيف الرئيسي للحادث:",
        [
            "اختر تصنيف الحادث...",
            "حادث تصادم بين مركبتين",
            "حادث انقلاب مركبة",
            "حادث سقوط من مرتفع",
            "حادث دهس مشاة",
            "حادث اصطدام بجسم ثابت"
        ]
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        road_type = st.selectbox(
            "نوع الطريق:",
            ["اختر...", "طريق رئيسي سريع", "طريق فرعي", "دوار (تقاطع دائري)", "تقاطع إشاري", "تقاطع غير منظم", "منحنى"]
        )
    with col_b:
        traffic_sign = st.selectbox(
            "التنظيم المروري:",
            ["اختر...", "إشارة ضوئية تعمل", "لوحة قف", "لوحة أولوية", "بدون لوحات تنظيمية"]
        )
    
    weather_cond = st.selectbox(
        "🌤️ الظروف الجوية:",
        ["اختر...", "طريق جاف وطبيعي", "مطر / زلق", "غبار / انعدام رؤية", "ليلي / إضاءة ضعيفة"]
    )
    
    st.markdown("---")
    st.markdown("#### 🏥 الأثر البشري والمادي")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        injury_status = st.selectbox("حالة الإصابات:", ["لا توجد إصابات", "إصابات خفيفة", "إصابات متوسطة", "إصابات بليغة"])
    with col_res2:
        fatality_status = st.selectbox("حالات الوفاة:", ["لا توجد وفيات", "حالة وفاة واحدة", "وفيات متعددة"])
    with col_res3:
        damage_status = st.selectbox("حجم التلفيات:", ["تلفيات بسيطة", "تلفيات متوسطة", "تلفيات جسيمة / تلف كلي"])

with tab2:
    st.markdown("### 🚙 بيانات الأطراف وحركتهم الميدانية")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**الطرف الأول**")
        veh1_type = st.selectbox("نوع الطرف 1:", ["اختر...", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v1_t")
        veh1_motion = st.selectbox("حركة الطرف الأول:", motion_options, key="v1_m")
        
    with col2:
        st.markdown("**الطرف الثاني**")
        veh2_type = st.selectbox("نوع الطرف 2:", ["لا يوجد (حادث طرف واحد)", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v2_t")
        veh2_motion = st.selectbox("حركة الطرف الثاني:", motion_options, key="v2_m")

with tab3:
    st.markdown("### 💥 تفاصيل الاصطدام والتلفيات")
    
    col5, col6 = st.columns(2)
    with col5:
        impact_point = st.selectbox(
            "موقع الاصطدام الرئيسي:",
            [
                "اختر نقطة الاصطدام...",
                "صدم خلفي (بمؤخرة المركبة)",
                "تداخل مسارات (جوانب المركبتين)",
                "تقابل وجهاً لوجه",
                "انقلاب المركبة",
                "سقوط من مرتفع",
                "اصطدام بجسم ثابت",
                "دهس مشاة"
            ]
        )
    with col6:
        impact_severity = st.selectbox(
            "طبيعة الاصطدام:",
            ["اختر...", "صدم مباشر", "احتكاك جانبي", "تداصم تقاطعي"]
        )

    additional_notes = st.text_area("📝 ملاحظات المعاينة الميدانية وأقوال الأطراف:", height=80)

st.markdown("---")

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_btn = st.button("🔍 إصدار التقرير النظامي المعتمد لمسرح الحادث", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ مسح الحقول", on_click=clear_inputs, use_container_width=True)

# --- 5. المحرك التحليلي الموضوعي الدقيق ---
if analyze_btn:
    if accident_category == "اختر تصنيف الحادث..." or road_type == "اختر..." or veh1_motion == "اختر حركة أو وضعية الطرف..." or impact_point == "اختر نقطة الاصطدام...":
        st.warning("⚠️ الرجاء استكمال اختيار الحقول الأساسية أولاً")
    else:
        with st.spinner("⏳ جاري تحليل المعطيات الميدانية وتطبيق اللائحة المرورية بدقة..."):
            
            p1_share = "0٪"
            p2_share = "0٪"
            violation_desc = "تحديد المسؤولية بناءً على المعطيات الفنية."
            
            # منطق تحليل موضوعي بحت بناءً على الحركة المختارة
            if "عبور الشارع من غير الأماكن المخصصة" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_desc = "عبور المشاة من غير الأماكن المخصصة."
            elif "عبور الشارع من غير الأماكن المخصصة" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "عبور المشاة من غير الأماكن المخصصة."
            elif "عبور الشارع من الممر المخصص للمشاة" in veh1_motion:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "عدم إعطاء الأولوية للمشاة في الممر المخصص."
            elif "عبور الشارع من الممر المخصص للمشاة" in veh2_motion:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_desc = "عدم إعطاء الأولوية للمشاة في الممر المخصص."
            elif "رجوع للخلف" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_desc = "الرجوع للخلف دون التأكد من خلو الطريق."
            elif "رجوع للخلف" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "الرجوع للخلف دون التأكد من خلو الطريق."
            elif "عدم ترك مسافة أمان" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_desc = "عدم ترك مسافة أمان كافية (الصدم من الخلف)."
            elif "عدم ترك مسافة أمان" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "عدم ترك مسافة أمان كافية (الصدم من الخلف)."
            elif "انحراف وتغيير مسار" in veh1_motion:
                p1_share = "75٪"
                p2_share = "25٪"
                violation_desc = "انحراف وتغيير مسار غير آمن."
            elif "انحراف وتغيير مسار" in veh2_motion:
                p1_share = "25٪"
                p2_share = "75٪"
                violation_desc = "انحراف وتغيير مسار غير آمن."
            elif "تقاطع" in road_type:
                p1_share = "50٪"
                p2_share = "50٪"
                violation_desc = "عدم الالتزام بأولويات التقاطعات المشتركة."
            else:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "تحديد المسؤولية بناءً على حركة الأطراف."

            tech_analysis = f"""
1. **تصنيف المعاينة:** {accident_category} على طريق ({road_type}) - التنظيم: ({traffic_sign}) - الجو: ({weather_cond}).
2. **الآثار البشرية والمادية:** الإصابات: ({injury_status}) | الوفيات: ({fatality_status}) | التلفيات: ({damage_status}).
3. **حركة الأطراف:** الطرف الأول ({veh1_type}: {veh1_motion}) | الطرف الثاني ({veh2_type}: {veh2_motion}).
4. **موقع الاصطدام:** ({impact_point}) - الطبيعة: ({impact_severity}).
            """
            
            legal_qualification = f"""
* **المخالفة المرصودة:** {violation_desc}
* **السند القانوني:** تطبيق مواد نظام المرور السعودي ولائحته التنفيذية بشأن القواعد والمسؤوليات المرورية.
            """
            
            official_report = f"""
**موضوع التقرير:** تقرير معاينة حادث ({accident_category}).

* **بيانات الموقع:** {road_type} ({traffic_sign})
* **النتائج:** الإصابات: {injury_status} | الوفيات: {fatality_status} | التلفيات: {damage_status}
* **الطرف الأول:** {veh1_type} ({veh1_motion})
* **الطرف الثاني:** {veh2_type} ({veh2_motion})
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد ملاحظات"}

**التحليل الفني والنتيجة النهائية:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}
* **السند النظامي:** نظام المرور ولائحته التنفيذية.
            """

            st.session_state['report_ready'] = True
            st.session_state['p1_share'] = p1_share
            st.session_state['p2_share'] = p2_share
            st.session_state['tech_analysis'] = tech_analysis
            st.session_state['legal_qualification'] = legal_qualification
            st.session_state['official_report'] = official_report

# عرض التقرير
if st.session_state.get('report_ready', False):
    st.markdown("---")
    st.markdown("### 📋 التقرير النظامي المعتمد لمسرح الحادث")
    
    with st.expander("🔍 أولاً: التحليل الفني للحادث", expanded=True):
        st.markdown(st.session_state['tech_analysis'])
        
    with st.expander("📜 ثانياً: التكييف النظامي", expanded=True):
        st.markdown(st.session_state['legal_qualification'])
        
    with st.expander("📄 ثالثاً: التقرير الرسمي", expanded=True):
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
