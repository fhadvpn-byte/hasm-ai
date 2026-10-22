import streamlit as st
import os

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - معاينة مسرح الحادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل حوادث المرور - محرك تحديد المسؤولية المحايد")

st.success("✅ النظام جاهز: إدخال محايد لكلا الطرفين واستنتاج نسبة الخطأ بموضوعية")

# --- 2. تهيئة حالة الجلسة (Session State) ---
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_inputs():
    st.session_state['report_ready'] = False

# --- 3. واجهة بيانات مسرح الحادث المحايدة ---
st.markdown("---")
st.markdown("### 📋 بيانات ومعاينة مسرح الحادث الميدانية")

# معلومات الطريق والبيئة
col_a, col_b, col_c = st.columns(3)
with col_a:
    road_type = st.selectbox(
        "🛣️ نوع الطريق:",
        ["اختر...", "طريق رئيسي مستقيم", "طريق فرعي / محلي", "دوار (تقاطع دائري)", "تقاطع رباعي", "تقاطع ثلاثي (T)", "شارع خدمي / مواقف"]
    )
with col_b:
    traffic_sign = st.selectbox(
        "🛑 الإشارات واللوحات:",
        ["اختر...", "إشارة ضوئية (تعمل)", "إشارة ضوئية (معطلة / وميض)", "لوحة قف (Stop)", "لوحة أفضلية / أولوية", "بدون لوحات أو إشارات تنظم الأولوية"]
    )
with col_c:
    weather_cond = st.selectbox(
        "🌤️ الظروف الجوية والبيئية:",
        ["اختر...", "أحوال طبيعية / طريق جاف", "مطر / سطح زلق", "غبار / انعدام رؤية جزئي", "فترة الليل / إضاءة ضعيفة"]
    )

# قائمة الحركات الموحدة والمحايدة للطرفين
action_options = [
    "اختر وضعية وحركة المركبة...",
    "تسير بشكل نظامي ومستقيم في مسارها",
    "متوقفة وقوفاً تاماً ونظامياً",
    "تستعد للوقوف أو التهدئة",
    "انحراف وتغيير مسار مفاجئ غير آمن (متسبب)",
    "الرجوع للخلف دون تأكد من خلو الطريق (متسبب)",
    "الصدم من الخلف لعدم ترك مسافة أمان (متسبب)",
    "دخول مفاجئ للدوار دون إعطاء الأولوية (متسبب)",
    "تجاوز إشارة ضوئية حمراء / عدم إعطاء أولوية"
]

