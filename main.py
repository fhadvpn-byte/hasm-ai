import html
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
header,
[data-testid="stHeader"],
[data-testid="stHeaderActionElements"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stMainMenu"],
#MainMenu,
.stAppDeployButton,
.stDeployButton,
footer,
[data-testid="stFooter"] {{
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: hidden !important;
    pointer-events: none !important;
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
.holo-mark {{
    width: 13px;
    height: 13px;
    flex: 0 0 13px;
    display: inline-block;
    border-radius: 3px;
    border: 2px solid #00f2fe;
    background: rgba(0, 242, 254, 0.35);
    box-shadow: 0 0 10px #00f2fe, inset 0 0 6px #00f2fe;
    transform: rotate(45deg);
}}
.holo-vehicle {{
    width: 26px;
    height: 26px;
    flex: 0 0 26px;
    display: block;
    overflow: visible;
    filter: drop-shadow(0 0 6px #00f2fe);
}}
.party-heading {{
    display: flex;
    align-items: center;
    gap: 10px;
    color: #00f2fe !important;
    font-weight: 800;
    margin-bottom: 8px;
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
    text-align: right !important;
    unicode-bidi: embed !important;
    position: relative !important;
    overflow: visible !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}}
.report-section-card {{
    background: linear-gradient(180deg, rgba(8, 42, 92, 0.94) 0%, rgba(3, 18, 46, 0.96) 100%) !important;
    border: 2px solid #00f2fe !important;
    border-radius: 18px !important;
    padding: 16px 18px 12px 18px !important;
    margin: 16px 0 0 0 !important;
    box-shadow: 0 0 22px rgba(0, 242, 254, 0.28), inset 0 0 16px rgba(0, 242, 254, 0.12) !important;
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: embed !important;
    page-break-inside: avoid !important;
}}
.holo-section-title {{
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.28) 0%, rgba(4, 25, 56, 0.12) 100%) !important;
    color: #00f2fe !important;
    font-weight: 900 !important;
    font-size: 1.08rem !important;
    border-right: 4px solid #00f2fe !important;
    border-bottom: 1px solid rgba(0, 242, 254, 0.45) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    margin: 0 0 12px 0 !important;
    text-shadow: 0 0 10px rgba(0, 242, 254, 0.55) !important;
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: embed !important;
}}
.report-section-body,
.report-section-body p,
.report-section-body li,
.report-section-body ul,
.report-section-body ol,
#official-report-container table,
#official-report-container th,
#official-report-container td {{
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: embed !important;
}}
.report-section-body ul,
.report-section-body ol {{
    margin: 8px 1.4rem 8px 0 !important;
    padding: 0 !important;
}}
[data-testid="stHtml"]:has(#official-report-container),
[data-testid="stMarkdown"]:has(#official-report-container) {{
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: embed !important;
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
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
}}
#official-report-container p,
#official-report-container li,
#official-report-container div {{
    color: #e0f2fe !important;
    line-height: 1.8 !important;
    font-size: 0.98rem !important;
    direction: rtl !important;
    text-align: right !important;
    unicode-bidi: embed !important;
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
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: embed !important;
    }}
    #official-report-container table,
    .report-section-card {{
        page-break-inside: avoid !important;
    }}
}}
</style>
""", unsafe_allow_html=True)
# ==================== المرجع النظامي الدقيق والمصحح للمواد (من 50 إلى 80) ====================
# موسوعة قانونية مصغرة مركزة (لمنع خطأ 413) مع الحفاظ على النصوص الدقيقة دون حشو
BUILTIN_TRAFFIC_LAW_REFERENCE = """
[موسوعة نظام المرور السعودي - نصوص معتمدة مركزة]
أ) المادة (50) القيادة والسرعة والأضواء (للسيارات):
- (50/2/1): السيطرة على المركبة وتكييف السرعة وفق الظروف وأحوال الطريق.
- (50/2/2): ترك مسافة آمنة كافية خلف المركبة الأمامية.
- (50/2/4): تهدئة السرعة والتأكد من خلو التقاطع/الدوار قبل الدخول.
- (50/3): استعمال المصابيح وأنوار التلاقي (ضباب/مطر/ليل).
- تحذير: (5/50) للدراجات العادية وما في حكمها فقط؛ يُحظر تطبيقها على السيارات.
ب) المادة (6/50) قواعد الأفضلية في الطرق والتقاطعات غير المنظمة:
- (1/6/50): الإطار العام لقواعد الأفضلية.
- (1/1/6/50): الأفضلية في التقاطعات غير المنظمة بالإشارات وفق الآتي:
  * (1/1/1/6/50): الأفضلية للمتقدم داخل منطقة السير/التقاطع/الدوار؛ وعليه مراقبة أثر تغيير سرعته أو اتجاهه.
  * (1/1/2/6/50): الأفضلية للمسار المستقيم عند التحادي؛ وعلى مغيّر الاتجاه إعطاء الأفضلية.
  * (1/1/3/6/50): الأفضلية للمستقيم عند الدخول/الخروج من طريق الخدمة أو العكس.
