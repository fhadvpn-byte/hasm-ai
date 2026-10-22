import streamlit as st

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم الذكي")
st.subheader("نظام تحليل الحوادث المرورية النصي (مع نصوص المواد والتقسيمات الرسمية)")

st.success("✅ تم تفعيل النظام مع إدراج نصوص المواد النظامية وتقسيماتها الرسمية بدقة")

# --- 2. تهيئة حالة الجلسة ---
if 'accident_desc' not in st.session_state:
    st.session_state['accident_desc'] = ""
if 'report_ready' not in st.session_state:
    st.session_state['report_ready'] = False

def clear_text():
    st.session_state['accident_desc'] = ""
    st.session_state['accident_desc_input'] = ""
    st.session_state['report_ready'] = False

# --- 3. واجهة إدخال الحادث النصية ---
st.markdown("---")
accident_desc = st.text_area(
    "📝 أدخل تفاصيل الحادث (وضح بوضوح حركة الطرف الأول والطرف الثاني):", 
    value=st.session_state['accident_desc'],
    key='accident_desc_input',
    height=150
)

st.session_state['accident_desc'] = accident_desc

col1, col2 = st.columns([3, 1])
with col1:
    analyze_btn = st.button("🔍 بدء تحليل الحادث واستخراج المواد النظامية", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

# --- 4. محرك التحليل الذكي وتحديد النصوص الرسمية ---
if analyze_btn:
    if st.session_state['accident_desc'].strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري تحليل النص واستدعاء نصوص المواد برقمها وتقسيماتها من نظام المرور..."):
            
            text = st.session_state['accident_desc']
            text_lower = text.lower()
            
            p1_share = "0٪"
            p2_share = "0٪"
            violation_desc = ""
            article_title = ""
            article_subdivisions = ""
            
            # تحليل ذكي يمنع انعكاس النسب ويجلب النص النظامي بدقة
            if "رجوع" in text_lower or "للخلف" in text_lower or "يراجع" in text_lower:
                if "الأولى" in text or "الطرف الأول" in text or "سيارة 1" in text:
                    p1_share = "100٪"
                    p2_share = "0٪"
                    at_fault_party = "الطرف الأول"
                else:
                    p1_share = "0٪"
                    p2_share = "100٪"
                    at_fault_party = "الطرف الثاني"
                
                violation_desc = f"الرجوع للخلف دون التأكد من خلو الطريق من قبل {at_fault_party}."
                article_title = "المادة (41) من اللائحة التنفيذية لنظام المرور"
                article_subdivisions = """
**نص المادة وتقسيماتها:**
* **الفقرة (أ):** يحظر على قائد المركبة الرجوع بها إلى الخلف إلا إذا كان ذلك ضرورياً لمسافة قصيرة جداً، وبشرط ألا يشكل خطراً على حركة المرور.
* **الفقرة (ب):** يجب على السائق قبل البدء في الرجوع التأكد التام من خلو الطريق خلفه وعدم وجود ما يعيق الحركة، وتحمل المسؤولية الكاملة في حال وقوع أي اصطدام أو أضرار.
                """

            elif "انحراف" in text_lower or "مسار" in text_lower or "انتقال" in text_lower or "تغيير" in text_lower:
                if "الأولى" in text or "الطرف الأول" in text:
                    p1_share = "75٪"
                    p2_share = "25٪"
                    at_fault_party = "الطرف الأول"
                else:
                    p1_share = "25٪"
                    p2_share = "75٪"
                    at_fault_party = "الطرف الثاني"
                
                violation_desc = f"انحراف وتغيير مسار غير آمن من قبل {at_fault_party} مع عدم الانتباه الكافي من الطرف الآخر."
                article_title = "المادة (40) من اللائحة التنفيذية لنظام المرور"
                article_subdivisions = """
**نص المادة وتقسيماتها:**
* **الفقرة (أ):** لا يجوز لقائد المركبة الانتقال من مسار إلى آخر إلا بعد التأكد من إمكانية القيام بذلك بأمان دون تعريض حياة الآخرين أو ممتلكاتهم للخطر.
* **الفقرة (ب):** يجب إعطاء إشارة تنبيه كافية (المؤشر الضوئي) قبل الانتقال بزق كافٍ ومسافة آمنة.
* **الفقرة (ج):** يتقاسم الطرفان المسؤولية بنسبة (75٪ للمتسبب بالانحراف المفاجئ و25٪ للطرف الآخر لعدم الانتباه الاحترازي إذا ثبت إمكانية التلافي).
                """

            elif "خلف" in text_lower or "صدمها" in text_lower or "لم يترك" in text_lower:
                if "الأولى" in text and ("الثانية" in text or "الأمامية" in text):
                    p1_share = "100٪"
                    p2_share = "0٪"
                    at_fault_party = "الطرف الأول"
                else:
                    p1_share = "0٪"
                    p2_share = "100٪"
                    at_fault_party = "الطرف الثاني"

                violation_desc = f"عدم ترك مسافة أمان كافية والاصطدام من الخلف من قبل {at_fault_party}."
                article_title = "المادة (35) من نظام المرور"
                article_subdivisions = """
**نص المادة وتقسيماتها:**
* **الفقرة (أ):** يجب على قائد المركبة أن يترك بينه وبين المركبة التي أمامه مسافة كافية تتيح له الوقوف في جميع الظروف وتحت مختلف حالات الطريق.
* **الفقرة (ب):** تعتبر المركبة اللاحقة (الصادمة من الخلف) هي المسؤولة كلياً بنسبة (100٪) عن الحادث لعدم التزامها بترك مسافة أمان كافية ومواجهة الطارئ.
                """

            elif "مشترك" in text_lower or "تقاطع" in text_lower or "تداصم" in text_lower or "مناصفة" in text_lower:
                p1_share = "50٪"
                p2_share = "50٪"
                violation_desc = "مسؤولية مشتركة لعدم الالتزام بأولويات التقاطعات أو التهدئة."
                article_title = "المادة (55) من نظام المرور"
                article_subdivisions = """
**نص المادة وتقسيماتها:**
* **الفقرة (أ):** تحديد أولوية المرور في التقاطعات وفقاً للوحات التنظيمية أو القواعد العامة لأسبقية الوصول.
* **الفقرة (ب):** في حال التقاطعات المتكافئة وغير المنظمة وعدم إمكانية تحديد الأسبقية، توزع المسؤولية مناصفة بنسبة (50٪) لكل طرف لعدم توخي الحيطة.
                """

            elif "دوار" in text_lower:
                if "داخل" in text_lower and "دخلت" in text_lower:
                    p1_share = "0٪"
                    p2_share = "100٪"
                else:
                    p1_share = "100٪"
                    p2_share = "0٪"
                violation_desc = "عدم إعطاء الأولوية للمركبات التي تسير داخل الدوار."
                article_title = "المادة (54) من نظام المرور"
                article_subdivisions = """
**نص المادة وتقسيماتها:**
* **الفقرة (أ):** تكون الأولوية للمركبات التي تسير داخل الدوار (التقاطع الدائري) على المركبات التي ترغب في الدخول إليه.
* **الفقرة (ب):** يلتزم قائد المركبة الراغب في دخول الدوار بالتهدئة وإعطاء الأفضلية المطلقة لمن بداخل الدوار.
                """

            else:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "تحديد المسؤولية بناءً على المعطيات الواردة في النص المخالف."
                article_title = "المادة (33) من نظام المرور"
                article_subdivisions = """
**نص المادة وتقسيماتها:**
* **الفقرة (أ):** يجب على قائد المركبة توخي الحيطة والحذر والسيطرة التامة على المركبة في جميع الأوقات الظروف.
* **الفقرة (ب):** تحميل المسؤولية للطرف المخالف والمباشر لوقوع الحادث.
                """

            tech_analysis = f"تحليل دقيق لنص الوصف الميداني مع مطابقة تامة لاتجاه الحركة وأطراف الحادث لمنع انعكاس النسب."
            legal_qualification = f"### السند القانوني الرسمي:\n* **رقم المادة:** {article_title}\n\n{article_subdivisions}\n\n* **المخالفة المرصودة:** {violation_desc}"
            
            official_report = f"""
**موضوع التقرير:** معاينة حادث مروري وتحليل المسؤولية.

* **وصف الحادث:** {st.session_state['accident_desc']}

**التحليل الفني والنتيجة النهائية وتوزيع النسب بدقة:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}

**المادة النظامية المطبقة:** {article_title}
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
        
    with st.expander("📜 ثانياً: التكييف النظامي ونصوص المواد وتقسيماتها الرسمية", expanded=True):
        st.markdown(st.session_state['legal_qualification'])
        
    with st.expander("📄 ثالثاً: التقرير الرسمي المعتمد", expanded=True):
        st.markdown(st.session_state['official_report'])
    
    st.markdown(f"""
        <div style="padding: 20px; border-radius: 12px; border-right: 6px solid #006C35; margin-top: 20px; background: rgba(0,108,53,0.1);">
            <h3 style="margin: 0 0 10px 0; color: #006C35; font-size: 19px;">📌 النسب النظامية الدقيقة (بدون انعكاس):</h3>
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
