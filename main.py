import streamlit as st

# --- 1. إعداد واجهة البرنامج (الهوية الرسمية للمرور: أخضر وأبيض) ---
st.set_page_config(page_title="برنامج حَسْم - معاينة مسرح الحادث", page_icon="🚓", layout="centered")

st.markdown("""
    <style>
    .stApp {
        background-color: #f4f9f4;
    }
    .main-header {
        background: linear-gradient(135deg, #006C35 0%, #004d26 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        border: 2px solid #ffffff;
        box-shadow: 0 4px 10px rgba(0,108,53,0.2);
    }
    .report-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-right: 6px solid #006C35;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-top: 15px;
    }
    </style>
    
    <div class="main-header">
        <h1 style="margin: 0; font-size: 30px; font-weight: bold;">🚓 برنامج حَسْم الذكي</h1>
        <p style="margin: 8px 0 0 0; font-size: 15px; opacity: 0.95;">النظام الميداني المعتمد لتحليل وتوثيق الحوادث المرورية نظامياً</p>
    </div>
""", unsafe_allow_html=True)

# --- 2. تهيئة حالة الجلسة ---
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_inputs():
    st.session_state['report_ready'] = False

# --- 3. قائمة الحركات الدقيقة للطرفين ---
motion_options = [
    "اختر حركة أو وضعية الطرف...",
    "تسير بشكل نظامي ومستقيم في مسارها",
    "متوقفة وقوفاً تاماً ونظامياً",
    "تستعد للوقوف أو تهدئة السرعة",
    "مستقرة داخل المسار أو الدوار",
    "انحراف وتغيير مسار مفاجئ غير آمن (متسبب)",
    "الرجوع للخلف دون تأكد من خلو الطريق (متسبب)",
    "الصدم من الخلف لعدم ترك مسافة أمان كافية (متسبب)",
    "دخول مفاجئ للدوار دون إعطاء الأولوية (متسبب)",
    "عبور الشارع من غير الأماكن المخصصة (خطأ على المشاة)",
    "عبور الشارع من الممر المخصص للمشاة (أولوية للمشاة)",
    "تجاوز إشارة ضوئية حمراء (متسبب)"
]

# --- 4. الواجهة المنظمة (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📍 1. الموقع، البيئة والآثار", "🚗 2. بيانات الأطراف والحركات", "💥 3. الاصطدام والتلفيات"])

with tab1:
    st.markdown("### 🛣️ بيانات الطريق، التنظيم المروري، والنتائج البشرية والمادية")
    
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
    st.markdown("#### 🏥 معاينة الأثر البشري والمادي")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        injury_status = st.selectbox("حالة الإصابات:", ["لا توجد إصابات", "إصابات خفيفة (سطحية)", "إصابات متوسطة", "إصابات بليغة"])
    with col_res2:
        fatality_status = st.selectbox("حالات الوفاة:", ["لا توجد وفيات", "توجد حالة وفاة واحدة", "توجد حالات وفاة متعددة"])
    with col_res3:
        damage_status = st.selectbox("حجم التلفيات:", ["تلفيات بسيطة", "تلفيات متوسطة", "تلفيات جسيمة / تلف كلي"])

