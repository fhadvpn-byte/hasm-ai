import streamlit as st

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - معاينة مسرح الحادث", page_icon="🚓", layout="centered")

# تصميم بصري أنيق وعصري للعنوان
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); padding: 20px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 28px;">🚓 برنامج حَسْم الذكي</h1>
        <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">النظام الميداني المعتمد لتحليل وتوثيق الحوادث المرورية</p>
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
    "عبور الشارع من غير الأماكن المخصصة (مشاة - مخالفة عبور)",
    "عبور الشارع من الممر المخصص للمشاة (مشاة - نظامي)",
    "السير على الطريق بطريقة مخالفة (مشاة)"
]

# --- 4. الواجهة المنظمة باستخدام التبويبات (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📍 1. الموقع والبيئة", "🚗 2. أطراف الحادث", "💥 3. الاصطدام والتلفيات"])

with tab1:
    st.markdown("### 🛣️ بيانات الطريق والتنظيم المروري")
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
        damage_severity = st.selectbox(
            "حجم التلفيات المادية / الإصابات:",
            ["اختر...", "تلفيات بسيطة (سطحية)", "تلفيات متوسطة (هيكلية)", "تلفيات جسيمة / إصابات بشرية"]
        )

    additional_notes = st.text_area("📝 ملاحظات المعاينة الميدانية وأقوال الأطراف الإضافية (اختياري)", height=80)

st.markdown("---")

# أزرار التحكم
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_btn = st.button("🔍 إصدار التقرير النظامي المعتمد لمسرح الحادث", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ مسح الحقول", on_click=clear_inputs, use_container_width=True)

# --- 5. المحرك التحليلي واستخراج التقرير ---
if analyze_btn:
    if accident_category == "اختر تصنيف الحادث..." or road_type == "اختر..." or veh1_motion == "اختر الحركة..." or impact_point == "اختر نقطة الاصطدام...":
        st.warning("⚠️ الرجاء استكمال اختيار الحقول الأساسية في التبويبات الثلاثة أولاً")
    else:
        with st.spinner("⏳ جاري معالجة المعطيات الميدانية واستخراج النسب النظامية الرسمية..."):
            
            # تحديد النسب الرسمية المعتمدة (مجموعها 100%)
            if "عبور الشارع من غير الأماكن المخصصة" in veh1_motion or "عبور الشارع من غير الأماكن المخصصة" in veh2_motion:
                error_percentage = "100% على المشاة (بسبب عبور الشارع من غير الأماكن المخصصة وعدم إعطاء الأولوية للسيارات)"
            elif "عبور الشارع من الممر المخصص للمشاة" in veh1_motion or "عبور الشارع من الممر المخصص للمشاة" in veh2_motion:
                error_percentage = "100% على قائد المركبة (لعدم إعطاء الأولوية للمشاة في الممر المخصص)"
            elif "الرجوع للخلف" in veh2_motion or "الرجوع للخلف" in veh1_motion:
                error_percentage = "100% على المركبة التي قامت بالرجوع للخلف / 0% على المركبة الأخرى"
            elif "انحراف وتغيير مسار" in veh2_motion or "انحراف وتغيير مسار" in veh1_motion:
                error_percentage = "75% على المركبة المتسببة بالانحراف و 25% على المركبة المتضررة (مسؤولية مشتركة نظامية)"
            elif "الصدم من الخلف" in veh2_motion or "الصدم من الخلف" in veh1_motion:
                error_percentage = "100% على المركبة اللاحقة (بسبب عدم ترك مسافة أمان) / 0% على المركبة الأمامية"
            elif "دخول مفاجئ للدوار" in veh2_motion or "دخول مفاجئ للدوار" in veh1_motion:
                error_percentage = "100% على المركبة الداخلة للدوار (عدم إعطاء الأولوية لمن بداخل الدوار)"
            elif "تقاطع" in road_type:
                error_percentage = "50% على المركبة الأولى و 50% على المركبة الثانية (مسؤولية مشتركة مناصفة)"
            elif "انقلاب" in accident_category:
                error_percentage = "100% على قائد المركبة المنقلبة (لعدم السيطرة أو السرعة)"
            else:
                error_percentage = "100% على الطرف المتسبب في الحادث / 0% على الطرف المتضرر"

            tech_analysis = f"""
1. **تصنيف المعاينة:** {accident_category} على طريق ({road_type})، التنظيم ({traffic_sign})، حالة الطقس ({weather_cond}).
2. **أطراف الحادث:** الطرف الأول ({veh1_type} - {veh1_motion}) والطرف الثاني ({veh2_type} - {veh2_motion}).
3. **نقطة الاصطدام والضرر:** ({impact_point}) بحجم تلفيات/إصابات مقدرة بـ ({damage_severity}).
            """
            
            legal_qualification = f"""
وفقاً لنظام المرور ولائحته التنفيذية وقواعد تحديد نسب الخطأ المعتمدة:
* تطبيق المواد النظامية المتعلقة بالعبور الآمن، أولوية المشاة، ترك مسافة الأمان، الالتزام بالمسارات، وحقوق الأولوية.
            """
            
            official_report = f"""
**موضوع التقرير:** معاينة وتحديد المسؤولية النظامية عن حادث ({accident_category}).

* **بيانات الموقع:** {road_type} | التنظيم: {traffic_sign} | الحالة الجوية: {weather_cond}
* **الطرف الأول:** {veh1_type} ({veh1_motion})
* **الطرف الثاني:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام والضرر:** {impact_point} ({damage_severity})
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد ملاحظات إضافية"}

**التحليل الفني والقانوني:** بناءً على المعطيات الفعلية لمسرح الحادث وتتبع حركة الأطراف، ثبت وقوع الاصطدام والأضرار المذكورة نتيجة المخالفة المرصودة وفقاً للائحة المرورية.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية المعتمدة:** {error_percentage}
* **السند النظامي:** نظام المرور السعودي ولائحته التنفيذية.
            """

            st.session_state['report_ready'] = True
            st.session_state['error_percentage'] = error_percentage
            st.session_state['tech_analysis'] = tech_analysis
            st.session_state['legal_qualification'] = legal_qualification
            st.session_state['official_report'] = official_report

# عرض التقرير إذا كان جاهزاً
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
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; border-right: 5px solid #ff4b4b; margin-top: 15px;">
            <h3 style="margin: 0; color: #1e3c72; font-size: 18px;">📌 نسبة الخطأ المعتمدة في النظام:</h3>
            <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold; color: #ff4b4b;">{st.session_state['error_percentage']}</p>
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
        background-color: #ff4b4b;
        color: white;
        padding: 14px 20px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        🖨️ طباعة التقرير / حفظ كـ PDF
    </button>
    """
    st.components.v1.html(print_html, height=70)
