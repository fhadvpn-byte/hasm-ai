import streamlit as st
import os
import base64
import re
from datetime import datetime
import streamlit.components.v1 as components
# استيراد المكتبات بمرونة
try:
    from groq import Groq
except ImportError:
    Groq = None
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        PdfReader = None
# ==================== إعدادات الصفحة ====================
st.set_page_config(
    page_title="حسم الذكي | Vision 2030 GovTech",
    page_icon="🚓",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# ==================== إدارة الجلسة (Session State) ====================
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "report_meta" not in st.session_state:
    st.session_state.report_meta = {}
def reset_all_fields():
    st.session_state.analysis_result = None
    st.session_state.report_meta = {}
    st.session_state.reset_counter += 1
# ==================== قراءة شعار المرور ====================
def get_logo_base64():
    for file_name in ["traffic_logo.png", "traffic_logo.png.png", "logo.png"]:
        if os.path.exists(file_name):
            try:
                with open(file_name, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
    return None
logo_b64 = get_logo_base64()
if logo_b64:
    center_hologram_content = f'<img src="data:image/png;base64,{logo_b64}" class="holo-logo-img" alt="شعار المرور">'
    watermark_bg = f"""
    .stApp::after {{
        content: "";
        position: fixed;
        top: 52%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 480px;
        height: 480px;
        background-image: url("data:image/png;base64,{logo_b64}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        opacity: 0.04;
        pointer-events: none;
        z-index: 0;
        filter: drop-shadow(0 0 25px #00f2fe);
    }}
    """
else:
    center_hologram_content = """
    <svg viewBox="0 0 100 100" width="78" height="78" fill="none">
        <circle cx="50" cy="50" r="44" stroke="#00f2fe" stroke-width="2" stroke-dasharray="6 4"/>
        <circle cx="50" cy="50" r="32" stroke="#38bdf8" stroke-width="1.5" fill="rgba(0,242,254,0.12)"/>
        <path d="M50 22L72 34V54C72 69 50 80 50 80C50 80 28 69 28 54V34L50 22Z" stroke="#ffffff" stroke-width="2.2" fill="rgba(14,165,233,0.35)"/>
        <circle cx="50" cy="50" r="8" fill="#00f2fe"/>
    </svg>
    """
    watermark_bg = ""
# ==================== التصميم الهولوغرامي الإبداعي الكامل (Vision 2030 Hologram UI) ====================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&family=Orbitron:wght@700;900&display=swap');
html, body, [class*="css"], .stApp {{
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
}}
.stApp, [data-testid="stAppViewContainer"] {{
    background:
        radial-gradient(circle at 50% -10%, rgba(0, 242, 254, 0.35) 0%, rgba(2, 132, 199, 0.15) 30%, transparent 65%),
        radial-gradient(circle at 15% 20%, rgba(14, 165, 233, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 85% 20%, rgba(14, 165, 233, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(0, 242, 254, 0.25) 0%, transparent 55%),
        linear-gradient(180deg, #020b1c 0%, #041938 45%, #031126 80%, #010712 100%) !important;
    color: #ffffff !important;
    background-attachment: fixed !important;
}}
.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background-image: 
        linear-gradient(rgba(0, 242, 254, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 242, 254, 0.04) 1px, transparent 1px);
    background-size: 45px 45px;
    pointer-events: none;
    z-index: 0;
}}
{watermark_bg}
[data-testid="stHeader"] {{
    background: transparent !important;
}}
.block-container {{
    max-width: 1050px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    position: relative;
    z-index: 2;
}}
.vision-hero-card {{
    background: linear-gradient(135deg, rgba(8, 48, 107, 0.9) 0%, rgba(3, 25, 62, 0.95) 100%);
    border: 2px solid #00f2fe;
    border-radius: 26px;
    padding: 26px 32px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    box-shadow: 
        0 0 35px rgba(0, 242, 254, 0.45),
        inset 0 0 28px rgba(0, 242, 254, 0.22);
    position: relative;
    overflow: hidden;
}}
.top-mini-badge {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 242, 254, 0.16);
    border: 1px solid #00f2fe;
    color: #e0f2fe;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
    width: fit-content;
    box-shadow: 0 0 12px rgba(0, 242, 254, 0.4);
}}
.vision-2030-title {{
    font-family: 'Orbitron', 'Tajawal', sans-serif;
    font-size: 2.7rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.1;
    letter-spacing: 2px;
    text-shadow: 0 0 20px #00f2fe, 0 0 40px rgba(0, 242, 254, 0.7);
    margin: 4px 0;
}}
.vision-2030-title span {{
    color: #00f2fe;
}}
.hasm-main-title {{
    font-size: 1.75rem;
    font-weight: 900;
    color: #ffffff;
    margin: 0;
    text-shadow: 0 0 14px rgba(56, 189, 248, 0.8);
}}
.hasm-subtitle {{
    color: #7dd3fc;
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
}}
.holo-orb-wrapper {{
    position: relative;
    width: 138px;
    height: 138px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    z-index: 2;
}}
.holo-orb-ring-outer {{
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 2.5px solid #00f2fe;
    box-shadow: 0 0 28px #00f2fe, inset 0 0 22px #00f2fe;
    animation: pulseGlow 3s infinite ease-in-out;
}}
.holo-orb-ring-inner {{
    position: absolute;
    inset: 12px;
    border-radius: 50%;
    border: 1.5px dashed #bae6fd;
    background: radial-gradient(circle, rgba(0, 242, 254, 0.35) 0%, rgba(2, 132, 199, 0.1) 70%);
}}
.holo-logo-img {{
    width: 82px;
    height: 82px;
    object-fit: contain;
    z-index: 3;
    filter: drop-shadow(0 0 12px #ffffff);
}}
@keyframes pulseGlow {{
    0%, 100% {{ transform: scale(1); opacity: 0.95; }}
    50% {{ transform: scale(1.04); opacity: 1; box-shadow: 0 0 42px #00f2fe, inset 0 0 30px #00f2fe; }}
}}
.holo-status-pill {{
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.18) 0%, rgba(14, 165, 233, 0.08) 100%);
    border: 1.5px solid rgba(0, 242, 254, 0.7);
    border-radius: 999px;
    padding: 10px 22px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.25);
}}
.holo-status-pill .dot {{
    width: 11px;
    height: 11px;
    background: #00f2fe;
    border-radius: 50%;
    display: inline-block;
    margin-left: 10px;
    box-shadow: 0 0 12px #00f2fe;
}}
.neon-section-card {{
    background: linear-gradient(160deg, rgba(7, 41, 92, 0.78) 0%, rgba(4, 21, 51, 0.88) 100%) !important;
    backdrop-filter: blur(16px);
    border: 1.8px solid rgba(0, 242, 254, 0.65) !important;
    border-radius: 24px !important;
    padding: 22px 24px !important;
    margin-bottom: 22px !important;
    box-shadow: 
        0 10px 35px rgba(0, 0, 0, 0.55),
        0 0 25px rgba(0, 242, 254, 0.22),
        inset 0 0 22px rgba(0, 242, 254, 0.1) !important;
    position: relative;
}}
.neon-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(0, 242, 254, 0.3);
    padding-bottom: 12px;
    margin-bottom: 16px;
}}
.neon-card-title {{
    color: #ffffff !important;
    font-size: 1.35rem !important;
    font-weight: 900 !important;
    text-shadow: 0 0 14px rgba(0, 242, 254, 0.75);
    display: flex;
    align-items: center;
    gap: 10px;
}}
.neon-badge {{
    background: linear-gradient(90deg, #00f2fe 0%, #0284c7 100%);
    color: #011627 !important;
    font-weight: 900;
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 999px;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.7);
}}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {{
    background: rgba(3, 19, 46, 0.88) !important;
    border: 1.4px solid rgba(56, 189, 248, 0.55) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.1) !important;
    transition: all 0.25s ease !important;
}}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
textarea:focus {{
    border-color: #00f2fe !important;
    box-shadow: 0 0 18px rgba(0, 242, 254, 0.65), inset 0 0 12px rgba(0, 242, 254, 0.2) !important;
}}
label, .stRadio label, .stCheckbox label {{
    color: #bae6fd !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}}
div.stButton > button, div.stDownloadButton > button {{
    width: 100% !important;
    height: 54px !important;
    background: linear-gradient(90deg, #e0f2fe 0%, #00f2fe 50%, #38bdf8 100%) !important;
    color: #021024 !important;
    border: 2px solid #ffffff !important;
    border-radius: 999px !important;
    font-size: 1.08rem !important;
    font-weight: 900 !important;
    box-shadow: 0 0 28px rgba(0, 242, 254, 0.75) !important;
    transition: all 0.3s ease !important;
}}
div.stButton > button:hover, div.stDownloadButton > button:hover {{
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 0 42px rgba(0, 242, 254, 1) !important;
    background: linear-gradient(90deg, #ffffff 0%, #7dd3fc 100%) !important;
}}
.holo-bottom-dock {{
    background: rgba(4, 22, 52, 0.9);
    border: 1.5px solid rgba(0, 242, 254, 0.55);
    border-radius: 999px;
    padding: 10px 28px;
    margin-top: 18px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
    color: #7dd3fc;
    font-size: 0.88rem;
    font-weight: 700;
}}
.holo-bottom-dock span.active {{
    color: #00f2fe;
    text-shadow: 0 0 10px #00f2fe;
}}
/* ==================== تنسيق التقرير الرسمي والطباعة الهولوغرامية ==================== */
#official-report-container {{
    background: radial-gradient(circle at 50% 0%, #0a3570 0%, #041938 55%, #020b1c 100%) !important;
    color: #ffffff !important;
    border-radius: 26px !important;
    padding: 28px 32px !important;
    margin-top: 24px !important;
    border: 2.5px solid #00f2fe !important;
    box-shadow: 0 0 40px rgba(0, 242, 254, 0.45), inset 0 0 25px rgba(0, 242, 254, 0.18) !important;
    direction: rtl !important;
    position: relative !important;
    overflow: visible !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}
.report-holo-header {{
    background: linear-gradient(135deg, rgba(8, 52, 115, 0.92) 0%, rgba(3, 24, 58, 0.96) 100%) !important;
    border: 2px solid #00f2fe !important;
    border-radius: 20px !important;
    padding: 18px 24px !important;
    margin-bottom: 20px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 18px rgba(0, 242, 254, 0.2) !important;
}}
.report-vision-tag {{
    font-family: 'Orbitron', 'Tajawal', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    letter-spacing: 1.5px !important;
    text-shadow: 0 0 15px #00f2fe !important;
    margin: 0 0 4px 0 !important;
}}
.report-vision-tag span {{
    color: #00f2fe !important;
}}
#official-report-container h2,
#official-report-container h3,
#official-report-container h4 {{
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.22) 0%, rgba(4, 25, 56, 0.4) 100%) !important;
    color: #00f2fe !important;
    font-weight: 900 !important;
    border-right: 4px solid #00f2fe !important;
    border-bottom: 1px solid rgba(0, 242, 254, 0.4) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin-top: 18px !important;
    margin-bottom: 12px !important;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.5) !important;
}}
#official-report-container p,
#official-report-container li,
#official-report-container div {{
    color: #e0f2fe !important;
    line-height: 1.8 !important;
    font-size: 0.98rem !important;
}}
#official-report-container strong {{
    color: #ffffff !important;
}}
#official-report-container table {{
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    margin: 14px 0 !important;
    background: rgba(4, 22, 52, 0.85) !important;
    border: 1.5px solid #00f2fe !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.2) !important;
}}
#official-report-container table th,
#official-report-container table thead tr {{
    background: linear-gradient(90deg, #0284c7 0%, #00f2fe 100%) !important;
    color: #011627 !important;
    font-weight: 900 !important;
    font-size: 0.96rem !important;
    padding: 11px 14px !important;
    border-bottom: 2px solid #ffffff !important;
    text-align: right !important;
}}
#official-report-container table td {{
    background: rgba(6, 30, 68, 0.82) !important;
    color: #f0f9ff !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid rgba(0, 242, 254, 0.25) !important;
    border-left: 1px solid rgba(0, 242, 254, 0.15) !important;
    text-align: right !important;
    font-weight: 600 !important;
}}
#official-report-container table tr:nth-child(even) td {{
    background: rgba(10, 42, 90, 0.88) !important;
    color: #ffffff !important;
}}
@media print {{
    @page {{
        size: A4 portrait;
        margin: 6mm !important;
    }}
    * {{
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        color-adjust: exact !important;
    }}
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container {{
        background: #020b1c !important;
        color: #ffffff !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }}
    header, [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"], .no-print,
    .vision-hero-card, .holo-status-pill, .holo-bottom-dock,
    div.stButton, div.stDownloadButton, iframe {{
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    #official-report-container {{
        background: radial-gradient(circle at 50% 0%, #0a3570 0%, #041938 60%, #020b1c 100%) !important;
        border: 2.5px solid #00f2fe !important;
        border-radius: 22px !important;
        margin: 0 !important;
        padding: 20px 24px !important;
        width: 100% !important;
        box-shadow: inset 0 0 25px rgba(0, 242, 254, 0.25) !important;
        overflow: visible !important;
    }}
    #official-report-container table {{
        page-break-inside: avoid !important;
    }}
}}
</style>
""", unsafe_allow_html=True)
# ==================== المرجع النظامي الدقيق والمصحح للمواد (من 50 إلى 80) ====================
BUILTIN_TRAFFIC_LAW_REFERENCE = """
[المرجع النظامي الأساسي لنظام المرور السعودي ولائحته التنفيذية - النصوص الرسمية المعتمدة]:
1. المادة (50) وتفريعاتها (القيادة والسرعة والأضواء والأولويات للسيارات):
- المادة (50/2/1): يجب على قائد المركبة السيطرة على مركبته وتكييف سرعته وفق الظروف الطبيعية وأحوال الطريق.
- المادة (50/2/2): يجب على قائد المركبة ترك مسافة آمنة كافية بينه وبين المركبة التي أمامه.
- المادة (50/2/4): يجب على قائد المركبة تهدئة السرعة والتأكد من خلو التقاطع قبل دخوله.
- المادة (50/3): قواعد استعمال مصابيح المركبة وأنوار التلاقي والقيادة في الأحوال المختلفة (مثل الضباب والمطر).
- تنبيه هام: المادة (5/50) خاصة حصرياً بتنظيمات سير "الدراجات العادية وما في حكمها" فقط وليست للسيارات.
2. المادة (6/50) وتفريعاتها - قواعد وتنظيمات السير على الطرق وقواعد الأفضلية:
- المادة (1/6/50): قواعد الأفضلية على الطرق.
- المادة (1/1/6/50): قواعد الأفضلية على الطرق والتقاطعات غير المنظمة بواسطة الإشارات المرورية حسب الأولوية الآتية:
  * المادة (1/1/1/6/50): الأفضلية لسائق المركبة المتقدم على غيره، وعليه مراقبة حركة المرور من حيث تأثرها بأي تغيير في المسافة أو الاتجاه عند تخفيف سرعته أو تبديل اتجاهه.
  * المادة (1/1/2/6/50): الأفضلية لسائق المركبة التي تسير باتجاه مستقيم في حال سير المركبتين متحاذيتين وعلى من يرغب تغيير اتجاهه أن يعطي الأفضلية للمركبة التي تسير باتجاه مستقيم.
  * المادة (1/1/3/6/50): الأفضلية للمركبة التي تسير باتجاه مستقيم في حال الدخول أو الخروج من طريق الخدمة أو العكس.
3. المادة الحادية والستون (51) - علامات الطريق والعاكسات والشاخسات:
- المادة (51/1): على السائق التقيد بعلامات الطريق والعاكسات والشاخسات الملحة بهذا النظام والتعليمات الصادرة من الجهات المختصة.
- المادة (51/6/2): علامات الأولوية: تبين لمستعملي الطريق القواعد الخاصة ببعض الأولويات في التقاطعات والأجزاء الضيقة من الطريق.
- المادة (51/6/3): علامات المنع والتنفيذ: تستعمل لمنع مستعملي الطريق من القيام بأعمال معينة أو إلزامهم بها.
4. المادة الثانية والستون (52) والمادة الثالثة والستون (53):
- المادة (52): حظر إتلاف علامات الطريق والعاكسات والشاخسات أو العبث بها أو نقلها.
- المادة (53): جهة السير على الطرق (جهة السير على الطرق هي الجهة اليمنى).
5. المادة الرابعة والستون (54) والمادة الخامسة والستون (55):
- المادة (54): أفضلية المرور لمركبات الطوارئ أثناء مباشرة مهماتها الرسمية.
- المادة (55): تنظيم سير المشاة وقواعد عبور الطرق وممرات المشاة والإشارات الضوئية الخاصة بهم.
6. المادة (60)، (61)، (62) - المسؤولية والتحقيق:
- المادة (60): تعريف الحادث وتقسيم نسب المسؤولية وفق النسب القياسية المعتمدة (100%، 75%، 50%، 25%، 0%) بحيث يكون مجموع نسب الأطراف 100% دائماً.
- المادة (61) و (62): تختص الإدارة المختصة (المرور) بمعاينة الموقع، رفع الآثار، وتحديد نسب الإدانة بدقة وفق الأنظمة.
"""
@st.cache_data(show_spinner=False)
def load_traffic_law_pages(start_page=50, end_page=80):
    pdf_path = None
    for f in os.listdir("."):
        if f.lower().endswith(".pdf"):
            pdf_path = f
            break
    extracted_text = ""
    if pdf_path and os.path.exists(pdf_path):
        try:
            if fitz is not None:
                doc = fitz.open(pdf_path)
                s_idx = max(0, start_page - 1)
                e_idx = min(len(doc), end_page)
                extracted_text = "\n".join([doc[i].get_text("text") for i in range(s_idx, e_idx)])
            elif PdfReader is not None:
                reader = PdfReader(pdf_path)
                s_idx = max(0, start_page - 1)
                e_idx = min(len(reader.pages), end_page)
                extracted_text = "\n".join([reader.pages[i].extract_text() or "" for i in range(s_idx, e_idx)])
        except Exception:
            extracted_text = ""
    if len(extracted_text) > 14000:
        extracted_text = extracted_text[:14000]
    return BUILTIN_TRAFFIC_LAW_REFERENCE + "\n\n" + extracted_text
law_reference_text = load_traffic_law_pages(50, 80)
def clean_ai_output(text: str) -> str:
    text = re.sub(r"\(صفحات\s*50\s*-\s*80\)", "", text)
    text = re.sub(r"\(الصفحات\s*50\s*-\s*80\)", "", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    return text.strip()
rc = st.session_state.reset_counter
# ==================== الواجهة الهولوغرامية الإبداعية ====================
st.markdown('<div class="no-print">', unsafe_allow_html=True)
st.markdown(f"""
<div class="vision-hero-card">
    <div class="vision-right">
        <div class="top-mini-badge">⚡ منظومة الذكاء الاصطناعي السيادي</div>
        <div class="vision-2030-title">VISION <span>2030</span></div>
        <h1 class="hasm-main-title">حسم الذكي للحوادث المرورية</h1>
        <p class="hasm-subtitle">منصة التحليل الهندسي والاستدلال النظامي الذكي وفق نظام المرور السعودي</p>
    </div>
    <div class="holo-orb-wrapper">
        <div class="holo-orb-ring-outer"></div>
        <div class="holo-orb-ring-inner"></div>
        {center_hologram_content}
    </div>
</div>
<div class="holo-status-pill">
    <div><span class="dot"></span><strong>حالة النظام:</strong> مرتبط بنظام المرور السعودي ولائحته التنفيذية</div>
    <div style="color:#00f2fe; font-weight:800;">AI ENGINE ACTIVE</div>
</div>
""", unsafe_allow_html=True)
# 1. بيانات المحضر (فارغة تماماً)
st.markdown("""
<div class="neon-section-card">
    <div class="neon-card-header">
        <div class="neon-card-title">🛡️ بيانات المحضر وظروف الموقع الميدانية</div>
        <span class="neon-badge">بيانات المباشرة</span>
    </div>
""", unsafe_allow_html=True)
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    inv_name = st.text_input("اسم المحقق", value="", placeholder="أدخل اسم المحقق...", key=f"inv_name_{rc}")
    inv_id = st.text_input("رتبة المحقق", value="", placeholder="مثال: رقيب / ملازم أول...", key=f"inv_id_{rc}")
with m_col2:
    report_no = st.text_input("رقم البلاغ / المحضر", value="", placeholder="أدخل رقم البلاغ...", key=f"report_no_{rc}")
    city = st.text_input("المدينة / الموقع", value="", placeholder="مثال: جازان - العارضة", key=f"city_{rc}")
with m_col3:
    site_type = st.selectbox(
        "نوع الموقع",
        [
            "تقاطع رباعي غير منظم",
            "تقاطع رباعي منظم بإشارات",
            "تقاطع حرف T (فرعي مع رئيسي)",
            "طريق رئيسي مستقيم",
            "طريق فرعي / داخلي",
            "دوار",
            "فتحة دوران (U-Turn)",
            "منحنى / منعطف",
            "مدخل أو مخرج خدمة / محطة / موقف"
        ],
        key=f"site_type_{rc}"
    )
    weather = st.selectbox("حالة الطقس", ["صحو", "ممطر", "غبار / ضباب", "رياح شديدة"], key=f"weather_{rc}")
with m_col4:
    road_cond = st.selectbox("حالة الطريق", ["جاف", "مبتل / زلق", "أعمال طريق", "غير معبد"], key=f"road_cond_{rc}")
    lighting = st.selectbox("الإنارة", ["نهار", "ليل - إنارة جيدة", "ليل - بدون إنارة"], key=f"lighting_{rc}")
s_col1, s_col2, s_col3 = st.columns(3)
with s_col1:
    injuries = st.selectbox("الإصابات", ["لا توجد", "إصابات بسيطة", "إصابات متوسطة / بليغة", "وفيات"], key=f"injuries_{rc}")
with s_col2:
    damages = st.selectbox("الأضرار المادية", ["بسيطة", "متوسطة", "تلف كبير"], key=f"damages_{rc}")
with s_col3:
    strict_mode = st.selectbox("مستوى الصرامة النظامية", ["صارم نظامي (100% / 75% / 50% / 25% / 0%)", "قياسي استدلالي"], key=f"strict_mode_{rc}")
st.markdown("</div>", unsafe_allow_html=True)
# 2. أطراف الحادث والمناورات الـ 21
st.markdown("""
<div class="neon-section-card">
    <div class="neon-card-header">
        <div class="neon-card-title">🚗 أطراف الحادث وخيارات المناورة الميدانية</div>
        <span class="neon-badge">تحليل المركبات</span>
    </div>
""", unsafe_allow_html=True)
num_parties = st.radio("عدد المركبات / الأطراف المشتركة في الحادث:", [2, 3, 4], horizontal=True, key=f"num_parties_{rc}")
MANEUVER_OPTIONS = [
    "سير مستقيم",
    "متوقف (وقوف نظامي / عند إشارة)",
    "متوقف (وقوف خاطئ / معطل بدون تحذير)",
    "توقف مفاجئ غير مبرر",
    "دخول من طريق فرعي إلى رئيسي",
    "دخول تقاطع غير منظم",
    "دخول دوار",
    "سير داخل الدوار",
    "خروج من الدوار",
    "انعطاف يمين",
    "انعطاف يسار",
    "دوران للخلف (U-Turn)",
    "تغيير مسار (انحراف مفاجئ)",
    "تجاوز (نظامياً / من اليسار)",
    "تجاوز خاطئ (من اليمين / كتف الطريق / في منحنى)",
    "رجوع للخلف (ريوس)",
    "خروج من موقف / عقار خاص / محطة",
    "سير عكس الاتجاه",
    "فتح باب المركبة أثناء السير أو الوقوف",
    "سقوط حمولة غير مثبتة",
    "اندفاع قسري (نتيجة صدم خلفي)"
]
parties_data = []
p_cols = st.columns(2)
for i in range(num_parties):
    with p_cols[i % 2]:
        st.markdown(f"<h4 style='color:#00f2fe; margin-bottom:8px;'>🔹 بيانات الطرف ({i+1})</h4>", unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            p_role = st.selectbox(f"صفة الطرف {i+1}", ["سائق", "مشاة", "مالك مركبة متوقفة"], key=f"p_role_{i}_{rc}")
            p_veh = st.text_input(f"نوع المركبة {i+1}", placeholder="مثال: كامري / صالون", key=f"p_veh_{i}_{rc}")
            p_plate = st.text_input(f"رقم اللوحة {i+1}", placeholder="ح س ص 4444", key=f"p_plate_{i}_{rc}")
            p_dir = st.selectbox(f"الاتجاه {i+1}", ["شمال", "جنوب", "شرق", "غرب", "شمال شرقي", "شمال غربي", "جنوب شرقي", "جنوب غربي"], key=f"p_dir_{i}_{rc}")
        with r2:
            p_lane = st.selectbox(f"المسار {i+1}", ["أيمن", "أوسط", "أيسر", "مسار خدمة", "كتف الطريق", "داخل التقاطع"], key=f"p_lane_{i}_{rc}")
            p_man = st.selectbox(f"المناورة {i+1}", MANEUVER_OPTIONS, key=f"p_man_{i}_{rc}")
            p_sig = st.selectbox(f"الإشارة {i+1}", ["لا توجد إشارة", "إشارة خضراء", "إشارة حمراء", "إشارة صفراء متقطعة", "لوحة قف (STOP)", "لوحة أعطِ الأولوية"], key=f"p_sig_{i}_{rc}")
            p_prio = st.selectbox(f"الأولوية {i+1}", ["له أولوية", "عليه أولوية للغير (يجب التوقف/التهدئة)", "متكافئ / غير محدد"], index=0 if i == 0 else 1, key=f"p_prio_{i}_{rc}")
        p_spd = st.selectbox(f"السرعة التقديرية للطرف {i+1}", ["ضمن الحد النظامي", "زائدة عن الحد النظامي", "سرعة عالية جداً (تهور)", "متوقف تماماً"], key=f"p_spd_{i}_{rc}")
        parties_data.append({
            "طرف": f"الطرف {i+1}",
            "الصفة": p_role,
            "المركبة": p_veh if p_veh.strip() else f"مركبة {i+1}",
            "اللوحة": p_plate if p_plate.strip() else "غير محدد",
            "الاتجاه": p_dir,
            "المسار": p_lane,
            "المناورة": p_man,
            "الإشارة": p_sig,
            "الأولوية": p_prio,
            "السرعة": p_spd
        })
st.markdown("</div>", unsafe_allow_html=True)
# 3. التحليل الهندسي والسرد الحر
st.markdown("""
<div class="neon-section-card">
    <div class="neon-card-header">
        <div class="neon-card-title">📐 التحليل الهندسي الميداني والسرد الحر للواقعة</div>
        <span class="neon-badge">الابتكار التقني</span>
    </div>
""", unsafe_allow_html=True)
sk_col1, sk_col2 = st.columns(2)
with sk_col1:
    sketch_notes = st.text_area(
        "ملاحظات الكروكي / الرسم الميداني:",
        placeholder="مثال: نقطة الاصطدام في منتصف الدوار، مقدمة المركبة الأولى في جانب الثانية...",
        height=95,
        key=f"sketch_notes_{rc}"
    )
with sk_col2:
    witness_notes = st.text_area(
        "إفادات الشهود / الكاميرات وملاحظات المحقق:",
        placeholder="أقوال الشهود أو ملاحظات المباشر الميداني...",
        height=95,
        key=f"witness_notes_{rc}"
    )
narrative = st.text_area(
    "السرد الحر لتفاصيل الحادث:",
    placeholder="اكتب تفاصيل الحادث هنا...",
    height=130,
    key=f"narrative_{rc}"
)
btn_c1, btn_c2 = st.columns(2)
with btn_c1:
    analyze_clicked = st.button("⚡ بدء التحليل النظامي الفوري", use_container_width=True)
with btn_c2:
    st.button("🗑️ مسح البيانات / حادث جديد", on_click=reset_all_fields, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("""
<div class="holo-bottom-dock">
    <span class="active">● الاستدلال النظامي</span>
    <span>◎ الهندسة المرورية</span>
    <span>◈ مواد اللائحة التنفيذية</span>
    <span>❖ التقارير الرسمية</span>
</div>
</div>
""", unsafe_allow_html=True)
# ==================== محرك التحليل الذكي (Groq AI) ====================
if analyze_clicked:
    st.session_state.analysis_result = None
    if not narrative.strip():
        st.warning("⚠️ يرجى كتابة تفاصيل الحادث في خانة (السرد الحر) قبل بدء التحليل.")
    else:
        api_key = st.secrets.get("GROQ_API_KEY", None) or os.environ.get("GROQ_API_KEY", None)
        if not api_key:
            st.error("❌ لم يتم العثور على مفتاح `GROQ_API_KEY` في إعدادات Secrets.")
        elif Groq is None:
            st.error("❌ مكتبة `groq` غير مثبتة.")
        else:
            with st.spinner("⚡ جاري تشغيل محرك الاستدلال النظامي بدقة مطابقة للائحة الرسمية..."):
                parties_summary = "\n".join([
                    f"- {p['طرف']}: الصفة ({p['الصفة']})، المركبة ({p['المركبة']})، اللوحة ({p['اللوحة']})، الاتجاه ({p['الاتجاه']})، المسار ({p['المسار']})، المناورة ({p['المناورة']})، الإشارة ({p['الإشارة']})، الأولوية ({p['الأولوية']})، السرعة ({p['السرعة']})."
                    for p in parties_data
                ])
                system_prompt = f"""
أنت خبير هندسة مرورية ومحقق نظامي معتمد في الإدارة العامة للمرور بالمملكة العربية السعودية.
مهمتك تحليل الحادث المروري وتحديد نسب المسؤولية بدقة هندسية وقانونية صارمة، مع **الالتزام الحرفي بالمواد النظامية الصحيحة** وعدم الخلط أبداً (مثل عدم استخدام مواد الدراجات 5/50 على السيارات، واستخدام تفريعات المادة 6/50 للأفضلية، والمادة 50/2/4 للتهدئة وخلو التقاطع، والمادة 51 لعلامات الطريق، والمادة 53 لجهة السير).
[القواعد الهندسية والنظامية الملزمة]:
1. إصدار حكم فاصل بنسب معتمدة حصرياً: (100%، 75%، 50%، 25%، 0%) بحيث يكون مجموع نسب الأطراف = 100% دائماً.
2. قاعدة الهندسة المرورية ونقطة الاصطدام: اصطدام مقدمة مركبة بجانب مركبة أخرى داخل تقاطع أو دوار دليل مادي قاطع على أن المصدومة في جانبها دخلت أولاً. وفي الدوائر والأولوية تُطبق المادة (1/1/6/50) وتفريعاتها والمادة (50/2/4).
3. يُمنع منعاً باتاً اقتطاع النص أو توقف التقرير في المنتصف؛ استمر في التوليد حتى يكتمل الجدول والخلاصة.
4. ابدأ فوراً بالأقسام الأربعة التالية دون تكرار بيانات المحضر:
   ### السرد الحر وتحليل الوقائع
   ### التكييف النظامي والمواد المستند إليها
   ### جدول المخطئ ونسب المسؤولية المعتمدة
   (جدول Markdown رسمي بالأعمدة: | الطرف | المركبة | نسبة المسؤولية % | سبب الإدانة / الإعفاء | السند النظامي الدقيق |)
   ### الخلاصة النظامية
[النصوص النظامية المرجعية المعتمدة]:
{law_reference_text}
"""
                user_prompt = f"""
بيانات الموقع: {site_type} | الطقس: {weather} | الطريق: {road_cond} | الإنارة: {lighting}
الأطراف:
{parties_summary}
السرد الحر:
{narrative}
{"ملاحظات الكروكي: " + sketch_notes if sketch_notes.strip() else ""}
{"إفادات الشهود والملاحظات: " + witness_notes if witness_notes.strip() else ""}
"""
                try:
                    client = Groq(api_key=api_key)
                    available_models = []
                    try:
                        models_resp = client.models.list()
                        for m in models_resp.data:
                            m_id = m.id
                            if not any(skip in m_id.lower() for skip in ["whisper", "guard", "tts", "vision", "embed", "playai", "allam"]):
                                available_models.append(m_id)
                    except Exception:
                        pass
                    preferred_order = [
                        "llama-3.3-70b-versatile",
                        "openai/gpt-oss-120b",
                        "deepseek-r1-distill-llama-70b",
                        "gemma2-9b-it"
                    ]
                    models_to_try = [m for m in preferred_order if m in available_models]
                    for m in available_models:
                        if m not in models_to_try:
                            models_to_try.append(m)
                    if not models_to_try:
                        models_to_try = preferred_order
                    response_text = None
                    last_err = None
                    for m_name in models_to_try:
                        try:
                            completion = client.chat.completions.create(
                                model=m_name,
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": user_prompt}
                                ],
                                temperature=0.1,
                                max_tokens=3200
                            )
                            response_text = completion.choices[0].message.content
                            if response_text:
                                response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()
                                break
                        except Exception as e_mod:
                            last_err = e_mod
                            continue
                    if response_text:
                        st.session_state.analysis_result = clean_ai_output(response_text)
                        st.session_state.report_meta = {
                            "report_no": report_no if report_no.strip() else "غير محدد",
                            "inv_name": inv_name if inv_name.strip() else "غير محدد",
                            "inv_id": inv_id if inv_id.strip() else "غير محدد",
                            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "location": city if city.strip() else "غير محدد",
                            "site_type": site_type,
                            "env": f"الطقس: {weather} | الطريق: {road_cond} | الإنارة: {lighting}",
                            "inj_dmg": f"الإصابات: {injuries} | الأضرار: {damages}",
                            "strict_mode": strict_mode,
                            "parties": parties_data
                        }
                    else:
                        st.error(f"⚠️ تعذر إتمام التحليل حالياً: {last_err}")
                except Exception as e:
                    st.error(f"⚠️ حدث خطأ أثناء الاتصال بمحرك التحليل: {e}")
# ==================== عرض التقرير الرسمي والطباعة ====================
if st.session_state.analysis_result:
    meta = st.session_state.report_meta
    parties_rows_html = ""
    for p in meta.get("parties", []):
        parties_rows_html += f"""
        <tr>
            <td style="width:18%; font-weight:800;">{p['طرف']} ({p['المركبة']})</td>
            <td>الصفة: {p['الصفة']} | اللوحة: {p['اللوحة']} | الاتجاه: {p['الاتجاه']} | المسار: {p['المسار']} | المناورة: {p['المناورة']} | الإشارة: {p['الإشارة']} | الأولوية: {p['الأولوية']} | السرعة: {p['السرعة']}</td>
        </tr>
        """
    header_logo_print = f'<img src="data:image/png;base64,{logo_b64}" style="width:65px;height:65px;object-fit:contain;">' if logo_b64 else ""
    st.markdown(f"""
    <div id="official-report-container">
        <div class="report-holo-header">
            <div>
                <div style="background:rgba(0,242,254,0.18); border:1px solid #00f2fe; color:#e0f2fe; padding:3px 12px; border-radius:999px; font-size:0.78rem; font-weight:800; display:inline-block; margin-bottom:6px;">
                    ⚡ منظومة الاستدلال النظامي الذكي
                </div>
                <div class="report-vision-tag">VISION <span>2030</span></div>
                <h2 style="margin:0 !important; padding:0 !important; border:none !important; background:transparent !important; color:#ffffff !important; font-size:1.55rem !important;">
                    حسم الذكي للحوادث المرورية
                </h2>
                <p style="margin:2px 0 0 0 !important; color:#7dd3fc !important; font-weight:700; font-size:0.92rem !important;">
                    وثيقة رسمية لتحليل المسؤولية المرورية وفق نظام المرور السعودي ولائحته التنفيذية
                </p>
            </div>
            <div class="holo-orb-wrapper" style="width:105px; height:105px;">
                <div class="holo-orb-ring-outer"></div>
                <div class="holo-orb-ring-inner"></div>
                {center_hologram_content}
            </div>
        </div>
        <h3>🛡️ بيانات المحضر وأطراف الحادث</h3>
        <table>
            <thead>
                <tr>
                    <th style="width:22%;">البند</th>
                    <th>البيان والتفاصيل الميدانية</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>رقم المحضر</td><td>{meta.get('report_no')}</td></tr>
                <tr><td>المحقق المباشر</td><td>{meta.get('inv_name')} | الرتبة: {meta.get('inv_id')}</td></tr>
                <tr><td>التاريخ والوقت</td><td>{meta.get('datetime')}</td></tr>
                <tr><td>الموقع ونوعه</td><td>{meta.get('location')} ({meta.get('site_type')})</td></tr>
                <tr><td>ظروف الموقع والإصابات</td><td>{meta.get('env')} | {meta.get('inj_dmg')}</td></tr>
                {parties_rows_html}
            </tbody>
        </table>
    """, unsafe_allow_html=True)
    st.markdown(st.session_state.analysis_result)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="no-print" style="margin-top: 18px;">', unsafe_allow_html=True)
    act_col1, act_col2 = st.columns(2)
    with act_col1:
        if st.button("🖨️ طباعة التقرير الرسمي (PDF)", use_container_width=True):
            components.html("<script>window.parent.print();</script>", height=0)
    with act_col2:
        full_txt_report = f"""حسم الذكي للحوادث المرورية - تقرير نظامي رسمي
=================================================
رقم المحضر: {meta.get('report_no')}
المحقق: {meta.get('inv_name')} (رتبة: {meta.get('inv_id')})
التاريخ والوقت: {meta.get('datetime')}
الموقع: {meta.get('location')} - {meta.get('site_type')}
=================================================
{st.session_state.analysis_result}
"""
        st.download_button(
            label="💾 حفظ وتحميل التقرير",
            data=full_txt_report.encode("utf-8"),
            file_name=f"Hasm_Report_{meta.get('report_no')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