st.markdown("---")
st.markdown("### 🚗 بيانات المركبة الأولى (الطرف الأول)")
col1, col2 = st.columns(2)
with col1:
    veh1_type = st.selectbox("نوع المركبة الأولى:", ["اختر...", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي (جيب)", "مركبة تجارية / نقل خفيف", "دراجة نارية"], key="v1_t")
with col2:
    veh1_motion = st.selectbox("حركة ووضع المركبة الأولى:", action_options, key="v1_m")

st.markdown("---")
st.markdown("### 🚙 بيانات المركبة الثانية (الطرف الثاني)")
col3, col4 = st.columns(2)
with col3:
    veh2_type = st.selectbox("نوع المركبة الثانية:", ["اختر...", "مركبة صغيرة (سيدان)", "مركبة عائلية / دفع رباعي (جيب)", "مركبة تجارية / نقل خفيف", "دراجة نارية"], key="v2_t")
with col4:
    veh2_motion = st.selectbox("حركة ووضع المركبة الثانية:", action_options, key="v2_m")

st.markdown("---")
st.markdown("### 💥 نقاط الاصطدام وتلفيات الهيكل")
col5, col6 = st.columns(2)
with col5:
    impact_point = st.selectbox(
        "موقع الاصطدام الرئيسي بين الطرفين:",
        ["اختر...", "مقدمة الأولى بمؤخرة الثانية", "مقدمة الثانية بمؤخرة الأولى", "الجانب الأيسر / الأيمن (تداخل مسارات)", "مقدمة المركبتين (تقابل وجهاً لوجه)", "الرجوع للخلف على مركبة مستقرة"]
    )
with col6:
    damage_severity = st.selectbox(
        "حجم التلفيات المادية:",
        ["اختر...", "تلفيات بسيطة (سطحية)", "تلفيات متوسطة (هيكلية)", "تلفيات جسيمة (تأثر الشاصيه والمحرك)"]
    )

additional_notes = st.text_area("📝 ملاحظات المعاينة الميدانية وأقوال الأطراف الإضافية (اختياري)", height=80)

# توزيع أزرار التحكم
col_btn1, col_btn2 = st.columns([3, 1])
with col_btn1:
    analyze_btn = st.button("🔍 إصدار التقرير النظامي لمسرح الحادث", use_container_width=True)
with col_btn2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_inputs, use_container_width=True)

if analyze_btn:
    if road_type == "اختر..." or traffic_sign == "اختر..." or veh1_motion == "اختر وضعية وحركة المركبة..." or veh2_motion == "اختر وضعية وحركة المركبة..." or impact_point == "اختر...":
        st.warning("⚠️ الرجاء استكمال اختيار كافة الحقول الأساسية لمسرح الحادث للطرفين أولاً")
    else:
        with st.spinner("⏳ جاري تحليل المعطيات وتحديد الطرف المتسبب بدقة..."):
            
            # منطق ذكي لمعرفة أي الطرفين هو المخالف
            at_fault = None
            violation_type = ""
            
            # فحص هل المركبة الأولى هي المخالفة
            if "الرجوع للخلف" in veh1_motion:
                at_fault = "المركبة الأولى"
                violation_type = "الرجوع للخلف دون تأكد من خلو الطريق"
            elif "انحراف وتغيير مسار" in veh1_motion:
                at_fault = "المركبة الأولى"
                violation_type = "الانحراف وتغيير المسار بشكل غير آمن"
            elif "الصدم من الخلف" in veh1_motion:
                at_fault = "المركبة الأولى"
                violation_type = "عدم ترك مسافة أمان والاصطدام من الخلف"
            elif "دخول مفاجئ للدوار" in veh1_motion:
                at_fault = "المركبة الأولى"
                violation_type = "الدخول المفاجئ للدوار وعدم إعطاء الأولوية"
            elif "تجاوز إشارة ضوئية" in veh1_motion:
                at_fault = "المركبة الأولى"
                violation_type = "تجاوز الإشارة الضوئية الحمراء"
                
            # فحص هل المركبة الثانية هي المخالفة
            elif "الرجوع للخلف" in veh2_motion:
                at_fault = "المركبة الثانية"
                violation_type = "الرجوع للخلف دون تأكد من خلو الطريق"
            elif "انحراف وتغيير مسار" in veh2_motion:
                at_fault = "المركبة الثانية"
                violation_type = "الانحراف وتغيير المسار بشكل غير آمن"
            elif "الصدم من الخلف" in veh2_motion:
                at_fault = "المركبة الثانية"
                violation_type = "عدم ترك مسافة أمان والاصطدام من الخلف"
            elif "دخول مفاجئ للدوار" in veh2_motion:
                at_fault = "المركبة الثانية"
                violation_type = "الدخول المفاجئ للدوار وعدم إعطاء الأولوية"
            elif "تجاوز إشارة ضوئية" in veh2_motion:
                at_fault = "المركبة الثانية"
                violation_type = "تجاوز الإشارة الضوئية الحمراء"
            else:
                # تقاطع أو أولوية مشتركة إذا لم يوجد خطأ فادح واضح
                at_fault = "مشترك بين الطرفين"
                violation_type = "عدم الالتزام بقواعد الأولويات في التقاطعات"

            # صياغة النتائج بناءً على الطرف المحدد
            if at_fault == "المركبة الأولى":
                error_percentage = "100% على قائد المركبة الأولى"
                tech_analysis = f"""
1. **معاينة الموقع:** طريق ({road_type})، اللوحات والإشارات ({traffic_sign})، حالة الجو ({weather_cond}).
2. **وضعية الأطراف:** المركبة الأولى ({veh1_type} - {veh1_motion})، والمركبة الثانية ({veh2_type} - {veh2_motion}).
3. **نقطة الاصطدام وتلفيات الهيكل:** ({impact_point}) بحجم تلفيات ({damage_severity}).
                """
                legal_qualification = f"""
وفقاً لنظام المرور ولائحته التنفيذية بشأن المخالفات المرورية:
* مسؤولية الطرف المخالف عن كافة الأضرار الناتجة لارتكابه مخالفة ({violation_type}).
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن الحادث المروري.

* **بيانات الطريق والبيئة:** {road_type} | {traffic_sign} | {weather_cond}
* **المركبة الأولى:** {veh1_type} ({veh1_motion})
* **المركبة الثانية:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام:** {impact_point} ({damage_severity})
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد"}

**التحليل الفني والقانوني:** أثبتت المعاينة الميدانية لمسرح الحادث وتتبع الحركات أن المركبة الأولى هي من ارتكبت المخالفة المتمثلة في ({violation_type})، مما أدى إلى وقوع الاصطدام مع المركبة الثانية التي كانت تسير بوضع نظامي.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 100% على قائد المركبة الأولى.
* **السند النظامي:** مخالفة ({violation_type}).
                """
            elif at_fault == "المركبة الثانية":
                error_percentage = "100% على قائد المركبة الثانية"
                tech_analysis = f"""
1. **معاينة الموقع:** طريق ({road_type})، اللوحات والإشارات ({traffic_sign})، حالة الجو ({weather_cond}).
2. **وضعية الأطراف:** المركبة الأولى ({veh1_type} - {veh1_motion})، والمركبة الثانية ({veh2_type} - {veh2_motion}).
3. **نقطة الاصطدام وتلفيات الهيكل:** ({impact_point}) بحجم تلفيات ({damage_severity}).
                """
                legal_qualification = f"""
وفقاً لنظام المرور ولائحته التنفيذية بشأن المخالفات المرورية:
* مسؤولية الطرف المخالف عن كافة الأضرار الناتجة لارتكابه مخالفة ({violation_type}).
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن الحادث المروري.

* **بيانات الطريق والبيئة:** {road_type} | {traffic_sign} | {weather_cond}
* **المركبة الأولى:** {veh1_type} ({veh1_motion})
* **المركبة الثانية:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام:** {impact_point} ({damage_severity})
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد"}

**التحليل الفني والقانوني:** أثبتت المعاينة الميدانية لمسرح الحادث وتتبع الحركات أن المركبة الثانية هي من ارتكبت المخالفة المتمثلة في ({violation_type})، مما أدى إلى وقوع الاصطدام مع المركبة الأولى التي كانت تسير بوضع نظامي.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 100% على قائد المركبة الثانية.
* **السند النظامي:** مخالفة ({violation_type}).
                """
            else:
                error_percentage = "50% على المركبة الأولى و 50% على المركبة الثانية (مسؤولية مشتركة)"
                tech_analysis = f"""
1. **معاينة الموقع:** طريق ({road_type})، اللوحات والإشارات ({traffic_sign})، حالة الجو ({weather_cond}).
2. **وضعية الأطراف:** المركبة الأولى ({veh1_type} - {veh1_motion})، والمركبة الثانية ({veh2_type} - {veh2_motion}).
3. **نقطة الاصطدام وتلفيات الهيكل:** ({impact_point}) بحجم تلفيات ({damage_severity}).
                """
                legal_qualification = """
وفقاً للقواعد العامة لأولويات المرور والتقاطعات غير الإشارية:
* المسؤولية المناصفة (50% لكل طرف) لعدم التزام كل قائد مركبة بحق الأولوية والتهدئة.
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن حادث مروري بمسؤولية مشتركة.

* **بيانات الطريق والبيئة:** {road_type} | {traffic_sign} | {weather_cond}
* **المركبة الأولى:** {veh1_type} ({veh1_motion})
* **المركبة الثانية:** {veh2_type} ({veh2_motion})
* **نقطة الاصطدام:** {impact_point} ({damage_severity})
* **ملاحظات الميدان:** {additional_notes if additional_notes else "لا توجد"}

**التحليل الفني والقانوني:** أظهرت معاينة مسرح الحادث تقاطع مسارات الطرفين دون إعطاء أولوية واضحة لأحدهما أو عدم التزام الطرفين بالاحتياطات اللازمة، مما يجعل المسؤولية موزعة مناصفة بينهما.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 50% على المركبة الأولى و50% على المركبة الثانية.
* **السند النظامي:** قواعد الأولويات المشتركة.
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
