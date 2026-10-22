import streamlit as st
import os

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - شامل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل حوادث المرور - المحرك الميداني الشامل")

st.success("✅ تم تفعيل واجهة الحوادث الشاملة (تصادم، انقلاب، سقوط، دهس، وغيرها)")

# --- 2. تهيئة حالة الجلسة (Session State) ---
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_inputs():
    st.session_state['report_ready'] = False

# --- 3. واجهة بيانات مسرح الحادث الشاملة ---
st.markdown("---")
st.markdown("### 📋 بيانات ومعاينة مسرح الحادث")

# التصنيف الرئيسي للحادث
accident_category = st.selectbox(
    "🚨 التصنيف الرئيسي للحادث:",
    [
        "اختر تصنيف الحادث...",
        "حادث تصادم بين مركبتين (أو أكثر)",
        "حادث انقلاب مركبة (فردي أو بسبب تفادي)",
        "حادث سقوط (من مرتفع / جسر / حفرة)",
        "حادث دهس مشاة",
        "حادث احتكاك / صدم جسم ثابت (رصيف، إنارة، جدار)"
    ]
)

# معلومات الطريق والبيئة المحيطة
col_a, col_b, col_c = st.columns(3)
with col_a:
    road_type = st.selectbox(
        "🛣️ نوع الطريق:",
        ["اختر...", "طريق رئيسي سريع", "طريق فرعي / محلي", "دوار (تقاطع دائري)", "تقاطع إشاري", "تقاطع غير منظم", "منحنى خطير"]
    )
with col_b:
    traffic_sign = st.selectbox(
        "🛑 التنظيم المروري:",
        ["اختر...", "إشارة ضوئية (تعمل)", "لوحة قف (Stop)", "لوحة أفضلية / أولوية", "بدون لوحات أو إشارات"]
    )
with col_c:
    weather_cond = st.selectbox(
        "🌤️ حالة الجو والطريق:",
        ["اختر...", "طريق جاف / طبيعي", "مطر / زلق", "غبار / انعدام رؤية", "ليلي / إضاءة ضعيفة"]
    )