with tab2:
    st.markdown("### 🚙 بيانات الأطراف وحركتهم الميدانية المثبتة")
    
    st.markdown("#### الطرف الأول")
    col1, col2 = st.columns(2)
    with col1:
        veh1_type = st.selectbox("نوع الطرف الأول:", ["اختر...", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v1_t")
    with col2:
        veh1_motion = st.selectbox("حركة ووضع الطرف الأول:", motion_options, key="v1_m")
        
    st.markdown("---")
    st.markdown("#### الطرف الثاني")
    col3, col4 = st.columns(2)
    with col3:
        veh2_type = st.selectbox("نوع الطرف الثاني:", ["لا يوجد (حادث طرف واحد)", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v2_t")
    with col4:
        veh2_motion = st.selectbox("حركة ووضع الطرف الثاني:", motion_options, key="v2_m")

with tab3:
    st.markdown("### 💥 تفاصيل الاصطدام والتلفيات الهيكلية")
    
    col5, col6 = st.columns(2)
    with col5:
        impact_point = st.selectbox(
            "موقع الاصطدام الرئيسي:",
            [
                "اختر نقطة الاصطدام...",
                "مقدمة مركبة بمؤخرة الأخرى (صدم خلفي)",
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
            ["اختر...", "صدم مباشر", "احتكاك جانبي", "تداصم تقاطعي"]
        )

    additional_notes = st.text_area("📝 ملاحظات المعاينة الميدانية وأقوال الأطراف الإضافية (اختياري)", height=80)

st.markdown("---")

# أزرار التحكم
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_btn = st.button("🔍 إصدار التقرير النظامي المعتمد لمسرح الحادث", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ مسح الحقول", on_click=clear_inputs, use_container_width=True)

# --- 5. المحرك القانوني والفني الدقيق لتحديد النسب (منع الانعكاس والخطأ) ---
if analyze_btn:
    if accident_category == "اختر تصنيف الحادث..." or road_type == "اختر..." or veh1_motion == "اختر حركة ووضع الطرف..." or impact_point == "اختر نقطة الاصطدام...":
        st.warning("⚠️ الرجاء استكمال اختيار الحقول الأساسية في التبويبات الثلاثة أولاً")
    else:
        with st.spinner("⏳ جاري تحليل المعطيات الميدانية وتطبيق المواد النظامية بدقة..."):
            
            p1_share = "0٪"
            p2_share = "0٪"
            violation_text = ""
            legal_basis = ""
            
            # منطق تحليل دقيق جداً لا يحتمل الخطأ
            # 1. حالات أخطاء الطرف الأول الصريحة
            if "عبور الشارع من غير الأماكن المخصصة" in veh1_motion or "السير على الطريق بطريقة مخالفة" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_text = "عبور المشاة من غير الأماكن المخصصة وعدم إعطاء الأولوية للسيارات."
                legal_basis = "المادة الخاصة بقواعد عبور المشاة وتحديد المسؤولية عند العبور الخاطئ."
            elif "الرجوع للخلف" in veh1_motion or "الصدم من الخلف" in veh1_motion or "دخول مفاجئ للدوار" in veh1_motion or "تجاوز إشارة ضوئية" in veh1_motion:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_text = f"ارتكاب مخالفة مرورية ({veh1_motion}) من قبل الطرف الأول."
                legal_basis = "نظام المرور السعودي - اللائحة التنفيذية بشأن عدم ترك مسافة أمان، أو مخالفة الأولويات."
            elif "انحراف وتغيير مسار" in veh1_motion:
                p1_share = "75٪"
                p2_share = "25٪"
                violation_text = "انحراف وتغيير مسار غير آمن من الطرف الأول مع عدم انتباه كافٍ من الطرف الثاني."
                legal_basis = "نظام المرور السعودي - قواعد الانتقال بين المسارات والانحراف المفاجئ."
                
            # 2. حالات أخطاء الطرف الثاني الصريحة
            elif "عبور الشارع من غير الأماكن المخصصة" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_text = "عبور المشاة (الطرف الثاني) من غير الأماكن المخصصة للعبور."
                legal_basis = "نظام المرور السعودي - قواعد سير وعبور المشاة."
            elif "عبور الشارع من الممر المخصص للمشاة" in veh1_motion and "دهس" in accident_category:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_text = "عدم إعطاء قائد المركبة الأولوية للمشاة في الممر المخصص."
                legal_basis = "نظام المرور السعودي - أولوية المشاة في الممرات المخصصة."
            elif "الرجوع للخلف" in veh2_motion or "الصدم من الخلف" in veh2_motion or "دخول مفاجئ للدوار" in veh2_motion or "تجاوز إشارة ضوئية" in veh2_motion:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_text = f"ارتكاب مخالفة مرورية ({veh2_motion}) من قبل الطرف الثاني."
                legal_basis = "نظام المرور السعودي ولائحته التنفيذية."
            elif "انحراف وتغيير مسار" in veh2_motion:
                p1_share = "25٪"
                p2_share = "75٪"
                violation_text = "انحراف وتغيير مسار غير آمن من الطرف الثاني مع عدم انتباه كافٍ من الطرف الأول."
                legal_basis = "نظام المرور السعودي - قواعد الانتقال بين المسارات."
                
            # 3. الحالات المشتركة أو الحوادث الفردية
            elif "تقاطع" in road_type:
                p1_share = "50٪"
                p2_share = "50٪"
                violation_text = "تقاطع مسارات الطرفين في تقاطع خالٍ من التنظيم دون إعطاء أولوية متبادلة."
                legal_basis = "نظام المرور السعودي - القواعد العامة لأولويات التقاطعات غير المنظمة."
            elif "انقلاب" in accident_category:
                p1_share = "100٪"
                p2_share = "0٪"
                violation_text = "فقدان السيطرة وعدم تقدير الظروف الطريق أدى إلى الانقلاب."
                legal_basis = "نظام المرور السعودي - عدم السيطرة على المركبة."
            else:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_text = "مسؤولية الطرف المتسبب المباشر عن وقوع الحادث والأضرار."
                legal_basis = "نظام المرور السعودي ولائحته التنفيذية."

            tech_analysis = f"""
1. **تصنيف الحادث:** {accident_category} واقع على طريق ({road_type})، وفق تنظيم ({traffic_sign})، وتحت ظروف جوية ({weather_cond}).
2. **الآثار والنتائج ميدانياً:** الإصابات: ({injury_status}) | الوفيات: ({fatality_status}) | حجم التلفيات: ({damage_status}).
3. **أطراف المعاينة:** الطرف الأول ({veh1_type} - {veh1_motion}) والطرف الثاني ({veh2_type} - {veh2_motion}).
4. **طبيعة الاصطدام:** ({impact_point}) بطبيعة ({impact_severity}).
            """
            
            legal_qualification = f"""
* **المخالفة المثبتة:** {violation_text}
* **السند النظامي:** {legal_basis}
            """
            
            official_report = f"""
**موضوع التقرير:** معاينة وتحديد المسؤولية النظامية عن حادث ({accident_category}).

* **بيانات الموقع:** {road_type} | التنظيم: {traffic_sign} | الحالة الجوية: {weather_cond}
* **الآثار البشرية والمادية:** الإصابات: {injury_status} | الوفيات: {fatality_status} | التلفيات: {damage_status}
* **الطرف الأول:** {veh1_type} ({veh1_motion})
* **الطرف الثاني:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام والضرر:** {impact_point}
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد ملاحظات إضافية"}

**التحليل الفني والقانوني:** بناءً على المعطيات الفعلية لمسرح الحادث وتتبع حركة الأطراف، ثبت وقوع الاصطدام والأضرار المذكورة نتيجة المخالفة المرصودة أعلاه.

**النتيجة النهائية وتوزيع نسب الخطأ:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}
* **السند النظامي المعتمد:** نظام المرور السعودي ولائحته التنفيذية.
            """

            st.session_state['report_ready'] = True
            st.session_state['p1_share'] = p1_share
            st.session_state['p2_share'] = p2_share
            st.session_state['tech_analysis'] = tech_analysis
            st.session_state['legal_qualification'] = legal_qualification
            st.session_state['official_report'] = official_report

# عرض التقرير بصيغة نظامية رسمية تليق بالعرض القيادي
if st.session_state.get('report_ready', False):
    st.markdown("---")
    st.markdown("### 📋 التقرير النظامي المفصل لمسرح الحادث")
    
    with st.expander("🔍 أولاً: التحليل الفني للحادث", expanded=True):
        st.markdown(st.session_state['tech_analysis'])
        
    with st.expander("📜 ثانياً: التكييف النظامي والمخالفة", expanded=True):
        st.markdown(st.session_state['legal_qualification'])
        
    with st.expander("📄 ثالثاً: التقرير الرسمي المعتمد", expanded=True):
        st.markdown(st.session_state['official_report'])
    
    st.markdown(f"""
        <div class="report-box">
            <h3 style="margin: 0 0 10px 0; color: #004d26; font-size: 19px;">📌 النسب النظامية النهائية المعتمدة:</h3>
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
        🖨️ طباعة التقرير الرسمي / حفظ كـ PDF
    </button>
    """
    st.components.v1.html(print_html, height=70)