- ربط هندسي ملزم: المركبة داخل الدوار متقدمة فتُحمى بـ (1/1/1/6/50)؛ والداخل للدوار بلا تهدئة/تأكد يخالف (50/2/4).
ج) المواد (51)-(55):
- (51/1): التقيد بعلامات الطريق والعاكسات والشاخسات والتعليمات.
- (51/6/2): علامات الأولوية في التقاطعات والأجزاء الضيقة.
- (51/6/3): علامات المنع والتنفيذ.
- (51/6/4): علامات الإرشاد والإعلام والتوجيه.
- (52): حظر إتلاف/العبث بعلامات الطريق أو نقلها.
- (53): جهة السير يمنى.
- (54): أفضلية مركبات الطوارئ أثناء المهمة الرسمية دون إعفاء من واجب السلامة.
- (55): تنظيم سير المشاة وعبور الطرق وممراتهم وإشاراتهم.
د) المواد (60)-(62) المسؤولية والتحقيق:
- (60): تعريف الحادث؛ نسب المسؤولية القياسية فقط: 100% / 75% / 50% / 25% / 0% ومجموعها 100%.
- (61)/(62): اختصاص المرور بالمعاينة ورفع الآثار وتحديد نسب الإدانة.
"""
PDF_EXTRACT_CHAR_LIMIT = 3500
TOTAL_LAW_CONTEXT_CHAR_LIMIT = 6500

@st.cache_data(show_spinner=False)
def load_traffic_law_pages(start_page=50, end_page=80):
    """يستخرج مقطعاً مركزاً من PDF بحد آمن لمنع تجاوز Limit 8000 / خطأ 413."""
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
                doc.close()
            elif PdfReader is not None:
                reader = PdfReader(pdf_path)
                s_idx = max(0, start_page - 1)
                e_idx = min(len(reader.pages), end_page)
                extracted_text = "\n".join([reader.pages[i].extract_text() or "" for i in range(s_idx, e_idx)])
        except Exception:
            extracted_text = ""
    # ضغط الفراغات ثم قطع آمن بحد 3500 حرف للمرفق
    extracted_text = re.sub(r"[ \t]+", " ", extracted_text)
    extracted_text = re.sub(r"\n{3,}", "\n\n", extracted_text).strip()
    if len(extracted_text) > PDF_EXTRACT_CHAR_LIMIT:
        extracted_text = extracted_text[:PDF_EXTRACT_CHAR_LIMIT].rsplit(" ", 1)[0] + "…"
    if extracted_text:
        law_bundle = (
            BUILTIN_TRAFFIC_LAW_REFERENCE.strip()
            + "\n\n[مقتطف مركّز من اللائحة PDF ص"
            + f"{start_page}-{end_page}]\n"
            + extracted_text
        )
    else:
        law_bundle = BUILTIN_TRAFFIC_LAW_REFERENCE.strip()
    if len(law_bundle) > TOTAL_LAW_CONTEXT_CHAR_LIMIT:
        law_bundle = law_bundle[:TOTAL_LAW_CONTEXT_CHAR_LIMIT].rsplit(" ", 1)[0] + "…"
    return law_bundle

law_reference_text = load_traffic_law_pages(50, 80)
def clean_ai_output(text: str) -> str:
    text = re.sub(r"\(صفحات\s*50\s*-\s*80\)", "", text)
    text = re.sub(r"\(الصفحات\s*50\s*-\s*80\)", "", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return text.strip()


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


_KNOWN_SECTION_MARKERS = (
    "السرد الحر",
    "التكييف النظامي",
    "جدول المخطئ",
    "الخلاصة النظامية",
)


def _strip_hashes(value: str) -> str:
    return value.replace("#", "").replace("＃", "")


def _heading_title(line: str):
    stripped = line.strip()
    if not stripped:
        return None
    hashed = re.match(r"^#{1,6}\s*(.+)$", stripped)
    if hashed:
        title = _strip_hashes(re.sub(r"[*_`]+", "", hashed.group(1))).strip(" :-–—")
        return title or None
    plain = _strip_hashes(re.sub(r"[*_`]+", "", stripped)).strip(" :-–—")
    if len(plain) <= 80 and any(plain.startswith(marker) for marker in _KNOWN_SECTION_MARKERS):
        return plain
    return None


def split_report_sections(text: str):
    lines = text.replace("\r\n", "\n").split("\n")
    sections = []
    current_title = None
    current_lines = []
    for line in lines:
        title = _heading_title(line)
        if title:
            if current_title is None and any(part.strip() for part in current_lines):
                sections.append(("التحليل النظامي", "\n".join(current_lines).strip()))
            elif current_title is not None:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = title
            current_lines = []
            continue
        current_lines.append(line)
    if current_title is None:
        body = "\n".join(current_lines).strip()
        return [("التحليل النظامي", body)] if body else []
    sections.append((current_title, "\n".join(current_lines).strip()))
    return sections


def _inline_format(value: str) -> str:
    safe = _strip_hashes(esc(value))
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"__(.+?)__", r"<strong>\1</strong>", safe)
    return safe


def _is_table_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2


def _is_separator_row(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _is_list_item(line: str) -> bool:
    return re.match(r"^(?:[-*•]|\d+[\.\)])\s+\S", line.strip()) is not None


def markdown_body_to_html(body: str) -> str:
    lines = body.replace("\r\n", "\n").split("\n")
    parts = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped or stripped.startswith("```"):
            index += 1
            continue
        if _is_table_row(stripped):
            rows = []
            while index < len(lines) and _is_table_row(lines[index].strip()):
                row = lines[index].strip()
                if not _is_separator_row(row):
                    cells = [cell.strip() for cell in row.strip("|").split("|")]
                    rows.append(cells)
                index += 1
            if rows:
                header = "".join(f"<th>{_inline_format(cell)}</th>" for cell in rows[0])
                body_rows = []
                for row in rows[1:]:
                    cells = "".join(f"<td>{_inline_format(cell)}</td>" for cell in row)
                    body_rows.append(f"<tr>{cells}</tr>")
                parts.append(
                    "<table dir=\"rtl\">"
                    f"<thead><tr>{header}</tr></thead>"
                    f"<tbody>{''.join(body_rows)}</tbody>"
                    "</table>"
                )
            continue
        if _is_list_item(stripped):
            items = []
            ordered = re.match(r"^\d+[\.\)]\s+", stripped) is not None
            while index < len(lines) and _is_list_item(lines[index].strip()):
                item = re.sub(r"^(?:[-*•]|\d+[\.\)])\s+", "", lines[index].strip())
                items.append(f"<li>{_inline_format(item)}</li>")
                index += 1
            tag = "ol" if ordered else "ul"
            parts.append(f"<{tag} dir=\"rtl\">{''.join(items)}</{tag}>")
            continue
        paragraph = [stripped]
        index += 1
        while index < len(lines):
            nxt = lines[index].strip()
            if not nxt or nxt.startswith("```") or _is_table_row(nxt) or _is_list_item(nxt) or _heading_title(nxt):
                break
            paragraph.append(nxt)
            index += 1
        parts.append(f"<p dir=\"rtl\">{_inline_format(' '.join(paragraph))}</p>")
    return "".join(parts) or "<p dir=\"rtl\">—</p>"


def render_analysis_cards(text: str) -> str:
    sections = split_report_sections(text or "")
    if not sections:
        return ""
    cards = []
    for title, body in sections:
        cards.append(
            "<section class=\"report-section-card\" dir=\"rtl\">"
            f"<h3 class=\"holo-section-title\" dir=\"rtl\">{_inline_format(title)}</h3>"
            f"<div class=\"report-section-body\" dir=\"rtl\">{markdown_body_to_html(body)}</div>"
            "</section>"
        )
    return "".join(cards)


def plain_analysis_text(text: str) -> str:
    lines = []
    for line in (text or "").replace("\r\n", "\n").split("\n"):
        if re.match(r"^#{1,6}\s*", line.strip()):
            line = re.sub(r"^#{1,6}\s*", "", line.strip())
        lines.append(_strip_hashes(line))
    return "\n".join(lines).strip()
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
        <div class="neon-card-title"><span class="holo-mark" aria-hidden="true"></span>بيانات المحضر وظروف الموقع الميدانية</div>
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
        <div class="neon-card-title"><svg class="holo-vehicle" viewBox="0 0 32 32" aria-hidden="true"><path d="M6 21h20" fill="none" stroke="#00f2fe" stroke-width="1.8" stroke-linecap="round"/><path d="M8.2 21l2.1-6.1c.3-.8 1.1-1.4 1.9-1.4h7.4c.8 0 1.5.4 1.8 1.1L23.6 21" fill="rgba(0,242,254,0.16)" stroke="#00f2fe" stroke-width="1.8" stroke-linejoin="round"/><path d="M13 13.5h5.2" fill="none" stroke="#00f2fe" stroke-width="1.4" stroke-linecap="round"/><circle cx="11" cy="21.2" r="2.15" fill="rgba(0,242,254,0.28)" stroke="#00f2fe" stroke-width="1.6"/><circle cx="21.2" cy="21.2" r="2.15" fill="rgba(0,242,254,0.28)" stroke="#00f2fe" stroke-width="1.6"/></svg>أطراف الحادث وخيارات المناورة الميدانية</div>
        <span class="neon-badge">تحليل المركبات</span>
    </div>
""", unsafe_allow_html=True)
num_parties = int(
    st.number_input(
        "عدد المركبات / الأطراف المشتركة في الحادث",
        min_value=2,
        max_value=15,
        value=2,
        step=1,
        key=f"party_count_{rc}",
    )
)
num_parties = max(2, min(15, num_parties))
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
primary_count = min(num_parties, 4)
p_cols = st.columns(2)
for i in range(primary_count):
    with p_cols[i % 2]:
        st.markdown(
            f"<h4 class='party-heading'><span class='holo-mark' aria-hidden='true'></span>بيانات الطرف ({i+1})</h4>",
            unsafe_allow_html=True,
        )
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
if num_parties > 4:
    for row_start in range(4, num_parties, 2):
        extra_cols = st.columns(2)
        for offset in range(2):
            i = row_start + offset
            if i >= num_parties:
                continue
            with extra_cols[offset]:
                with st.expander(f"مركبة إضافية — الطرف {i + 1}", expanded=False):
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
                        p_prio = st.selectbox(f"الأولوية {i+1}", ["له أولوية", "عليه أولوية للغير (يجب التوقف/التهدئة)", "متكافئ / غير محدد"], index=1, key=f"p_prio_{i}_{rc}")
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
        <div class="neon-card-title"><span class="holo-mark" aria-hidden="true"></span>التحليل الهندسي الميداني والسرد الحر للواقعة</div>
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
                if num_parties > 4:
                    parties_summary = "\n".join([
                        f"- {p['طرف']}: {p['الصفة']}/{p['المركبة']}/{p['اللوحة']} | {p['الاتجاه']}/{p['المسار']} | {p['المناورة']} | {p['الإشارة']} | {p['الأولوية']} | {p['السرعة']}"
                        for p in parties_data
                    ])
                else:
                    parties_summary = "\n".join([
                        f"- {p['طرف']}: الصفة ({p['الصفة']})، المركبة ({p['المركبة']})، اللوحة ({p['اللوحة']})، الاتجاه ({p['الاتجاه']})، المسار ({p['المسار']})، المناورة ({p['المناورة']})، الإشارة ({p['الإشارة']})، الأولوية ({p['الأولوية']})، السرعة ({p['السرعة']})."
                        for p in parties_data
                    ])
                system_prompt = f"""
أنت محقق نظامي وهندسي معتمد لدى الإدارة العامة للمرور. حلّل الواقعة بعمق هندسي وقانوني مطلق، واستخدم فقط أرقام المواد الصحيحة من المرجع المركّز أدناه دون خلط أو اختراع تفريعات.
[إلزام التحليل العميق]:
1. اربط دائماً: نقطة الاصطدام + المناورة + الأولوية النظامية + المادة الدقيقة.
2. قاعدة هندسية قاطعة: مقدمة مركبة (أ) في جانب/أبواب مركبة (ب) داخل تقاطع أو دوار = دليل أن (ب) كانت متقدمة ودخلت أولاً. طبّق (1/1/1/6/50) لحماية المتقدم/داخل الدوار، و(50/2/4) على من دخل دون تهدئة أو دون التأكد من الخلو.
3. الأفضلية غير المنظمة: (1/1/6/50) وتفريعاتها؛ المستقيم عند التحادي (1/1/2/6/50)؛ طريق الخدمة (1/1/3/6/50)؛ علامات الأولوية (51/6/2)؛ جهة السير يمنى (53). ممنوع استخدام (5/50) على السيارات.
4. النسب بحزم حصري فقط: 100% / 75% / 50% / 25% / 0% ومجموعها 100%. لا تتهرب من الحكم. في الخلاصة اذكر النسبة رقماً لكل طرف.
5. أكمل التقرير كاملاً دون انقطاع بهذه الأقسام فقط:
### السرد الحر وتحليل الوقائع
### التكييف النظامي والمواد المستند إليها
### جدول المخطئ ونسب المسؤولية المعتمدة
| الطرف | المركبة | نسبة المسؤولية % | سبب الإدانة / الإعفاء | السند النظامي الدقيق |
### الخلاصة النظامية
[مرجع قانوني مركّز]:
{law_reference_text}
في حوادث التتابع المتعددة، طبّق المادة (50/2/2) لعدم ترك مسافة آمنة، وميّز هندسياً في جدول النسب بين الاصطدام المستقل وبين الدفع القسري من الخلف للمركبة المتوقفة نظامياً (0% إعفاء، وتُحمّل المسؤولية على الدافع).
"""
                # ضغط مدخلات المستخدم أيضاً لتقليل احتمال 413 مع الإبقاء على الوقائع الجوهرية
                narrative_safe = narrative.strip()
                if len(narrative_safe) > 2500:
                    narrative_safe = narrative_safe[:2500] + "…"
                sketch_safe = sketch_notes.strip()
                if len(sketch_safe) > 600:
                    sketch_safe = sketch_safe[:600] + "…"
                witness_safe = witness_notes.strip()
                if len(witness_safe) > 600:
                    witness_safe = witness_safe[:600] + "…"
                user_prompt = f"""
الموقع: {site_type} | الطقس: {weather} | الطريق: {road_cond} | الإنارة: {lighting} | الصرامة: {strict_mode}
الأطراف:
{parties_summary}
السرد:
{narrative_safe}
{"كروكي: " + sketch_safe if sketch_safe else ""}
{"شهود/ملاحظات: " + witness_safe if witness_safe else ""}
حلّل هندسياً وقانونياً بعمق، واربط الاصطدام الجانبي بأولوية الدوار/التقاطع عبر (1/1/1/6/50) و(50/2/4) عند انطباقهما، ثم أصدر النسب القياسية بحزم.
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
                        "deepseek-r1-distill-llama-70b",
                        "gemma2-9b-it",
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
            <td style="width:18%; font-weight:800;">{esc(p.get('طرف'))} ({esc(p.get('المركبة'))})</td>
            <td>الصفة: {esc(p.get('الصفة'))} | اللوحة: {esc(p.get('اللوحة'))} | الاتجاه: {esc(p.get('الاتجاه'))} | المسار: {esc(p.get('المسار'))} | المناورة: {esc(p.get('المناورة'))} | الإشارة: {esc(p.get('الإشارة'))} | الأولوية: {esc(p.get('الأولوية'))} | السرعة: {esc(p.get('السرعة'))}</td>
        </tr>
        """
    analysis_cards = render_analysis_cards(st.session_state.analysis_result)
    st.html(f"""
    <div id="official-report-container" class="rtl-report" dir="rtl">
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
        <h3 class="case-heading"><span class="holo-mark" aria-hidden="true"></span>بيانات المحضر وأطراف الحادث</h3>
        <table>
            <thead>
                <tr>
                    <th style="width:22%;">البند</th>
                    <th>البيان والتفاصيل الميدانية</th>
                </tr>
            </thead>
            <tbody>
                <tr><td>رقم المحضر</td><td>{esc(meta.get('report_no'))}</td></tr>
                <tr><td>المحقق المباشر</td><td>{esc(meta.get('inv_name'))} | الرتبة: {esc(meta.get('inv_id'))}</td></tr>
                <tr><td>التاريخ والوقت</td><td>{esc(meta.get('datetime'))}</td></tr>
                <tr><td>الموقع ونوعه</td><td>{esc(meta.get('location'))} ({esc(meta.get('site_type'))})</td></tr>
                <tr><td>ظروف الموقع والإصابات</td><td>{esc(meta.get('env'))} | {esc(meta.get('inj_dmg'))}</td></tr>
                {parties_rows_html}
            </tbody>
        </table>
        <div class="report-sections" dir="rtl">{analysis_cards}</div>
    </div>
    """)
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
{plain_analysis_text(st.session_state.analysis_result)}
"""
        st.download_button(
            label="💾 حفظ وتحميل التقرير",
            data=full_txt_report.encode("utf-8"),
            file_name=f"Hasm_Report_{meta.get('report_no')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)