st.markdown("---")
st.markdown("### 🚗 بيانات الطرف الأول (المتضرر أو المركبة الأساسية)")
col1, col2 = st.columns(2)
with col1:
    veh1_type = st.selectbox("نوع المركبة / الطرف الأول:", ["اختر...", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة / شخص"], key="v1_t")
with col2:
    veh1_motion = st.selectbox(
        "حركة الطرف الأول:",
        [
            "اختر حركة الطرف الأول...",
            "تسير بشكل نظامي ومستقيم",
            "متوقفة وقوفاً تاماً ونظامياً",
            "تستعد للوقوف أو تهدئة السرعة",
            "مستقرة داخل المسار / الدوار",
            "تغير مسارها بشكل نظامي"
        ],
        key="v1_m"
    )

st.markdown("---")
st.markdown("### 🚙 بيانات الطرف الثاني (المركبة الأخرى أو الجهة المتسببة - إن وجدت)")
col3, col4 = st.columns(2)
with col3:
    veh2_type = st.selectbox("نوع الطرف الثاني:", ["لا يوجد (حادث طرف واحد)", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي", "مركبة تجارية / نقل", "دراجة نارية", "مشاة"], key="v2_t")
with col4:
    veh2_motion = st.selectbox(
        "حركة أو فعل الطرف الثاني / سبب الحادث:",
        [
            "اختر حركة أو سبب الحادث...",
            "انحراف وتغيير مسار مفاجئ غير آمن",
            "الرجوع للخلف دون تأكد من خلو الطريق",
            "الصدم من الخلف (عدم ترك مسافة أمان)",
            "تجاوز إشارة حمراء / عدم إعطاء أولوية",
            "سرعة زائدة أدت إلى فقدان السيطرة والانقلاب",
            "تفادي مفاجئ أدى إلى الانقلاب أو السقوط",
            "دخول مفاجئ للدوار دون إعطاء أولوية",
            "عدم الالتزام بأولويات التقاطعات",
            "الاصطدام بجسم ثابت (رصيف / حاجز / إنارة)"
        ],
        key="v2_m"
    )

st.markdown("---")
st.markdown("### 💥 نقاط الاصطدام وتلفيات الهيكل")
col5, col6 = st.columns(2)
with col5:
    impact_point = st.selectbox(
        "موقع الاصطدام أو الضرر الرئيسي:",
        [
            "اختر نقطة الاصطدام...",
            "مقدمة المركبة بمؤخرة المركبة الأخرى (خلفي)",
            "الجانب الأيسر / الأيمن (تداخل مسارات)",
            "مقدمة المركبتين (تقابل وجهاً لوجه)",
            "انقلاب كلي / جزئي للمركبة",
            "سقوط من مرتفع أو جسر",
            "اصطدام بمقدمة المركبة في جسم ثابت",
            "دهس مشاة"
        ]
    )
with col6:
    damage_severity = st.selectbox(
        "حجم التلفيات المادية:",
        ["اختر...", "تلفيات بسيطة (سطحية)", "تلفيات متوسطة (هيكلية)", "تلفيات جسيمة / تلف الهيكل بالكامل"]
    )

additional_notes = st.text_area("📝 ملاحظات المعاينة الميدانية وأقوال الأطراف الإضافية (اختياري)", height=80)

# أزرار التحكم
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_btn = st.button("🔍 إصدار التقرير النظامي لمسرح الحادث", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_inputs, use_container_width=True)

if analyze_btn:
    if accident_category == "اختر تصنيف الحادث..." or road_type == "اختر..." or veh1_motion == "اختر حركة الطرف الأول..." or impact_point == "اختر نقطة الاصطدام...":
        st.warning("⚠️ الرجاء استكمال اختيار الحقول الأساسية لمسرح الحادث أولاً")
    else:
        with st.spinner("⏳ جاري تحليل بيانات مسرح الحادث واستخراج التقرير النظامي..."):
            
            # محرك تحليل الحوادث
            violation_desc = veh2_motion
            
            if "انقلاب" in accident_category or "انقلاب" in impact_point:
                if "سرعة" in veh2_motion or "فقدان السيطرة" in veh2_motion:
                    error_percentage = "100% على قائد المركبة المنقلبة (بسبب السرعة وعدم السيطرة)"
                else:
                    error_percentage = "100% على الطرف المتسبب الذي أجبر المركبة على الانحراف أو التفادي المفاجئ"
            elif "سقوط" in accident_category or "سقوط" in impact_point:
                error_percentage = "100% على قائد المركبة لعدم الانتباه ومراعاة حالة الطريق"
            elif "دهس" in accident_category:
                error_percentage = "تحدد المسؤولية بناءً على عبور المشاة من غير الأماكن المخصصة أو خطأ السائق"
            elif "الرجوع للخلف" in veh2_motion:
                error_percentage = "100% على قائد الطرف الثاني (بسبب الرجوع للخلف دون تأكد)"
            elif "انحراف" in veh2_motion:
                error_percentage = "75% على الطرف الثاني المتسبب بالانحراف و 25% على الطرف الأول"
            elif "الصدم من الخلف" in veh2_motion:
                error_percentage = "100% على قائد الطرف الثاني (بسبب عدم ترك مسافة أمان)"
            elif "دوار" in road_type or "دوار" in veh2_motion:
                error_percentage = "100% على قائد الطرف الثاني (الدخول الخاطئ للدوار)"
            elif "تقاطع" in road_type:
                error_percentage = "50% على كل طرف (مسؤولية مشتركة لعدم الالتزام بالأولويات)"
            else:
                error_percentage = "100% على الطرف المتسبب في الحادث"

            tech_analysis = f"""
1. **تصنيف الحادث:** {accident_category} على طريق ({road_type}) مع تنظيم ({traffic_sign}) وظروف بيئية ({weather_cond}).
2. **أطراف الحادث:** الطرف الأول ({veh1_type} - {veh1_motion}) والطرف الثاني ({veh2_type} - {veh2_motion}).
3. **نقطة الاصطدام والضرر:** ({impact_point}) بحجم تلفيات مقدرة بـ ({damage_severity}).
            """
            
            legal_qualification = f"""
وفقاً لنظام المرور ولائحته التنفيذية بشأن قواعد السير والسلامة المرورية:
* تطبيق المواد النظامية المتعلقة بالسيطرة، ترك مسافة الأمان، الالتزام بالمسارات، ومراعاة حقوق الأولوية.
            """
            
            official_report = f"""
**موضوع التقرير:** معاينة وتحديد المسؤولية عن حادث ({accident_category}).

* **بيانات الموقع:** {road_type} | التنظيم: {traffic_sign} | الحالة: {weather_cond}
* **الطرف الأول:** {veh1_type} ({veh1_motion})
* **الطرف الثاني:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام / الضرر:** {impact_point} ({damage_severity})
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد ملاحظات إضافية"}

**التحليل الفني والقانوني:** بناءً على المعطيات الفعلية لمسرح الحادث وتتبع حركة الأطراف، ثبت وقوع الحادث نتيجة ({violation_desc}), مما أدى إلى حدوث الأضرار المادية المذكورة.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** {error_percentage}
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
    
    st.markdown("---")
    st.markdown("### أولاً: التحليل الفني للحادث")
    st.markdown(st.session_state['tech_analysis'])
    
    st.markdown("---")
    st.markdown("### ثانياً: التكييف النظامي (المخالفة)")
    st.markdown(st.session_state['legal_qualification'])
    
    st.markdown("---")
    st.markdown("### ثالثاً: تقرير الحادث (بصياغة رسمية)")
    st.markdown(st.session_state['official_report'])
    
    st.markdown(f"**📌 نسبة الخطأ المعتمدة في النظام:** {st.session_state['error_percentage']}")

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
        padding: 12px 20px;
        border: none;
        border-radius: 8px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        width: 100%;">
        🖨️ طباعة التقرير / حفظ كـ PDF
    </button>
    """
    st.components.v1.html(print_html, height=60)
