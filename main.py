import streamlit as st

# --- 1. إعداد واجهة البرنامج (الهوية الرسمية للمرور: أخضر وأبيض بتصميم عصري مميز) ---
st.set_page_config(page_title="برنامج حَسْم - معاينة مسرح الحادث", page_icon="🚓", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #f8faf8;
    }
    .main-header {
        background: linear-gradient(135deg, #006C35 0%, #004d26 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid #ffffff;
        box-shadow: 0 6px 12px rgba(0,108,53,0.15);
    }
    </style>
    
    <div class="main-header">
        <h1 style="margin: 0; font-size: 30px; font-weight: bold;">🚓 برنامج حَسْم الذكي</h1>
        <p style="margin: 8px 0 0 0; font-size: 15px; opacity: 0.95;">النظام الميداني المعتمد لتحليل وتوثيق الحوادث المرورية بدقة واحترافية</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. تهيئة حالة الجلسة ---
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_inputs():
    st.session_state['report_ready'] = False

# --- 3. قائمة الحركات الشاملة (للمركبات والمشاة) ---
motion_options = [
    "اختر الحركة...",
    "تسير بشكل نظامي ومستقيم في مسارها",
    "متوقفة وقوفاً تاماً ونظامياً",
    "تستعد للوقوف أو تهدئة السرعة",
    "مستقرة داخل المسار أو الدوار",
    "انحراف وتغيير مسار غير آمن (متسبب)",
    "الرجوع للخلف دون تأكد من خلو الطريق (متسبب)",
    "الصدم من الخلف لعدم ترك مسافة أمان (متسبب)",
    "دخول مفاجئ للدوار أو تقاطع (متسبب)",
    "عبور الشارع من غير الأماكن المخصصة (مشاة - خطأ على المشاة)",
    "عبور الشارع من الممر المخصص للمشاة (مشاة - نظامي)",
    "السير على الطريق بطريقة مخالفة (مشاة)"
]

# --- 4. الواجهة المنظمة باستخدام التبويبات (Tabs) بتصميم بطاقات فخمة ---
tab1, tab2, tab3 = st.tabs(["📍 1. الموقع والبيئة والنتائج", "🚗 2. أطراف الحادث", "💥 3. الاصطدام والتلفيات"])

with tab1:
    st.markdown("### 🛣️ بيانات الطريق، التنظيم، والنتائج البشرية والمادية")
    
    accident_category = st.selectbox(
        "🚨 التصنيف الرئيسي للحادث:",
        [
            "اختر تصنيف الحادث...",
            "حادث تصادم بين مركبتين (أو أكثر)",
            "حادث انقلاب مركبة (فردي أو بسبب تفادي)",
            "حادث سقوط (من مرتفع / جسر)",
            "حادث دهس مشاة",
            "حادث اصطدام بجسم ثابت (رصيف / إنارة / جدار)"
        ]
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        road_type = st.selectbox(
            "نوع الطريق:",
            ["اختر...", "طريق رئيسي سريع", "طريق فرعي / محلي", "دوار (تقاطع دائري)", "تقاطع إشاري", "تقاطع غير منظم", "منحنى خطير"]
        )
    with col_b:
        traffic_sign = st.selectbox(
            "التنظيم المروري والإشارات:",
            ["اختر...", "إشارة ضوئية (تعمل)", "لوحة قف (Stop)", "لوحة أفضلية / أولوية", "بدون لوحات أو إشارات تنظم الأولوية"]
        )
    
    weather_cond = st.selectbox(
        "🌤️ الظروف الجوية والبيئية:",
        ["اختر...", "طريق جاف / أحوال طبيعية", "مطر / سطح زلق", "غبار / انعدام رؤية جزئي", "فترة الليل / إضاءة ضعيفة"]
    )
    
    st.markdown("---")
    st.markdown("#### 🏥 الإصابات والوفيات والتلفيات (معاينة الأثر)")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        injury_status = st.selectbox("حالة الإصابات:", ["لا توجد إصابات", "إصابات خفيفة (سطحية)", "إصابات متوسطة", "إصابات بليغة"])
    with col_res2:
        fatality_status = st.selectbox("حالات الوفاة:", ["لا توجد وفيات", "توجد حالة وفاة واحدة", "توجد حالات وفاة متعددة"])
    with col_res3:
        damage_status = st.selectbox("حجم التلفيات:", ["تلفيات بسيطة", "تلفيات متوسطة", "تلفيات جسيمة / تلف كلي"])

with tab2:
    st.markdown("### 🚙 بيانات الأطراف وحركتهم الميدانية")
    
    st.markdown("#### الطرف الأول")
    col1, col2 = st.columns(2)
    with col1:
        veh1_type = st.selectbox("نوع المركبة / الطرف 1:", ["اختر...", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v1_t")
    with col2:
        veh1_motion = st.selectbox("حركة الطرف الأول:", motion_options, key="v1_m")
        
    st.markdown("---")
    st.markdown("#### الطرف الثاني")
    col3, col4 = st.columns(2)
    with col3:
        veh2_type = st.selectbox("نوع المركبة / الطرف 2:", ["لا يوجد (حادث طرف واحد)", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v2_t")
    with col4:
        veh2_motion = st.selectbox("حركة الطرف الثاني:", motion_options, key="v2_m")

with tab3:
    st.markdown("### 💥 تفاصيل الاصطدام والتلفيات المادية")
    
    col5, col6 = st.columns(2)
    with col5:
        impact_point = st.selectbox(
            "موقع الاصطدام الرئيسي:",
            [
                "اختر نقطة الاصطدام...",
                "مقدمة مركبة بمؤخرة الأخرى (صدم من الخلف)",
                "الجانب الأيسر أو الأيمن (تداخل مسارات)",
                "مقدمة المركبتين (تقابل وجهاً لوجه)",
                "انقلاب كلي أو جزئي للمركبة",
                "سقوط من مرتفع أو جسر",
                "اصطدام بجسم ثابت (رصيف / إنارة)",
                "دهس مشاة (مقدمة المركبة بالمشاة)"
            ]
        )
    with col6:
        impact_severity = st.selectbox(
            "طبيعة الاصطدام الميداني:",
            ["اختر...", "اصطدام مباشر", "احتكاك جانبي", "تداصم تقاطعي"]
        )

    additional_notes = st.text_area("📝 ملاحظات المعاينة الميدانية وأقوال الأطراف الإضافية (اختياري)", height=80)

st.markdown("---")

# أزرار التحكم بتصميم احترافي
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_btn = st.button("🔍 إصدار التقرير النظامي المعتمد لمسرح الحادث", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ مسح الحقول", on_click=clear_inputs, use_container_width=True)

# --- 5. المحرك التحليلي الدقيق (منع انعكاس النسب) ---
if analyze_btn:
    if accident_category == "اختر تصنيف الحادث..." or road_type == "اختر..." or veh1_motion == "اختر الحركة..." or impact_point == "اختر نقطة الاصطدام...":
        st.warning("⚠️ الرجاء استكمال اختيار الحقول الأساسية في التبويبات الثلاثة أولاً")
    else:
        with st.spinner("⏳ جاري معالجة المعطيات الميدانية وتحديد النسب بدقة تامة..."):
            
            p1_share = "0٪"
            p2_share = "0٪"
            
            # فحص أخطاء الطرف الأول بدقة
            if "عبور الشارع من غير الأماكن المخصصة" in veh1_motion or "السير على الطريق بطريقة مخالفة" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
            elif "عبور الشارع من الممر المخصص للمشاة" in veh1_motion:
                p1_share = "0٪"
                p2_share = "100٪"
            elif "الرجوع للخلف" in veh1_motion or "الصدم من الخلف" in veh1_motion or "دخول مفاجئ للدوار" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
            elif "انحراف وتغيير مسار" in veh1_motion:
                p1_share = "75٪"
                p2_share = "25٪"
                
            # فحص أخطاء الطرف الثاني بدقة
            elif "عبور الشارع من غير الأماكن المخصصة" in veh2_motion or "السير على الطريق بطريقة مخالفة" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
            elif "عبور الشارع من الممر المخصص للمشاة" in veh2_motion:
                p1_share = "100٪"
                p2_share = "0٪"
            elif "الرجوع للخلف" in veh2_motion or "الصدم من الخلف" in veh2_motion or "دخول مفاجئ للدوار" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
            elif "انحراف وتغيير مسار" in veh2_motion:
                p1_share = "25٪"
                p2_share = "75٪"
            elif "تقاطع" in road_type:
                p1_share = "50٪"
                p2_share = "50٪"
            elif "انقلاب" in accident_category:
                p1_share = "100٪"
                p2_share = "0٪"
            else:
                p1_share = "0٪"
                p2_share = "100٪"

            tech_analysis = f"""
1. **تصنيف المعاينة والنتائج:** {accident_category} على طريق ({road_type}) | التنظيم ({traffic_sign}) | حالة الطقس ({weather_cond}).
2. **الآثار البشرية والمادية:** الإصابات: ({injury_status}) | الوفيات: ({fatality_status}) | التلفيات: ({damage_status}).
3. **أطراف الحادث:** الطرف الأول ({veh1_type} - {veh1_motion}) والطرف الثاني ({veh2_type} - {veh2_motion}).
4. **نقطة الاصطدام والضرر:** ({impact_point}) طبيعة الاصطدام ({impact_severity}).
            """
            
            legal_qualification = f"""
وفقاً لنظام المرور ولائحته التنفيذية وقواعد تحديد نسب الخطأ المعتمدة:
* تطبيق المواد النظامية المتعلقة بالعبور الآمن، أولوية المشاة، ترك مسافة الأمان، الالتزام بالمسارات، وحقوق الأولوية، مع رصد الحالات البشرية والمادية.
            """
            
            official_report = f"""
**موضوع التقرير:** معاينة وتحديد المسؤولية النظامية عن حادث ({accident_category}).

* **بيانات الموقع والبيئة:** {road_type} | التنظيم: {traffic_sign} | الحالة الجوية: {weather_cond}
* **النتائج والآثار:** الإصابات: {injury_status} | الوفيات: {fatality_status} | التلفيات: {damage_status}
* **الطرف الأول:** {veh1_type} ({veh1_motion})
* **الطرف الثاني:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام والضرر:** {impact_point}
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد ملاحظات إضافية"}

**التحليل الفني والقانوني:** بناءً على المعطيات الفعلية لمسرح الحادث وتتبع حركة الأطراف، ثبت وقوع الاصطدام والأضرار المذكورة نتيجة المخالفة المرصودة وفقاً للائحة المرورية.

**النتيجة النهائية وتوزيع نسب الخطأ:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}
* **السند النظامي:** نظام المرور السعودي ولائحته التنفيذية.
            """

            st.session_state['report_ready'] = True
            st.session_state['p1_share'] = p1_share
            st.session_state['p2_share'] = p2_share
            st.session_state['tech_analysis'] = tech_analysis
            st.session_state['legal_qualification'] = legal_qualification
            st.session_state['official_report'] = official_report

# عرض التقرير إذا كان جاهزاً بتصميم منسق ومميز
if st.session_state.get('report_ready', False):
    st.markdown("---")
    st.markdown("### 📋 التقرير النظامي المفصل لمسرح الحادث")
    
    with st.expander("🔍 أولاً: التحليل الفني للحادث", expanded=True):
        st.markdown(st.session_state['tech_analysis'])
        
    with st.expander("📜 ثانياً: التكييف النظامي (المخالفة)", expanded=True):
        st.markdown(st.session_state['legal_qualification'])
        
    with st.expander("📄 ثالثاً: تقرير الحادث (بصياغة رسمية)", expanded=True):
        st.markdown(st.session_state['official_report'])
    
    st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 12px; border-right: 6px solid #006C35; margin-top: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <h3 style="margin: 0 0 10px 0; color: #004d26; font-size: 19px;">📌 النسب النظامية الدقيقة المعتمدة في النظام:</h3>
            <p style="margin: 6px 0; font-size: 18px; font-weight: bold; color: #004d26;">🚗 الطرف الأول: {st.session_state['p1_share']}</p>
            <p style="margin: 0; font-size: 18px; font-weight: bold; color: #d32f2f;">🚙 الطرف الثاني: {st.session_state['p2_share']}</p>
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
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        🖨️ طباعة التقرير / حفظ كـ PDF
    </button>
    """
    st.components.v1.html(print_html, height=70)
