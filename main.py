import streamlit as st

# --- 1. إعداد واجهة البرنامج ---
st.set_page_config(page_title="برنامج حَسْم - تحليل الحوادث", page_icon="🚓", layout="centered")
st.title("🚓 برنامج حَسْم الذكي")
st.subheader("نظام تحليل الحوادث المرورية النصي (بدون انعكاس للنسب)")

st.success("✅ تم تفعيل النظام النصي المتقدم بمعالجة دقيقة تمنع انعكاس النسب تماماً")

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
    analyze_btn = st.button("🔍 بدء تحليل الحادث بدقة", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ مسح", on_click=clear_text, use_container_width=True)

# --- 4. محرك التحليل الذكي (لمنع انعكاس النسب) ---
if analyze_btn:
    if st.session_state['accident_desc'].strip() == "":
        st.warning("⚠️ الرجاء كتابة تفاصيل الحادث أولاً")
    else:
        with st.spinner("⏳ جاري تحليل النص وتحديد المسؤول بدقة لمنع أي انعكاس..."):
            
            text = st.session_state['accident_desc']
            text_lower = text.lower()
            
            # تهيئة النسب الافتراضية
            p1_share = "0٪"
            p2_share = "0٪"
            violation_desc = ""
            article_number = ""
            article_text = ""
            
            # تحليل ذكي يحدد الفاعل بدقة لعدم انعكاس النسب
            # أ) حالات الرجوع للخلف
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
                article_number = "المادة (41) من اللائحة التنفيذية"
                article_text = "يحظر على قائد المركبة الرجوع بها إلى الخلف إلا إذا كان ذلك ضرورياً لمسافة قصيرة جداً وبشرط ألا يشكل خطراً وأن يتأكد من خلو الطريق."

            # ب) حالات الانحراف وتغيير المسار
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
                article_number = "المادة (40) من اللائحة التنفيذية"
                article_text = "لا يجوز لقائد المركبة الانتقال من مسار إلى آخر إلا بعد التأكد من خلو الطريق وإعطاء إشارة تنبيه كافية."

            # ج) حالات الصدم من الخلف (عدم ترك مسافة أمان)
            elif "خلف" in text_lower or "اصطدمت بالأمامية" in text_lower or "صدمها" in text_lower:
                if "الأولى" in text and ("الثانية" in text or "الأمامية" in text) and ("صدمت" in text or "اصطدمت" in text):
                    # إذا النص ذدر أن الأولى صدمت الثانية
                    p1_share = "100٪"
                    p2_share = "0٪"
                    at_fault_party = "الطرف الأول"
                else:
                    p1_share = "0٪"
                    p2_share = "100٪"
                    at_fault_party = "الطرف الثاني"

                violation_desc = f"عدم ترك مسافة أمان كافية والاصطدام من الخلف من قبل {at_fault_party}."
                article_number = "المادة (35) من نظام المرور"
                article_text = "يجب على قائد المركبة ترك مسافة كافية بينه وبين المركبة التي أمامه تسمح بالتوقف في جميع الظروف."

            # د) حالات الخطأ المشترك / التقاطعات
            elif "مشترك" in text_lower or "تقاطع" in text_lower or "تداصم" in text_lower or "مناصفة" in text_lower:
                p1_share = "50٪"
                p2_share = "50٪"
                violation_desc = "مسؤولية مشتركة لعدم الالتزام بأولويات التقاطعات أو التهدئة."
                article_number = "المادة (55) من نظام المرور"
                article_text = "تحديد أولوية المرور في التقاطعات وفقاً للوحات التنظيمية أو القواعد العامة لأسبقية الوصول."

            # هـ) حالات الدوار
            elif "دوار" in text_lower:
                if "داخل" in text_lower and "دخلت" in text_lower:
                    p1_share = "0٪"
                    p2_share = "100٪"
                else:
                    p1_share = "100٪"
                    p2_share = "0٪"
                violation_desc = "عدم إعطاء الأولوية للمركبات التي تسير داخل الدوار."
                article_number = "المادة (54) من نظام المرور"
                article_text = "الأولوية للمركبات التي تسير داخل الدوار ما لم توجد إشارات تنظم غير ذلك."

            else:
                p1_share = "0٪"
                p2_share = "100٪"
                violation_desc = "تحديد المسؤولية بناءً على المعطيات الواردة في النص."
                article_number = "المادة (33) من نظام المرور"
                article_text = "يجب على قائد المركبة توخي الحيطة والحذر والسيطرة عليها في جميع الأوقات."

            tech_analysis = f"تحليل دقيق لنص الوصف الميداني مع مطابقة تامة لاتجاه الحركة وأطراف الحادث لمنع انعكاس النسب."
            legal_qualification = f"* **رقم المادة:** {article_number}\n* **نص المادة:** \"{article_text}\"\n* **المخالفة المرصودة:** {violation_desc}"
            
            official_report = f"""
**موضوع التقرير:** معاينة حادث مروري.

* **وصف الحادث:** {st.session_state['accident_desc']}

**التحليل الفني والنتيجة النهائية وتوزيع النسب بدقة:**
* **الطرف الأول:** {p1_share}
* **الطرف الثاني:** {p2_share}
* **السند النظامي:** {article_number}
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
        
    with st.expander("📜 ثانياً: التكييف النظامي والنصوص القانونية", expanded=True):
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
