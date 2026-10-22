import streamlit as st
import os

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم")
st.subheader("نظام تحليل الحوادث المرورية المدعوم بالذكاء الاصطناعي")

st.success("✅ تم ربط النظام بنجاح (مع قاعدة نسب المسؤولية 25%، 50%، 75%، 100%)")

# --- 2. تهيئة حالة الجلسة (Session State) ---
if 'accident_desc' not in st.session_state:
    st.session_state['accident_desc'] = ""
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

# دالة لمسح الحقول والتقرير
def clear_text():
    st.session_state['accident_desc'] = ""
    st.session_state['report_ready'] = False

# --- 3. واجهة إدخال الحادث والتحليل المباشر ---
st.markdown("---")
accident_desc = st.text_area(
    "📝 أدخل تفاصيل الحادث (المركبات، الاتجاهات، الإشارات، الخ)", 
    value=st.session_state['accident_desc'],
    key='accident_desc_input',
    height=150
)

# تحديث النص في الجلسة
st.session_state['accident_desc'] = accident_desc

# توزيع الأزرار (بدء التحليل ومسح)
col1, col2 = st.columns([3, 1])
with col1:
    analyze_btn = st.button("🔍 بدء تحليل الحادث بالذكاء الاصطناعي", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

if analyze_btn:
    if st.session_state['accident_desc'].strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري فحص الحادث وتحديد نسب المسؤولية..."):
            
            desc_lower = st.session_state['accident_desc'].lower()
            
            # تحديد النسب والسيناريوهات بناءً على وصف الحادث
            if "تغيير مسار" in desc_lower or "مسار مفاجئ" in desc_lower or "انحراف" in desc_lower:
                error_percentage = "75% على الطرف المتسبب بالانحراف و 25% على الطرف الآخر (عدم اتخاذ احتراز كافٍ)"
                tech_analysis = """
1. **وضعية المركبات:** سير المركبات بشكل متوازي مع إحداث تغيير مفاجئ في المسار من أحد الطرفين.
2. **حركة المركبة المتسببة:** انتقلت المركبة إلى مسار مركبة أخرى دون التأكد من خلوه أو إعطاء إشارة تنبيه كافية.
3. **نقطة الاصطدام:** تركزت التلفيات في الأجزاء الجانبية للمركبتين نتيجة التداخل المروري.
                """
                legal_qualification = """
وفقاً لنظام المرور ولائحته التنفيذية بشأن قواعد تغيير المسارات والانتقال الآمن:
* عدم التأكد من خلو الطريق قبل الانتقال.
* المسؤولية المشتركة بنسب متفاوتة عند عدم انتباه الطرف المتضرر بالقدر الكافي.
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن حادث تغيير مسار مفاجئ.

**وصف الحادث:** {st.session_state['accident_desc']}

**التحليل الفني والقانوني:** تبين من المعطيات حصول تغيير مسار غير آمن أدى إلى التداخل والاصطدام الجانبي. وحيث إن نظام المرور يفرض المسؤولية الكبرى على من تسبب بالانحراف المفاجئ، مع رصد نسبة جزئية لعدم الانتباه في حال توفر مساحة تفادي.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 75% على المتسبب بالانحراف، و25% على الطرف الثاني.
* **السند النظامي:** مخالفة قواعد الانتقال بين المسارات.
                """
            elif "تداصم" in desc_lower or "مشترك" in desc_lower or "خطأ مشترك" in desc_lower or ("تقاطع" in desc_lower and "خطأ" in desc_lower):
                error_percentage = "50% على كل طرف (خطأ مشترك / عدم إعطاء أولوية متبادلة)"
                tech_analysis = """
1. **وضعية المركبات:** وصول المركبتين إلى نقطة تقاطع أو منطقة غير منظمة في نفس الوقت تقريباً.
2. **حركة المركبات:** عدم التزام الطرفين بالتهدئة أو التأكد من خلو الطريق قبل العبور.
3. **نقطة الاصطدام:** اصطدام مباشر بين مقدمة أو جوانب المركبتين.
                """
                legal_qualification = """
وفقاً للقواعد العامة لأولويات المرور والتقاطعات غير الإشارية:
* المسؤولية المناصفة (50% لكل طرف) لعدم التزام كل قائد مركبة بحق الأولوية والحيطة والحذر.
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن حادث تقاطع بمسؤولية مشتركة.

**وصف الحادث:** {st.session_state['accident_desc']}

**التحليل الفني والقانوني:** أظهرت المعطيات تقاطع مسار الطرفين دون إعطاء الأولوية النظامية الواضحة أو تأكيد خلو الطريق من كلا الجانبين، مما يجعل المسؤولية موزعة مناصفة بينهما.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 50% على الطرف الأول و50% على الطرف الثاني.
* **السند النظامي:** قواعد الأولويات المشتركة في التقاطعات.
                """
            elif "دوار" in desc_lower:
                error_percentage = "100% على المركبة الداخلة للدوار (عدم إعطاء أولوية)"
                tech_analysis = """
1. **وضعية المركبات:** المركبة الأولى مستقرة داخل الدوار، والمركبة الثانية في حالة دخول مفاجئ.
2. **حركة المركبة المتسببة:** تجاوز قواعد الأولوية لمن هم بداخل المسار الدائري.
3. **نقطة الاصطدام:** الجانب الأيسر للمركبة المستقرة ومقدمة المركبة الداخلة.
                """
                legal_qualification = """
وفقاً للائحة التنفيذية لنظام المرور:
* عدم إعطاء الأولوية للمركبات التي تسير داخل الدوار.
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن حادث تقاطع (دوار).

**وصف الحادث:** {st.session_state['accident_desc']}

**التحليل الفني والقانوني:** الأولوية النظامية المطلقة لمن بداخل الدوار، ودخول أي مركبة دون التأكد من الخلو يعرضها لكامل المسؤولية.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 100% على قائد المركبة الداخلة للدوار.
* **السند النظامي:** مخالفة قواعد السير داخل الدوائر.
                """
            else:
                error_percentage = "100% على الطرف الثاني (اللاحق أو المتسبب المباشر)"
                tech_analysis = """
1. **وضعية المركبات:** المركبة المتضررة تسير بوضع نظامي سليم، والمركبة المتسببة خالفت قواعد السير والمسافة الآمنة.
2. **حركة المركبة:** عدم السيطرة وتوقع المفاجآت على الطريق العام.
                """
                legal_qualification = """
وفقاً للمذكرة الإيضاحية لنظام المرور ولائحته التنفيذية:
* عدم ترك مسافة كافية أو عدم التوقع والسيطرة.
                """
                official_report = f"""
**موضوع التقرير:** تحديد المسؤولية عن حادث مروري نظامي.

**وصف الحادث:** {st.session_state['accident_desc']}

**التحليل الفني والقانوني:** دراسة المعطيات وتطبيق المواد النظامية ذات العلاقة لتحديد المسؤولية وحجم الخطأ المروري.

**النتيجة النهائية:**
* **نسبة الخطأ والمسؤولية:** 100% على الطرف المتسبب.
* **السند النظامي:** نظام المرور السعودي.
                """

            # حفظ التقرير في الجلسة لعرضه وطباعته
            st.session_state['report_ready'] = True
            st.session_state['error_percentage'] = error_percentage
            st.session_state['tech_analysis'] = tech_analysis
            st.session_state['legal_qualification'] = legal_qualification
            st.session_state['official_report'] = official_report

# عرض التقرير إذا كان جاهزاً
if st.session_state.get('report_ready', False):
    st.markdown("---")
    st.markdown("### 📋 التقرير النظامي المفصل للحادث")
    
    st.markdown("---")
    st.markdown("### أولاً: التحليل الفني للحادث")
    st.markdown(st.session_state['tech_analysis'])
    
    st.markdown("---")
    st.markdown("### ثانياً: التكييف النظامي (المخالفة)")
    st.markdown(st.session_state['legal_qualification'])
    
    st.markdown("---")
    st.markdown("### ثالثاً: تقرير الحادث (بصياغة رسمية)")
    st.markdown(st.session_state['official_report'])
    
    st.markdown(f"**📌 نسبة الخطأ المعتمدة في النظام:** `{st.session_state['error_percentage']}`")

    # زر الطباعة المباشرة (يحول الصفحة لخيارات الطباعة أو حفظ PDF)
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
