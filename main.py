import base64
import html
import os
import re
from datetime import datetime
from pathlib import Path

import streamlit as st

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

APP_DIR = Path(__file__).resolve().parent
LOGO_NAMES = ("traffic_logo.png", "logo.png", "traffic_logo.png.png", "logo.svg")

BUILTIN_TRAFFIC_LAW_REFERENCE = """
[المرجع النظامي الأساسي لنظام المرور السعودي ولائحته التنفيذية - المواد 50، 60، 61، 62]:
1. المادة (50) وتقسيماتها - تنظيمات السير والأولويات على الطرق:
- المادة (50/2): يجب على قائد المركبة السيطرة على مركبته وتكييف سرعته وفق الظروف الطبيعية وأحوال الطريق، وتهدئة السرعة والتأكد من خلو التقاطع قبل دخوله، وترك مسافة آمنة كافية بينه وبين المركبة التي أمامه.
- المادة (50/4): يحظر الانعطاف أو الدوران للخلف أو الرجوع للخلف أو تغيير المسار إلا بعد التأكد من خلو الطريق وإعطاء الإشارة اللازمة.
- المادة (50/5) - قواعد أولوية المرور في التقاطعات:
  أ) في التقاطعات غير المنظمة بإشارات ضوئية أو رجل مرور أو لوحات أولوية: تكون الأولوية للمركبة التي دخلت التقاطع أولاً.
  ب) عند دخول مركبتين للتقاطع المتكافئ في وقت واحد: تكون الأولوية للمركبة القادمة من جهة اليمين.
  ج) تكون الأولوية للمركبات السائرة في الطريق الرئيسي على المركبات القادمة من طريق فرعي أو موقف أو محطة أو عقار خاص.
  د) تكون الأولوية للمركبات السائرة داخل الدوار على المركبات الراغبة في دخول الدوار.
  هـ) تكون الأولوية للمركبات السائرة في مسارها المستقيم على المركبات الراغبة في الانعطاف أو الدوران أو تغيير المسار.
2. المادة (60): الحادث المروري هو كل حادث ينتج عنه أضرار بشرية أو مادية دون قصد نتيجة استخدام المركبة، وتُقسم نسب المسؤولية حصرياً وفق النسب القياسية المعتمدة: (100%، 75%، 50%، 25%، 0%) بحيث يكون مجموع نسب الأطراف 100% دائماً.
3. المادة (61) والمادة (62): تختص الإدارة المختصة (المرور) بمباشرة الحوادث المرورية، معاينة الموقع، رفع الآثار المادية، تخطيط الرسم الميداني (الكروكي)، وتحديد نسب الإدانة والمسؤولية بدقة وفق الأنظمة.
"""

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
    "اندفاع قسري (نتيجة صدم خلفي)",
]

FALLBACK_ORB_SVG = """
<svg viewBox="0 0 100 100" width="78" height="78" fill="none">
    <circle cx="50" cy="50" r="44" stroke="#00f2fe" stroke-width="2" stroke-dasharray="6 4"/>
    <circle cx="50" cy="50" r="32" stroke="#38bdf8" stroke-width="1.5" fill="rgba(0,242,254,0.12)"/>
    <path d="M50 22L72 34V54C72 69 50 80 50 80C50 80 28 69 28 54V34L50 22Z" stroke="#ffffff" stroke-width="2.2" fill="rgba(14,165,233,0.35)"/>
    <circle cx="50" cy="50" r="8" fill="#00f2fe"/>
</svg>
"""

PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800;900&family=Orbitron:wght@700;900&display=swap');
html, body, [class*="css"], .stApp {
    font-family: 'Tajawal', sans-serif !important;
    direction: rtl;
}
.stApp, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 50% -10%, rgba(0, 242, 254, 0.35) 0%, rgba(2, 132, 199, 0.15) 30%, transparent 65%),
        radial-gradient(circle at 15% 20%, rgba(14, 165, 233, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 85% 20%, rgba(14, 165, 233, 0.22) 0%, transparent 45%),
        radial-gradient(circle at 50% 100%, rgba(0, 242, 254, 0.25) 0%, transparent 55%),
        linear-gradient(180deg, #020b1c 0%, #041938 45%, #031126 80%, #010712 100%) !important;
    color: #ffffff !important;
    background-attachment: fixed !important;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0, 242, 254, 0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 242, 254, 0.04) 1px, transparent 1px);
    background-size: 45px 45px;
    pointer-events: none;
    z-index: 0;
}
/*WATERMARK*/
[data-testid="stHeader"] {
    background: transparent !important;
}
.block-container {
    max-width: 1050px !important;
    position: relative;
    z-index: 2;
}
.st-key-device_frame {
    background: linear-gradient(180deg, rgba(6, 32, 72, 0.72) 0%, rgba(3, 18, 42, 0.85) 100%);
    border: 2px solid #00f2fe;
    border-radius: 34px;
    padding: 22px 26px 10px 26px;
    box-shadow:
        0 0 40px rgba(0, 242, 254, 0.35),
        inset 0 0 30px rgba(0, 242, 254, 0.15);
    margin-bottom: 24px;
}
.vision-hero-card {
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
}
.vision-hero-card::before {
    content: "";
    position: absolute;
    top: -50%;
    left: -20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(0, 242, 254, 0.28) 0%, transparent 70%);
    pointer-events: none;
}
.vision-right {
    display: flex;
    flex-direction: column;
    gap: 6px;
    z-index: 2;
}
.top-mini-badge {
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
}
.vision-2030-title {
    font-family: 'Orbitron', 'Tajawal', sans-serif;
    font-size: 2.7rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.1;
    letter-spacing: 2px;
    text-shadow: 0 0 20px #00f2fe, 0 0 40px rgba(0, 242, 254, 0.7);
    margin: 4px 0;
}
.vision-2030-title span {
    color: #00f2fe;
}
.hasm-main-title {
    font-size: 1.75rem;
    font-weight: 900;
    color: #ffffff;
    margin: 0;
    text-shadow: 0 0 14px rgba(56, 189, 248, 0.8);
}
.hasm-subtitle {
    color: #7dd3fc;
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
}
.holo-orb-wrapper {
    position: relative;
    width: 138px;
    height: 138px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    z-index: 2;
}
.holo-orb-ring-outer {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 2.5px solid #00f2fe;
    box-shadow: 0 0 28px #00f2fe, inset 0 0 22px #00f2fe;
    animation: pulseGlow 3s infinite ease-in-out;
}
.holo-orb-ring-inner {
    position: absolute;
    inset: 12px;
    border-radius: 50%;
    border: 1.5px dashed #bae6fd;
    background: radial-gradient(circle, rgba(0, 242, 254, 0.35) 0%, rgba(2, 132, 199, 0.1) 70%);
}
.holo-logo-img {
    width: 82px;
    height: 82px;
    object-fit: contain;
    z-index: 3;
    filter: drop-shadow(0 0 12px #ffffff);
}
@keyframes pulseGlow {
    0%, 100% { transform: scale(1); opacity: 0.95; }
    50% { transform: scale(1.04); opacity: 1; box-shadow: 0 0 42px #00f2fe, inset 0 0 30px #00f2fe; }
}
.holo-status-pill {
    background: linear-gradient(90deg, rgba(0, 242, 254, 0.18) 0%, rgba(14, 165, 233, 0.08) 100%);
    border: 1.5px solid rgba(0, 242, 254, 0.7);
    border-radius: 999px;
    padding: 10px 22px;
    margin-bottom: 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.25);
}
.holo-status-pill .dot {
    width: 11px;
    height: 11px;
    background: #00f2fe;
    border-radius: 50%;
    display: inline-block;
    margin-left: 10px;
    box-shadow: 0 0 12px #00f2fe;
}
.st-key-case_card,
.st-key-parties_card,
.st-key-narrative_card {
    background: linear-gradient(160deg, rgba(7, 41, 92, 0.78) 0%, rgba(4, 21, 51, 0.88) 100%) !important;
    border: 1.8px solid rgba(0, 242, 254, 0.65) !important;
    border-radius: 24px !important;
    padding: 22px 24px 8px 24px !important;
    margin-bottom: 22px !important;
    box-shadow:
        0 10px 35px rgba(0, 0, 0, 0.55),
        0 0 25px rgba(0, 242, 254, 0.22),
        inset 0 0 22px rgba(0, 242, 254, 0.1) !important;
}
.neon-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(0, 242, 254, 0.3);
    padding-bottom: 12px;
    margin-bottom: 16px;
}
.neon-card-title {
    color: #ffffff !important;
    font-size: 1.35rem !important;
    font-weight: 900 !important;
    text-shadow: 0 0 14px rgba(0, 242, 254, 0.75);
    display: flex;
    align-items: center;
    gap: 10px;
}
.neon-badge {
    background: linear-gradient(90deg, #00f2fe 0%, #0284c7 100%);
    color: #011627 !important;
    font-weight: 900;
    font-size: 0.78rem;
    padding: 4px 12px;
    border-radius: 999px;
    box-shadow: 0 0 15px rgba(0, 242, 254, 0.7);
}
.party-title {
    color: #00f2fe;
    margin: 8px 0;
    font-size: 1.05rem;
    font-weight: 800;
}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
    background: rgba(3, 19, 46, 0.88) !important;
    border: 1.4px solid rgba(56, 189, 248, 0.55) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    box-shadow: inset 0 0 10px rgba(0, 242, 254, 0.1) !important;
}
div[data-baseweb="select"] > div:focus-within,
div[data-baseweb="input"] > div:focus-within,
textarea:focus {
    border-color: #00f2fe !important;
    box-shadow: 0 0 18px rgba(0, 242, 254, 0.65), inset 0 0 12px rgba(0, 242, 254, 0.2) !important;
}
label, .stRadio label, .stCheckbox label {
    color: #bae6fd !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
}
.st-key-analyze_btn button,
.st-key-reset_btn button,
.st-key-print_btn button,
.st-key-download_btn button {
    width: 100% !important;
    height: 54px !important;
    background: linear-gradient(90deg, #e0f2fe 0%, #00f2fe 50%, #38bdf8 100%) !important;
    color: #021024 !important;
    border: 2px solid #ffffff !important;
    border-radius: 999px !important;
    font-size: 1.08rem !important;
    font-weight: 900 !important;
    box-shadow: 0 0 28px rgba(0, 242, 254, 0.75) !important;
}
.st-key-analyze_btn button:hover,
.st-key-reset_btn button:hover,
.st-key-print_btn button:hover,
.st-key-download_btn button:hover {
    box-shadow: 0 0 42px rgba(0, 242, 254, 1) !important;
    background: linear-gradient(90deg, #ffffff 0%, #7dd3fc 100%) !important;
}
.holo-bottom-dock {
    background: rgba(4, 22, 52, 0.9);
    border: 1.5px solid rgba(0, 242, 254, 0.55);
    border-radius: 999px;
    padding: 10px 28px;
    margin-top: 6px;
    display: flex;
    justify-content: space-around;
    align-items: center;
    gap: 12px;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.3);
    color: #7dd3fc;
    font-size: 0.88rem;
    font-weight: 700;
}
.holo-bottom-dock span.active {
    color: #00f2fe;
    text-shadow: 0 0 10px #00f2fe;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #041531 0%, #020a18 100%) !important;
    border-left: 2px solid #00f2fe !important;
}
[data-testid="stSidebar"][aria-expanded="false"] {
    width: 0px !important;
    min-width: 0px !important;
    max-width: 0px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
}
#official-report-container,
.st-key-official_report {
    background: radial-gradient(circle at 50% 0%, #0a3570 0%, #041938 55%, #020b1c 100%) !important;
    color: #ffffff !important;
    border-radius: 26px !important;
    padding: 28px 32px !important;
    margin-top: 24px !important;
    border: 2.5px solid #00f2fe !important;
    box-shadow: 0 0 40px rgba(0, 242, 254, 0.45), inset 0 0 25px rgba(0, 242, 254, 0.18) !important;
    direction: rtl !important;
    position: relative !important;
    overflow: hidden !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
.report-holo-header {
    background: linear-gradient(135deg, rgba(8, 52, 115, 0.92) 0%, rgba(3, 24, 58, 0.96) 100%) !important;
    border: 2px solid #00f2fe !important;
    border-radius: 20px !important;
    padding: 18px 24px !important;
    margin-bottom: 20px !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 18px rgba(0, 242, 254, 0.2) !important;
}
#official-report-container .report-vision-tag,
.st-key-official_report .report-vision-tag,
.report-vision-tag {
    font-family: 'Orbitron', 'Tajawal', sans-serif !important;
    font-size: 1.9rem !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    letter-spacing: 1.5px !important;
    text-shadow: 0 0 15px #00f2fe !important;
    margin: 0 0 4px 0 !important;
    line-height: 1.2 !important;
}
#official-report-container .report-vision-tag span,
.st-key-official_report .report-vision-tag span,
.report-vision-tag span {
    color: #00f2fe !important;
}
#official-report-container h2,
#official-report-container h3,
#official-report-container h4,
.st-key-official_report h2,
.st-key-official_report h3,
.st-key-official_report h4 {
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
}
#official-report-container p,
#official-report-container li,
#official-report-container div,
.st-key-official_report p,
.st-key-official_report li,
.st-key-official_report div {
    color: #e0f2fe !important;
    line-height: 1.8 !important;
    font-size: 0.98rem !important;
}
#official-report-container strong,
.st-key-official_report strong {
    color: #ffffff !important;
}
#official-report-container table,
.st-key-official_report table {
    width: 100% !important;
    border-collapse: separate !important;
    border-spacing: 0 !important;
    margin: 14px 0 !important;
    background: rgba(4, 22, 52, 0.85) !important;
    border: 1.5px solid #00f2fe !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.2) !important;
}
#official-report-container table th,
#official-report-container table thead tr,
.st-key-official_report table th,
.st-key-official_report table thead tr {
    background: linear-gradient(90deg, #0284c7 0%, #00f2fe 100%) !important;
    color: #011627 !important;
    font-weight: 900 !important;
    font-size: 0.96rem !important;
    padding: 11px 14px !important;
    border-bottom: 2px solid #ffffff !important;
    text-align: right !important;
}
#official-report-container table td,
.st-key-official_report table td {
    background: rgba(6, 30, 68, 0.82) !important;
    color: #f0f9ff !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid rgba(0, 242, 254, 0.25) !important;
    border-left: 1px solid rgba(0, 242, 254, 0.15) !important;
    text-align: right !important;
    font-weight: 600 !important;
}
#official-report-container table tr:nth-child(even) td,
.st-key-official_report table tr:nth-child(even) td {
    background: rgba(10, 42, 90, 0.88) !important;
    color: #ffffff !important;
}
.report-logo {
    width: 65px;
    height: 65px;
    object-fit: contain;
    filter: drop-shadow(0 0 10px rgba(0, 242, 254, 0.85));
}
@media (max-width: 760px) {
    .vision-hero-card {
        flex-direction: column-reverse;
        text-align: center;
        padding: 20px;
    }
    .vision-right { align-items: center; }
    .vision-2030-title { font-size: 2rem; }
    .holo-status-pill,
    .holo-bottom-dock { flex-wrap: wrap; justify-content: center; }
}
@media print {
    @page { size: A4 portrait; margin: 8mm !important; }
    * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        color-adjust: exact !important;
    }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container {
        background: #020b1c !important;
        color: #ffffff !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    .stApp::before, .stApp::after, header, [data-testid="stHeader"], [data-testid="stToolbar"],
    [data-testid="stSidebar"], [data-testid="collapsedControl"],
    .st-key-device_frame, .st-key-report_actions {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    #official-report-container,
    .st-key-official_report {
        margin: 0 !important;
        width: 100% !important;
        background: radial-gradient(circle at 50% 0%, #0a3570 0%, #041938 55%, #020b1c 100%) !important;
        color: #ffffff !important;
        border: 2.5px solid #00f2fe !important;
        box-shadow: 0 0 40px rgba(0, 242, 254, 0.45), inset 0 0 25px rgba(0, 242, 254, 0.18) !important;
    }
    #official-report-container table th,
    #official-report-container table thead tr,
    .st-key-official_report table th,
    .st-key-official_report table thead tr {
        background: linear-gradient(90deg, #0284c7 0%, #00f2fe 100%) !important;
        color: #011627 !important;
    }
    #official-report-container table td,
    .st-key-official_report table td {
        background: rgba(6, 30, 68, 0.82) !important;
        color: #f0f9ff !important;
    }
}
</style>
"""


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def find_logo_file():
    for name in LOGO_NAMES:
        path = APP_DIR / name
        if path.is_file():
            return path
    return None


def logo_src(path: Path) -> str:
    mime = "image/svg+xml" if path.suffix.lower() == ".svg" else "image/png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def section_header(title: str, badge: str) -> None:
    st.html(
        f"""
        <div class="neon-card-header">
            <div class="neon-card-title">{title}</div>
            <span class="neon-badge">{badge}</span>
        </div>
        """
    )


def load_api_key():
    try:
        value = st.secrets.get("GROQ_API_KEY")
        if value:
            return value
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")


def find_law_pdf():
    matches = sorted(APP_DIR.glob("*.pdf"))
    return matches[0] if matches else None


@st.cache_data(show_spinner=False)
def load_traffic_law_pages(pdf_path: str, start_page: int, end_page: int) -> str:
    extracted_text = ""
    path = Path(pdf_path) if pdf_path else None
    if path and path.is_file():
        try:
            if fitz is not None:
                doc = fitz.open(path)
                start_index = max(0, start_page - 1)
                end_index = min(len(doc), end_page)
                extracted_text = "\n".join(
                    doc[i].get_text("text") for i in range(start_index, end_index)
                )
                doc.close()
            elif PdfReader is not None:
                reader = PdfReader(str(path))
                start_index = max(0, start_page - 1)
                end_index = min(len(reader.pages), end_page)
                extracted_text = "\n".join(
                    reader.pages[i].extract_text() or ""
                    for i in range(start_index, end_index)
                )
        except Exception:
            extracted_text = ""
    if len(extracted_text) > 12000:
        extracted_text = extracted_text[:12000]
    return BUILTIN_TRAFFIC_LAW_REFERENCE + "\n\n" + extracted_text


def clean_ai_output(text: str) -> str:
    text = re.sub(r"\(صفحات\s*50\s*-\s*80\)", "", text)
    text = re.sub(r"\(الصفحات\s*50\s*-\s*80\)", "", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def reset_all_fields():
    st.session_state.analysis_result = None
    st.session_state.report_meta = {}
    st.session_state.reset_counter += 1


def build_system_prompt(law_reference_text: str) -> str:
    return f"""
أنت خبير هندسة مرورية ومحقق نظامي معتمد في الإدارة العامة للمرور بالمملكة العربية السعودية.
مهمتك تحليل الحادث المروري وتحديد نسب المسؤولية بصرامة مطلقة ودقة هندسية وقانونية استناداً إلى نظام المرور السعودي ولائحته التنفيذية (المواد 50، 60، 61، 62).
[القواعد القانونية والهندسية الملزمة]:
1. يُمنع منعاً باتاً الامتناع عن تحديد النسب أو كتابة "غير ممكن تحديد المسؤولية". يجب دائماً إصدار حكم فاصل بنسب قياسية معتمدة فقط: (100%، 75%، 50%، 25%، 0%) بحيث يكون مجموع نسب الأطراف = 100% دائماً.
2. قاعدة الهندسة المرورية ونقطة الاصطدام:
   - إذا اصطدمت (مقدمة) المركبة أ بـ (جانب / أبواب) المركبة ب في منتصف التقاطع، فهذا دليل هندسي مادي قاطع على أن (المركبة ب المصدومة في جانبها) هي التي دخلت التقاطع أولاً وقطعت مسافة داخله، وليس العكس.
   - في التقاطعات المتكافئة غير المنظمة بإشارات، المركبة القادمة من جهة اليمين لها أولوية المرور (المادة 50/5).
3. متى تطبق نسب (100%-0%) مقابل (75%-25%) مقابل (50%-50%)؟
   - (100% - 0%): عندما يكون طرف ملتزماً تماماً بسرعة نظامية وأولوية مطلقة والآخر خالف صراحةً.
   - (75% - 25%): في حالة الاشتراك بالخطأ مع تفاوت الجسامة:
     * طرف خالف قاعدة الأولوية (يتحمل 75% وفق المادة 50/5)، والطرف الآخر له الأولوية ولكنه كان يقود بسرعة زائدة عن الحد أو لم يهدئ السرعة عند الاقتراب من التقاطع أو لم يتخذ الحيطة الكافية لتفادي الحادث (يتحمل 25% وفق المادة 50/2).
     * أو في تقاطع غير منظم عندما يدخل طرف للتقاطع أولاً دون التثبت التام من خلوه (25%) ويصدمه الطرف الآخر بمقدمته في جانبه لعدم إعطائه الأولوية وعدم الانتباه (75%).
   - (50% - 50%): عند تساوي الطرفين في الإهمال والخطأ المشترك بنفس الدرجة.
4. لا تذكر مصطلح "حوادث التتابع" أو "الدفع القسري" إلا إذا كان الحادث المدخل هو فعلياً حادث تتابع لعدة مركبات.
5. التزم بمستوى الصرامة المدخل. في الوضع الصارم لا تستخدم إلا النسب القياسية المذكورة.
6. اكتب بلغة عربية فصيحة ورسمية ومرتبة 100%، وابدأ مباشرة بالأقسام الأربعة التالية فقط دون إعادة كتابة بيانات المحضر العلوية:
   ### السرد الحر وتحليل الوقائع
   ### التكييف النظامي والمواد المستند إليها
   ### جدول المخطئ ونسب المسؤولية المعتمدة
   (جدول Markdown رسمي بالأعمدة: | الطرف | المركبة | نسبة المسؤولية % | سبب الإدانة / الإعفاء | السند النظامي من المادة |)
   ### الخلاصة النظامية
[النصوص النظامية المرجعية]:
{law_reference_text}
"""


def run_analysis(api_key: str, system_prompt: str, user_prompt: str):
    client = Groq(api_key=api_key)
    models_to_try = ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "llama-3.1-8b-instant"]
    last_error = None
    for model_name in models_to_try:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=1800,
            )
            response_text = completion.choices[0].message.content
            if response_text:
                return response_text, None
        except Exception as error:
            last_error = error
    return None, last_error


st.set_page_config(
    page_title="حسم الذكي | Vision 2030 GovTech",
    page_icon="🚓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "report_meta" not in st.session_state:
    st.session_state.report_meta = {}

logo_file = find_logo_file()
logo_uri = logo_src(logo_file) if logo_file else None
if logo_uri:
    center_hologram = (
        f'<img src="{logo_uri}" class="holo-logo-img" alt="شعار المرور">'
    )
    watermark_bg = f"""
    .stApp::after {{
        content: "";
        position: fixed;
        top: 52%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 480px;
        height: 480px;
        background-image: url("{logo_uri}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: contain;
        opacity: 0.04;
        pointer-events: none;
        z-index: 0;
    }}
    """
else:
    center_hologram = FALLBACK_ORB_SVG
    watermark_bg = ""

st.html(PAGE_CSS.replace("/*WATERMARK*/", watermark_bg))

law_pdf = find_law_pdf()
law_reference_text = load_traffic_law_pages(str(law_pdf or ""), 50, 80)
rc = st.session_state.reset_counter

with st.container(key="device_frame", border=False):
    st.html(
        f"""
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
                {center_hologram}
            </div>
        </div>
        <div class="holo-status-pill">
            <div><span class="dot"></span><strong>حالة النظام:</strong> مرتبط بنظام المرور السعودي ولائحته التنفيذية</div>
            <div style="color:#00f2fe; font-weight:800;">AI ENGINE ACTIVE</div>
        </div>
        """
    )

    with st.container(key="case_card", border=False):
        section_header("🛡️ بيانات المحضر وظروف الموقع الميدانية", "بيانات المباشرة")
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            inv_name = st.text_input("اسم المحقق", value="", placeholder="أدخل اسم المحقق...", key=f"inv_name_{rc}")
            inv_id = st.text_input("الرقم الوظيفي / العسكري", value="", placeholder="أدخل الرقم...", key=f"inv_id_{rc}")
        with m_col2:
            report_no = st.text_input("رقم البلاغ / المحضر", value="", placeholder="أدخل رقم المحضر...", key=f"report_no_{rc}")
            city = st.text_input("المدينة / الموقع", value="", placeholder="مثال: المدينة - الحي / الشارع", key=f"city_{rc}")
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
                    "مدخل أو مخرج خدمة / محطة / موقف",
                ],
                key=f"site_type_{rc}",
            )
            weather = st.selectbox(
                "حالة الطقس",
                ["صحو", "ممطر", "غبار / ضباب", "رياح شديدة"],
                key=f"weather_{rc}",
            )
        with m_col4:
            road_cond = st.selectbox(
                "حالة الطريق",
                ["جاف", "مبتل / زلق", "أعمال طريق", "غير معبد"],
                key=f"road_cond_{rc}",
            )
            lighting = st.selectbox(
                "الإنارة",
                ["نهار", "ليل - إنارة جيدة", "ليل - بدون إنارة"],
                key=f"lighting_{rc}",
            )
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            injuries = st.selectbox(
                "الإصابات",
                ["لا توجد", "إصابات بسيطة", "إصابات متوسطة / بليغة", "وفيات"],
                key=f"injuries_{rc}",
            )
        with s_col2:
            damages = st.selectbox(
                "الأضرار المادية",
                ["بسيطة", "متوسطة", "تلف كبير"],
                key=f"damages_{rc}",
            )
        with s_col3:
            strict_mode = st.selectbox(
                "مستوى الصرامة النظامية",
                ["صارم نظامي (100% / 75% / 50% / 25% / 0%)", "قياسي استدلالي"],
                key=f"strict_mode_{rc}",
            )

    with st.container(key="parties_card", border=False):
        section_header("🚗 أطراف الحادث وخيارات المناورة الميدانية", "تحليل المركبات")
        num_parties = st.segmented_control(
            "عدد المركبات / الأطراف المشتركة في الحادث",
            [2, 3, 4],
            default=2,
            required=True,
            key=f"num_parties_{rc}",
            width="stretch",
        )
        parties_data = []
        p_cols = st.columns(2)
        for i in range(num_parties):
            with p_cols[i % 2]:
                st.html(f'<h4 class="party-title">🔹 بيانات الطرف ({i + 1})</h4>')
                r1, r2 = st.columns(2)
                with r1:
                    p_role = st.selectbox(
                        f"صفة الطرف {i + 1}",
                        ["سائق", "مشاة", "مالك مركبة متوقفة"],
                        key=f"p_role_{i}_{rc}",
                    )
                    p_veh = st.text_input(
                        f"نوع المركبة {i + 1}",
                        placeholder="مثال: إف جي / صالون / كامري",
                        key=f"p_veh_{i}_{rc}",
                    )
                    p_plate = st.text_input(
                        f"رقم اللوحة {i + 1}",
                        placeholder="ح س ص 4444",
                        key=f"p_plate_{i}_{rc}",
                    )
                    p_dir = st.selectbox(
                        f"الاتجاه {i + 1}",
                        ["شمال", "جنوب", "شرق", "غرب", "شمال شرقي", "شمال غربي", "جنوب شرقي", "جنوب غربي"],
                        key=f"p_dir_{i}_{rc}",
                    )
                with r2:
                    p_lane = st.selectbox(
                        f"المسار {i + 1}",
                        ["أيمن", "أوسط", "أيسر", "مسار خدمة", "كتف الطريق", "داخل التقاطع"],
                        key=f"p_lane_{i}_{rc}",
                    )
                    p_man = st.selectbox(
                        f"المناورة {i + 1}",
                        MANEUVER_OPTIONS,
                        key=f"p_man_{i}_{rc}",
                    )
                    p_sig = st.selectbox(
                        f"الإشارة {i + 1}",
                        ["لا توجد إشارة", "إشارة خضراء", "إشارة حمراء", "إشارة صفراء متقطعة", "لوحة قف (STOP)", "لوحة أعطِ الأولوية"],
                        key=f"p_sig_{i}_{rc}",
                    )
                    p_prio = st.selectbox(
                        f"الأولوية {i + 1}",
                        ["له أولوية", "عليه أولوية للغير (يجب التوقف/التهدئة)", "متكافئ / غير محدد"],
                        index=0 if i == 0 else 1,
                        key=f"p_prio_{i}_{rc}",
                    )
                p_spd = st.selectbox(
                    f"السرعة التقديرية للطرف {i + 1}",
                    ["ضمن الحد النظامي", "زائدة عن الحد النظامي", "سرعة عالية جداً (تهور)", "متوقف تماماً"],
                    key=f"p_spd_{i}_{rc}",
                )
                parties_data.append(
                    {
                        "طرف": f"الطرف {i + 1}",
                        "الصفة": p_role,
                        "المركبة": p_veh.strip() or f"مركبة {i + 1}",
                        "اللوحة": p_plate.strip() or "غير محدد",
                        "الاتجاه": p_dir,
                        "المسار": p_lane,
                        "المناورة": p_man,
                        "الإشارة": p_sig,
                        "الأولوية": p_prio,
                        "السرعة": p_spd,
                    }
                )

    with st.container(key="narrative_card", border=False):
        section_header("📐 التحليل الهندسي الميداني والسرد الحر للواقعة", "الابتكار التقني")
        sk_col1, sk_col2 = st.columns(2)
        with sk_col1:
            sketch_notes = st.text_area(
                "ملاحظات الكروكي / الرسم الميداني (نقطة الاصطدام، آثار الفرملة، المطبات)",
                placeholder="مثال: نقطة الاصطدام في منتصف التقاطع، مقدمة المركبة الأولى في الباب الأيمن للثانية...",
                height=95,
                key=f"sketch_notes_{rc}",
            )
        with sk_col2:
            witness_notes = st.text_area(
                "إفادات الشهود / الكاميرات وملاحظات المحقق",
                placeholder="أقوال الشهود أو ملاحظات المباشر الميداني...",
                height=95,
                key=f"witness_notes_{rc}",
            )
        narrative = st.text_area(
            "السرد الحر لتفاصيل الحادث (المركبات، الاتجاهات، التسلسل الزمني، كيفية وقوع التصادم)",
            placeholder="اكتب تفاصيل الحادث هنا ليقوم محرك حسم الذكي بتكييف المواد النظامية وتحديد نسب المسؤولية بدقة...",
            height=130,
            key=f"narrative_{rc}",
        )
        feedback = st.empty()
        btn_c1, btn_c2 = st.columns(2, vertical_alignment="bottom")
        with btn_c1:
            analyze_clicked = st.button(
                "⚡ بدء التحليل النظامي الفوري",
                key="analyze_btn",
                width="stretch",
            )
        with btn_c2:
            st.button(
                "🗑️ مسح البيانات / حادث جديد",
                key="reset_btn",
                on_click=reset_all_fields,
                width="stretch",
            )

    st.html(
        """
        <div class="holo-bottom-dock">
            <span class="active">● الاستدلال النظامي</span>
            <span>◎ الهندسة المرورية</span>
            <span>◈ المواد (50 - 62)</span>
            <span>❖ التقارير الرسمية</span>
        </div>
        """
    )

if analyze_clicked:
    st.session_state.analysis_result = None
    if not narrative.strip():
        feedback.warning("يرجى كتابة تفاصيل الحادث في خانة السرد الحر قبل بدء التحليل.")
    else:
        api_key = load_api_key()
        if not api_key:
            feedback.error("لم يتم العثور على مفتاح GROQ_API_KEY في الأسرار أو متغيرات البيئة.")
        elif Groq is None:
            feedback.error("مكتبة groq غير مثبتة.")
        else:
            parties_summary = "\n".join(
                [
                    (
                        f"- {p['طرف']}: الصفة ({p['الصفة']})، المركبة ({p['المركبة']})، "
                        f"اللوحة ({p['اللوحة']})، الاتجاه ({p['الاتجاه']})، المسار ({p['المسار']})، "
                        f"المناورة ({p['المناورة']})، الإشارة ({p['الإشارة']})، "
                        f"الأولوية المدخلة ({p['الأولوية']})، السرعة ({p['السرعة']})."
                    )
                    for p in parties_data
                ]
            )
            sketch_line = f"ملاحظات الكروكي: {sketch_notes}" if sketch_notes.strip() else ""
            witness_line = f"إفادات الشهود والملاحظات: {witness_notes}" if witness_notes.strip() else ""
            user_prompt = f"""
بيانات الموقع: {site_type} | الطقس: {weather} | الطريق: {road_cond} | الإنارة: {lighting}
الإصابات: {injuries} | الأضرار المادية: {damages}
مستوى الصرامة النظامية: {strict_mode}
الأطراف:
{parties_summary}
السرد الحر:
{narrative}
{sketch_line}
{witness_line}
"""
            with feedback.container():
                with st.spinner("جاري تشغيل محرك الاستدلال النظامي وتحليل هندسة الاصطدام..."):
                    response_text, last_error = run_analysis(
                        api_key,
                        build_system_prompt(law_reference_text),
                        user_prompt,
                    )
            if response_text:
                st.session_state.analysis_result = clean_ai_output(response_text)
                st.session_state.report_meta = {
                    "report_no": report_no.strip() or "غير محدد",
                    "inv_name": inv_name.strip() or "غير محدد",
                    "inv_id": inv_id.strip() or "غير محدد",
                    "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "location": city,
                    "site_type": site_type,
                    "env": f"الطقس: {weather} | الطريق: {road_cond} | الإنارة: {lighting}",
                    "inj_dmg": f"الإصابات: {injuries} | الأضرار: {damages}",
                    "strict_mode": strict_mode,
                    "parties": parties_data,
                }
            else:
                feedback.error(f"تعذر إتمام التحليل حالياً: {last_error}")

if st.session_state.analysis_result:
    meta = st.session_state.report_meta
    party_rows = []
    for party in meta.get("parties", []):
        details = (
            f"الصفة: {esc(party['الصفة'])} | اللوحة: {esc(party['اللوحة'])} | "
            f"الاتجاه: {esc(party['الاتجاه'])} | المسار: {esc(party['المسار'])} | "
            f"المناورة: {esc(party['المناورة'])} | الإشارة: {esc(party['الإشارة'])} | "
            f"الأولوية: {esc(party['الأولوية'])} | السرعة: {esc(party['السرعة'])}"
        )
        party_rows.append(
            "<tr>"
            f"<td style=\"width:18%; font-weight:800;\">{esc(party['طرف'])} ({esc(party['المركبة'])})</td>"
            f"<td>{details}</td>"
            "</tr>"
        )
    header_logo = (
        f'<img src="{logo_uri}" class="report-logo" alt="شعار المرور">'
        if logo_uri
        else ""
    )
    with st.container(key="official_report", border=False):
        st.html(
            f"""
            <div class="report-holo-header">
                <div>
                    <p class="report-vision-tag">VISION <span>2030</span></p>
                    <p><strong>حسم الذكي للحوادث المرورية</strong></p>
                    <p>تقرير نظامي رسمي لتحليل المسؤولية المرورية</p>
                </div>
                {header_logo}
            </div>
            <h3>بيانات المحضر وأطراف الحادث</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width:22%;">البند</th>
                        <th>البيان</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td>رقم المحضر</td><td>{esc(meta.get("report_no", ""))}</td></tr>
                    <tr><td>المحقق المباشر</td><td>{esc(meta.get("inv_name", ""))} | الرقم: {esc(meta.get("inv_id", ""))}</td></tr>
                    <tr><td>التاريخ والوقت</td><td>{esc(meta.get("datetime", ""))}</td></tr>
                    <tr><td>الموقع ونوعه</td><td>{esc(meta.get("location", ""))} ({esc(meta.get("site_type", ""))})</td></tr>
                    <tr><td>ظروف الموقع</td><td>{esc(meta.get("env", ""))}</td></tr>
                    <tr><td>الإصابات والأضرار</td><td>{esc(meta.get("inj_dmg", ""))}</td></tr>
                    <tr><td>مستوى الصرامة</td><td>{esc(meta.get("strict_mode", ""))}</td></tr>
                    {"".join(party_rows)}
                </tbody>
            </table>
            """
        )
        st.markdown(st.session_state.analysis_result)

    full_txt_report = f"""حسم الذكي للحوادث المرورية - تقرير نظامي رسمي
=================================================
رقم المحضر: {meta.get("report_no")}
المحقق: {meta.get("inv_name")} ({meta.get("inv_id")})
التاريخ والوقت: {meta.get("datetime")}
الموقع: {meta.get("location")} - {meta.get("site_type")}
=================================================
{st.session_state.analysis_result}
"""
    with st.container(key="report_actions", border=False):
        act_col1, act_col2 = st.columns(2, vertical_alignment="bottom")
        with act_col1:
            print_clicked = st.button(
                "🖨️ طباعة التقرير الرسمي (PDF)",
                key="print_btn",
                width="stretch",
            )
        with act_col2:
            st.download_button(
                label="💾 حفظ وتحميل التقرير",
                data=full_txt_report.encode("utf-8"),
                file_name=f"Hasm_Report_{meta.get('report_no')}.txt",
                mime="text/plain",
                key="download_btn",
                width="stretch",
            )
        if print_clicked:
            st.html("<script>window.print();</script>", unsafe_allow_javascript=True)
