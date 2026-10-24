import html
import re
import time

import pandas as pd
import PyPDF2
import streamlit as st
import streamlit.components.v1 as components
from groq import Groq

st.set_page_config(
    page_title="حسم الذكي للحوادث المرورية",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      html, body, .stApp, [data-testid="stAppViewContainer"],
      [data-testid="stHeader"], [data-testid="stToolbar"],
      [data-testid="stSidebar"], [data-testid="stSidebarContent"],
      .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
      }
      .stMarkdown, .stText, .stCaption, label, p, h1, h2, h3, h4, h5, h6,
      .stAlert, [data-testid="stNotification"], [data-testid="stWidgetLabel"] {
        direction: rtl !important;
        text-align: right !important;
      }
      textarea, input, .stTextArea textarea, .stTextInput input {
        direction: rtl !important;
        text-align: right !important;
      }
      div[data-baseweb="select"] > div, div[data-baseweb="input"] {
        direction: rtl !important;
        text-align: right !important;
      }
      [data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
      }
      [data-testid="stSidebar"] {
        overflow-x: hidden !important;
      }
      [data-testid="stSidebar"][aria-expanded="false"] {
        width: 0px !important;
        min-width: 0px !important;
        overflow: hidden !important;
      }
      [data-testid="stSidebar"][aria-expanded="false"] > div {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
      }
      .hasm-hero {
        display: flex;
        align-items: center;
        gap: 18px;
        margin: 0.2rem 0 1.4rem;
        padding: 1.1rem 1.3rem;
        border: 1px solid rgba(120, 200, 255, 0.25);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(8, 28, 48, 0.92), rgba(12, 64, 86, 0.78));
      }
      .hasm-mark {
        width: 64px;
        height: 64px;
        flex: 0 0 64px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        font-size: 34px;
        color: #7ee7ff;
        background: radial-gradient(circle at 30% 30%, #1bd6ff, #0b3b63 62%);
        box-shadow: 0 0 24px rgba(80, 220, 255, 0.35);
      }
      .hasm-hero h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 800;
        color: #f4fbff;
        letter-spacing: 0.3px;
      }
      .hasm-hero p {
        margin: 0.25rem 0 0;
        color: #b7d7e8;
        font-size: 0.98rem;
      }
      .stButton > button {
        width: 100%;
        font-weight: 700;
      }
      .print-document {
        background: #ffffff;
        color: #111827;
        border: 1px solid #d7dde6;
        border-radius: 12px;
        padding: 1.3rem 1.4rem 1.5rem;
        margin: 0.4rem 0 1rem;
      }
      .print-document h2, .print-document h3, .print-document h4 {
        color: #0f3d5e;
        font-family: Tahoma, Arial, sans-serif;
        margin: 1rem 0 0.45rem;
      }
      .print-brand {
        border-bottom: 3px solid #0f3d5e;
        padding-bottom: 0.7rem;
        margin-bottom: 1rem;
      }
      .print-brand h2 {
        margin: 0;
        font-size: 1.35rem;
        color: #0f3d5e;
      }
      .print-brand p {
        margin: 0.2rem 0 0;
        color: #4a5b6b;
      }
      .official-report {
        line-height: 1.9;
        text-align: right;
        direction: rtl;
        font-family: Tahoma, Arial, sans-serif;
        font-size: 1.02rem;
        color: #111827;
      }
      .print-document table,
      .official-report table,
      [data-testid="stTable"] table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.8rem 0 1.1rem;
        background: #ffffff !important;
      }
      .print-document th,
      .official-report th,
      [data-testid="stTable"] th {
        background: #0f3d5e !important;
        color: #ffffff !important;
        font-weight: 700;
        padding: 10px 8px;
        border: 1px solid #0b2e47;
      }
      .print-document td,
      .official-report td,
      [data-testid="stTable"] td,
      .print-document td *,
      .official-report td *,
      [data-testid="stTable"] td * {
        border: 1px solid #c5d0db;
        padding: 9px 8px;
        background: #ffffff !important;
        color: #111827 !important;
      }
      .print-document tr:nth-child(even) td,
      .official-report tr:nth-child(even) td,
      [data-testid="stTable"] tbody tr:nth-child(even) td,
      .print-document tr:nth-child(even) td *,
      .official-report tr:nth-child(even) td *,
      [data-testid="stTable"] tbody tr:nth-child(even) td * {
        background: #f8f9fa !important;
        color: #111827 !important;
      }
      [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]) {
        align-items: stretch !important;
        gap: 0.75rem;
      }
      [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]) [data-testid="stColumn"] {
        display: flex !important;
        align-items: stretch !important;
      }
      [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]:has([data-testid="stDownloadButton"]) iframe {
        height: 48px !important;
        min-height: 48px !important;
        width: 100% !important;
        border: 0 !important;
      }
      [data-testid="stDownloadButton"],
      [data-testid="stDownloadButton"] > button,
      .stDownloadButton,
      .stDownloadButton > button {
        width: 100% !important;
        height: 48px !important;
        min-height: 48px !important;
        margin: 0 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        background: #0f3d5e !important;
        color: #ffffff !important;
        border: 1px solid #0b2e47 !important;
      }
      @media print {
        @page {
          size: A4;
          margin: 12mm;
        }
        html, body, .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stMain"], [data-testid="stAppScrollToBottomContainer"],
        .main, .block-container, [data-testid="stHeader"] {
          background: #ffffff !important;
          color: #000000 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        body * {
          visibility: hidden !important;
        }
        #official-print-report,
        #official-print-report * {
          visibility: visible !important;
        }
        #official-print-report {
          position: absolute !important;
          inset: 0 !important;
          width: 100% !important;
          margin: 0 !important;
          padding: 0 !important;
          border: none !important;
          border-radius: 0 !important;
          box-shadow: none !important;
          background: #ffffff !important;
          color: #000000 !important;
        }
        header, footer, [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"], .hasm-hero,
        .no-print, .stDownloadButton, [data-testid="stDownloadButton"],
        .stButton, iframe, [data-testid="stBottomBlockContainer"],
        [data-testid="stTextInput"], [data-testid="stTextArea"],
        [data-testid="stSelectbox"], [data-testid="stRadio"],
        [data-testid="stCheckbox"], [data-testid="stDateInput"],
        [data-testid="stTimeInput"], [data-testid="stAlert"],
        [data-testid="stNotification"], [data-testid="stWidgetLabel"],
        [data-testid="stChatInput"], hr {
          display: none !important;
        }
        .print-document, .official-report, .print-brand,
        .print-document *, .official-report *, .print-brand *,
        table, thead, tbody, tr, th, td {
          background: #ffffff !important;
          color: #000000 !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
        .print-document th, .official-report th, th {
          background: #ffffff !important;
          color: #000000 !important;
          border: 1px solid #000000 !important;
        }
        .print-document td, .official-report td, td,
        .print-document td *, .official-report td *, td * {
          background: #ffffff !important;
          color: #000000 !important;
          border: 1px solid #000000 !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

GROQ_MODEL = "openai/gpt-oss-120b"
API_KEY_NAME = "GROQ_API_KEY"
APPROVED_RATIOS = ("0%", "25%", "50%", "75%", "100%")
PDF_PATH = "traffic.pdf"
LAW_PAGE_START = 50
LAW_PAGE_END = 80
CHUNK_SIZE = 1800
CHUNK_OVERLAP = 150
MAX_MAP_CHUNKS = 4
MAX_EXTRACT_CHARS = 4500
MAX_QUERY_CHARS = 900
REQUEST_PAUSE_SEC = 1.8
MAX_RETRIES = 4
LAW_KEYWORDS = (
    "حادث", "مسؤولية", "خطأ", "تقاطع", "إشارة", "تجاوز", "أولوية", "مسار",
    "انعطف", "انعطاف", "سرعة", "مشاة", "وقوف", "متوقف", "رجوع", "دوار",
    "يسار", "يمين", "حمراء", "خضراء", "كتف", "مخرج", "مدخل", "عكس",
    "مركبة", "سائق", "تصادم", "اصطدام", "مادة",
)
CHAIN_HINTS = (
    "تتابع",
    "رتل",
    "دفع قسري",
    "اندفعت قسرا",
    "اندفعت قسري",
    "اصطدام متسلسل",
    "سلسلة اصطدام",
    "مركبات متتالية",
    "عدة مركبات خلف",
    "صدمتها من الخلف فاندفعت",
    "اصطدمت من الخلف واندفعت",
)
MANEUVERS = [
    "سير مستقيم",
    "انعطاف يمين",
    "انعطاف يسار",
    "دوران للخلف",
    "تجاوز",
    "تغيير مسار",
    "رجوع للخلف",
    "توقف مفاجئ",
    "مركبة متوقفة",
    "فتح باب",
    "خروج من موقف",
]
SIGNALS = ["لا توجد إشارة", "خضراء", "صفراء", "حمراء", "وميض", "غير معلوم"]
PRIORITIES = ["له أولوية", "عليه أولوية للغير", "غير محدد"]


def liability_rules(apply_chain_rules=False):
    text = (
        "أنت خبير تحقيق حوادث مرورية. التزم حرفياً وبصرامة تامة بالنصوص النظامية "
        "المستخلصة من نظام المرور السعودي ولائحته التنفيذية فقط. "
        "ممنوع أي اجتهاد أو معرفة عامة خارج هذا النص.\n"
        f"- النسب القياسية المعتمدة حصرياً: {' / '.join(APPROVED_RATIOS)}. "
        "مجموع نسب أطراف الحادث يجب أن يساوي 100% دائماً.\n"
        "- اذكر رقم المادة والفقرة الفرعية الدقيقة (مثل 50/2/4 أو 60/1) "
        "واقتبس معناها النظامي قرين كل نسبة خطأ. ممنوع ذكر أرقام صفحات المصدر "
        "وممنوع كتابة أي عبارة مثل (صفحات 50-80) بجانب المواد أو في أي موضع بالتقرير.\n"
        "- النصوص المستخرجة من ملف PDF قد تكون مكسّرة أو معكوسة أو مشوهة. "
        "ممنوع نسخها كما هي. أعد صياغة نص المادة بلغة عربية فصيحة سليمة ومرتبة 100% "
        "مع الإبقاء على رقم المادة والفقرة.\n"
        "- ممنوع استخدام رموز التنسيق أو علامات Markdown داخل التقرير، "
        "بما في ذلك الرموز > و * و --- . التقرير نص رسمي نظيف فقط.\n"
        "- لا تذكر أسماء ملفات أو نماذج برمجية في التقرير.\n"
    )
    if apply_chain_rules:
        text += (
            "- هذا المحضر حادث تتابع لعدة مركبات، فطبّق القاعدتين التاليتين فقط دون تسميتهما بعناوين إنشائية: "
            "المركبة الأولى في مقدمة الرتل التي لم تصدم مركبة أمامها ومقدمتها سليمة نسبة خطئها 0% دائماً. "
            "إذا كانت مركبة متوقفة أو تترك مسافة آمنة واندفعت قسراً بسبب صدمة خلفية قوية لتصدم من أمامها، "
            "تُعفى من مسؤولية الصدم الأمامي (0% عن الصدم الأمامي)، وتتحمل المركبة الصادمة من الخلف المسؤولية الكاملة.\n"
        )
    else:
        text += (
            "- هذا الحادث ليس حادث تتابع لعدة مركبات. "
            "ممنوع منعاً باتاً تطبيق قواعد حوادث التتابع أو الدفع القسري، "
            "وممنوع الإشارة إليهما أو كتابة أي ملاحظة عنهما، "
            "وممنوع ذكر كلمتي «تتابع» أو «دفع قسري» في أي موضع من التقرير. "
            "حلّل الحادث وفق نوعه الفعلي فقط (تقاطع، دوران، رجوع للخلف، تغيير مسار، إشارة، أو غيرها).\n"
        )
    return text


def load_api_key():
    try:
        secrets = st.secrets
    except Exception as error:
        return "", (
            "تعذر قراءة ملف .streamlit/secrets.toml. "
            f"السبب: {type(error).__name__}: {error}"
        )

    try:
        raw = secrets[API_KEY_NAME]
    except Exception:
        return "", (
            f"المطلوب هو المتغير {API_KEY_NAME} تحديداً في .streamlit/secrets.toml. "
            "لن يُستخدم GEMINI_API_KEY أو أي مفتاح آخر."
        )

    value = str(raw or "").strip().strip('"').strip("'")
    value = value.replace("\ufeff", "").replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
    value = value.strip()
    if not value:
        return "", f"المتغير {API_KEY_NAME} موجود لكنه فارغ بعد إزالة المسافات."
    if not value.startswith("gsk_") or len(value) <= 20:
        return "", (
            f"قيمة {API_KEY_NAME} غير صالحة بعد التنظيف بـ strip(). "
            "مفتاح Groq يجب أن يبدأ بـ gsk_."
        )
    return value, ""


def describe_error(error):
    text = str(error)
    status = getattr(error, "status_code", None)
    body = getattr(error, "body", None)
    if status in (401, 403):
        return (
            f"فشل توثيق Groq (رمز {status}). تحقق من المفتاح في st.secrets. "
            f"التفاصيل: {text}"
        )
    if status == 404:
        return (
            f"Groq أعاد 404 أثناء استدعاء النموذج. "
            "غالباً المفتاح غير مقبول أو الطلب غير صالح. "
            f"التفاصيل: {text}"
            + (f" | {body}" if body else "")
        )
    if status == 429 or "rate limit" in text.lower() or "tpm" in text.lower():
        return f"تم تجاوز حد الرموز مؤقتاً. التفاصيل: {text}"
    return f"{type(error).__name__}: {text}"


def groq_client():
    api_key, error = load_api_key()
    if error:
        raise RuntimeError(error)
    try:
        return Groq(api_key=api_key)
    except Exception as error:
        raise RuntimeError(f"فشل إنشاء عميل Groq. {describe_error(error)}") from error


def groq_chat(client, messages, temperature=0.1, max_tokens=2048, allow_empty=False):
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            choices = getattr(response, "choices", None) or []
            content = getattr(getattr(choices[0], "message", None), "content", None) if choices else None
            if content and str(content).strip():
                return str(content).strip()
            if allow_empty:
                return ""
            last_error = RuntimeError("Groq أعاد رداً فارغاً.")
            continue
        except Exception as error:
            last_error = error
            message = str(error).lower()
            if allow_empty and "فارغاً" not in str(error):
                if "rate limit" in message or "tpm" in message or getattr(error, "status_code", None) == 429:
                    time.sleep(min(2 ** attempt + REQUEST_PAUSE_SEC, 20))
                    continue
                return ""
            if "rate limit" in message or "tpm" in message or getattr(error, "status_code", None) == 429:
                time.sleep(min(2 ** attempt + REQUEST_PAUSE_SEC, 20))
                continue
            raise RuntimeError(describe_error(error)) from error
    if allow_empty:
        return ""
    raise RuntimeError(describe_error(last_error or RuntimeError(f"تعذر الاتصال بالنموذج {GROQ_MODEL}.")))


def is_chain_collision(facts, narrative, party_count):
    blob = f"{facts}\n{narrative}"
    if any(hint in blob for hint in CHAIN_HINTS):
        return True
    rear_hit = any(token in blob for token in ("من الخلف", "اصطدام خلفي", "صدمة خلفية", "صدمتها من الخلف"))
    return party_count >= 3 and rear_hit


def clean_report_text(text, strip_chain_terms=False):
    cleaned = str(text or "")
    cleaned = re.sub(r"(?i)<br\s*/?>", "\n", cleaned)
    cleaned = re.sub(r"\(?\s*صفحات?\s*50\s*[-–—/إلى]+\s*80\s*\)?", "", cleaned)
    cleaned = re.sub(r"\(?\s*الصفحات\s*\d+\s*[-–—/إلى]+\s*\d+\s*\)?", "", cleaned)
    cleaned = cleaned.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = re.sub(r"(?i)traffic\.pdf", "نظام المرور ولائحته التنفيذية", cleaned)
    if strip_chain_terms:
        cleaned = re.sub(r"الدفع\s*القسري", "", cleaned)
        cleaned = re.sub(r"دفع\s*قسري", "", cleaned)
        cleaned = re.sub(r"حوادث\s*التتابع", "", cleaned)
        cleaned = re.sub(r"حادث\s*التتابع", "", cleaned)
        cleaned = re.sub(r"قاعدة\s*التتابع", "", cleaned)
        cleaned = re.sub(r"التتابع", "", cleaned)
    lines = []
    for line in cleaned.splitlines():
        if looks_like_table_line(line):
            lines.append(line.replace("*", ""))
            continue
        line = re.sub(r"^\s*>+\s?", "", line)
        line = line.replace(">", "").replace("*", "")
        line = re.sub(r"-{3,}", "", line)
        lines.append(line)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def unique_headers(headers):
    seen = {}
    result = []
    for header in headers:
        name = header or "عمود"
        count = seen.get(name, 0) + 1
        seen[name] = count
        result.append(name if count == 1 else f"{name} ({count})")
    return result


def split_table_row(line):
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def is_separator_row(cells):
    if not cells:
        return False
    return all(re.fullmatch(r":?-{2,}:?", (cell or "").replace(" ", "")) for cell in cells)


def looks_like_table_line(line):
    text = (line or "").strip()
    if not text or text.count("|") < 1:
        return False
    if text.startswith("|") and text.endswith("|"):
        return True
    return text.count("|") >= 2


def parse_markdown_table(lines):
    rows = []
    for line in lines:
        cells = split_table_row(line)
        if not cells or is_separator_row(cells):
            continue
        rows.append(cells)
    if len(rows) < 2:
        return None
    width = max(len(row) for row in rows)
    padded = [row + [""] * (width - len(row)) for row in rows]
    headers = unique_headers(padded[0])
    body = padded[1:]
    frame = pd.DataFrame(body, columns=headers)
    return frame


def parse_report_blocks(text):
    lines = clean_report_text(text).splitlines()
    blocks = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if looks_like_table_line(line):
            table_lines = []
            while index < len(lines) and (looks_like_table_line(lines[index]) or not lines[index].strip()):
                if lines[index].strip():
                    table_lines.append(lines[index])
                index += 1
            frame = parse_markdown_table(table_lines)
            if frame is not None:
                blocks.append(("table", frame))
            else:
                blocks.append(("text", "\n".join(table_lines)))
            continue
        text_lines = []
        while index < len(lines) and not looks_like_table_line(lines[index]):
            text_lines.append(lines[index])
            index += 1
        chunk = "\n".join(text_lines).strip()
        if chunk:
            blocks.append(("text", chunk))
    return blocks


def facts_frame(facts):
    rows = []
    for line in clean_report_text(facts).splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            rows.append({"البند": key.strip(), "البيان": value.strip()})
        else:
            rows.append({"البند": "ملاحظة", "البيان": line})
    if not rows:
        return pd.DataFrame([{"البند": "بيانات المحضر", "البيان": "غير متوفرة"}])
    return pd.DataFrame(rows)


def html_table(frame):
    if frame is None or frame.empty:
        return ""
    head = "".join(f"<th>{html.escape(str(col))}</th>" for col in frame.columns)
    body_rows = []
    for _, row in frame.iterrows():
        cells = "".join(f"<td>{html.escape(str(value))}</td>" for value in row.tolist())
        body_rows.append(f"<tr>{cells}</tr>")
    return (
        "<table><thead><tr>"
        + head
        + "</tr></thead><tbody>"
        + "".join(body_rows)
        + "</tbody></table>"
    )


def text_to_html(text):
    parts = []
    for paragraph in clean_report_text(text).split("\n"):
        raw = paragraph.strip().strip("#").strip()
        if not raw:
            continue
        heading = re.sub(r"^#{1,6}\s*", "", raw)
        if paragraph.strip().startswith("#") or raw.endswith(":"):
            parts.append(f"<h3>{html.escape(heading)}</h3>")
        else:
            parts.append(f"<p>{html.escape(raw)}</p>")
    return "".join(parts)


def official_report_body(facts, report):
    facts_table = html_table(facts_frame(facts))
    report_parts = []
    for kind, payload in parse_report_blocks(report):
        if kind == "table":
            report_parts.append(html_table(payload))
        else:
            report_parts.append(text_to_html(payload))
    report_html = "".join(report_parts) or f"<p>{html.escape(clean_report_text(report))}</p>"
    return f"""
      <div class="print-brand">
        <h2>حسم الذكي للحوادث المرورية</h2>
        <p>تقرير نظامي رسمي لتحليل المسؤولية المرورية</p>
      </div>
      <h3>بيانات المحضر</h3>
      {facts_table}
      <h3>التقرير النظامي</h3>
      <div class="official-report">{report_html}</div>
    """


def report_download_html(facts, report):
    body = official_report_body(facts, report)
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>التقرير الرسمي للحادث</title>
  <style>
    @page {{ size: A4; margin: 16mm; }}
    body {{
      font-family: Tahoma, Arial, sans-serif;
      direction: rtl;
      text-align: right;
      color: #000000;
      background: #ffffff;
      line-height: 1.85;
      margin: 0;
      padding: 8mm;
    }}
    .print-brand {{
      border-bottom: 3px solid #0f3d5e;
      padding-bottom: 10px;
      margin-bottom: 18px;
    }}
    h1, h2, h3 {{ color: #0f3d5e; margin: 16px 0 8px; }}
    .print-brand h2 {{ font-size: 22px; margin: 0; color: #0f3d5e; }}
    p {{ margin: 0 0 10px; color: #111827; }}
    table {{ width: 100%; border-collapse: collapse; margin: 10px 0 16px; background: #ffffff; }}
    th {{ background: #0f3d5e; color: #ffffff; padding: 8px; border: 1px solid #0b2e47; }}
    td {{
      border: 1px solid #c5d0db;
      padding: 8px;
      background: #ffffff;
      color: #111827 !important;
    }}
    tr:nth-child(even) td {{
      background: #f8f9fa;
      color: #111827 !important;
    }}
    .footer {{ margin-top: 28px; font-size: 12px; color: #4a5b6b; }}
    @media print {{
      html, body, table, th, td, p, h1, h2, h3, div {{
        background: #ffffff !important;
        color: #000000 !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }}
      th, td {{ border: 1px solid #000000 !important; }}
    }}
  </style>
</head>
<body>
  {body}
  <div class="footer">أُعد وفق نظام المرور السعودي ولائحته التنفيذية. النسب المعتمدة فقط: 0٪، 25٪، 50٪، 75٪، 100٪.</div>
</body>
</html>
"""


def render_official_report(facts, report):
    body = official_report_body(facts, report)
    st.markdown(
        f'<div class="print-document" id="official-print-report">{body}</div>',
        unsafe_allow_html=True,
    )


@st.cache_data
def load_traffic_law():
    try:
        with open(PDF_PATH, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            total = len(reader.pages)
            start_idx = LAW_PAGE_START - 1
            end_idx = LAW_PAGE_END
            if total <= start_idx:
                return 0, ""
            selected = reader.pages[start_idx:end_idx]
            parts = []
            for page in selected:
                text = page.extract_text() or ""
                if text.strip():
                    parts.append(text.strip())
            return len(selected), "\n".join(parts)
    except Exception:
        return 0, ""


def split_chunks(text):
    pieces = re.split(r"(?=المادة\s+\d+|مادة\s+\d+)", text or "")
    chunks = []
    buffer = ""
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        if len(buffer) + len(piece) + 1 <= CHUNK_SIZE:
            buffer = f"{buffer}\n{piece}".strip()
            continue
        if buffer:
            chunks.append(buffer)
        if len(piece) <= CHUNK_SIZE:
            buffer = piece
            continue
        step = max(CHUNK_SIZE - CHUNK_OVERLAP, 1)
        for start in range(0, len(piece), step):
            chunks.append(piece[start:start + CHUNK_SIZE])
        buffer = ""
    if buffer:
        chunks.append(buffer)
    return chunks


@st.cache_data
def cached_chunks(text):
    return split_chunks(text)


def tokenize(text):
    return set(re.findall(r"[\w\u0600-\u06FF]+", (text or "").lower()))


def select_chunks(chunks, query, limit=MAX_MAP_CHUNKS):
    query_tokens = tokenize(query)
    ranked = []
    for index, chunk in enumerate(chunks):
        overlap = len(query_tokens & tokenize(chunk))
        keywords = sum(1 for word in LAW_KEYWORDS if word in chunk)
        ranked.append((overlap * 2 + keywords, index, chunk[:CHUNK_SIZE]))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    selected = [chunk for score, _index, chunk in ranked[:limit] if score > 0]
    return selected or [chunk[:CHUNK_SIZE] for _, _, chunk in ranked[:limit]]


def extract_articles(client, chunk, query, apply_chain_rules):
    messages = [
        {
            "role": "system",
            "content": (
                f"{liability_rules(apply_chain_rules)}\n"
                "في هذه المرحلة استخرج فقط المواد والفقرات ذات الصلة من الجزء المرفق "
                "من نظام المرور ولائحته التنفيذية. أعد صياغة النص بعربية فصيحة ولا تنسخ النص المشوه. "
                "إن لم توجد مادة منطبقة فاكتب: لا يوجد."
            ),
        },
        {
            "role": "user",
            "content": (
                "وقائع الحادث:\n"
                f"{(query or '')[:MAX_QUERY_CHARS]}\n\n"
                "جزء من نظام المرور:\n"
                f"{(chunk or '')[:CHUNK_SIZE]}"
            ),
        },
    ]
    try:
        return groq_chat(
            client,
            messages,
            temperature=0,
            max_tokens=700,
            allow_empty=True,
        )
    except Exception:
        return ""


def build_final_prompt(law_excerpts, facts, narrative, apply_chain_rules):
    ratios = " / ".join(APPROVED_RATIOS)
    return f"""{liability_rules(apply_chain_rules)}

المهمة:
حلّل الحادث اعتماداً على وقائع المحقق والمواد المجمّعة حصرياً من نظام المرور السعودي ولائحته التنفيذية.

قواعد ملزمة إضافية:
1) ممنوع الاجتهاد خارج النص النظامي المستخلص.
2) نسب المسؤولية المسموحة فقط: {ratios}، ومجموعها بين الأطراف 100% دائماً.
3) التركيبات المعتمدة مثل: 100%، أو 75% و25%، أو 50% و50%، أو 0% مع تحمل طرف آخر 100%.
4) اذكر رقم المادة والفقرة الفرعية الدقيقة (مثل 50/2/4 أو 60/1) بصياغة عربية فصيحة للنص، دون ذكر صفحات المصدر.
5) إذا نقصت الوقائع، بيّن النقص ولا تخترع مادة أو نسبة.
6) أسلوب رسمي ومباشر بلا رموز Markdown وبلا > أو * أو ---.

صيغة التقرير:
- بيانات المحضر والوقائع
- التكييف النظامي
- المخطئ / المخطئون
- نسب المسؤولية المعتمدة مع سند المادة
- الخلاصة النظامية

المواد المستخرجة من نظام المرور ولائحته التنفيذية:

{law_excerpts}

بيانات المحقق:

{facts}

السرد الحر:
{narrative}
"""


def analyze_accident(law_text, facts, narrative, apply_chain_rules):
    client = groq_client()
    chunks = cached_chunks(law_text)
    if not chunks:
        raise RuntimeError("تعذر تقسيم نص نظام المرور إلى أجزاء.")

    query = f"{facts}\n{narrative}"
    selected = select_chunks(chunks, query)
    extracted = []
    progress = st.progress(0, text="بدء التحليل المجزأ...")
    total = len(selected) + 1

    for index, chunk in enumerate(selected, start=1):
        progress.progress(index / total, text=f"معالجة الجزء {index} من {len(selected)}")
        try:
            excerpt = extract_articles(client, chunk, query, apply_chain_rules) or ""
        except Exception:
            excerpt = ""
        compact = excerpt.strip()
        if compact and not compact.startswith("لا يوجد"):
            extracted.append(compact)
        time.sleep(REQUEST_PAUSE_SEC)

    law_excerpts = "\n\n".join(extracted).strip() or "\n\n".join(selected)
    law_excerpts = law_excerpts[:MAX_EXTRACT_CHARS]

    progress.progress(1.0, text="صياغة التقرير النهائي...")
    messages = [
        {
            "role": "system",
            "content": liability_rules(apply_chain_rules),
        },
        {"role": "user", "content": build_final_prompt(law_excerpts, facts, narrative, apply_chain_rules)},
    ]
    report = groq_chat(client, messages, temperature=0.1, max_tokens=2048)
    progress.empty()
    return clean_report_text(report, strip_chain_terms=not apply_chain_rules)


def collect_party_facts(party_count):
    facts = []
    columns = st.columns(party_count)
    for index, column in enumerate(columns, start=1):
        with column:
            st.markdown(f"**الطرف {index}**")
            role = st.selectbox(
                f"صفة الطرف {index}",
                ["سائق", "راكب", "مشاة", "دراجة", "مركبة ثقيلة", "أخرى"],
                key=f"role_{index}",
            )
            vehicle = st.text_input(f"نوع المركبة {index}", key=f"veh_{index}")
            plate = st.text_input(f"رقم اللوحة {index}", key=f"plate_{index}")
            direction = st.selectbox(
                f"الاتجاه {index}",
                ["شمال", "جنوب", "شرق", "غرب", "غير محدد"],
                key=f"dir_{index}",
            )
            lane = st.selectbox(
                f"المسار {index}",
                ["أيمن", "أوسط", "أيسر", "كتف الطريق", "غير محدد"],
                key=f"lane_{index}",
            )
            move = st.selectbox(f"المناورة {index}", MANEUVERS, key=f"move_{index}")
            light = st.selectbox(f"الإشارة أمام الطرف {index}", SIGNALS, key=f"light_{index}")
            priority = st.selectbox(f"الأولوية {index}", PRIORITIES, key=f"prio_{index}")
            speed = st.selectbox(
                f"السرعة التقديرية {index}",
                ["ضمن الحد", "تجاوز بسيط", "تجاوز كبير", "متوقف", "غير معلوم"],
                key=f"speed_{index}",
            )
            facts.append(
                f"الطرف {index}: الصفة={role}، المركبة={vehicle or 'غير مذكورة'}، "
                f"اللوحة={plate or 'غير مذكورة'}، الاتجاه={direction}، المسار={lane}، "
                f"المناورة={move}، الإشارة={light}، الأولوية={priority}، السرعة={speed}"
            )
    return facts


def build_facts_block(
    report_no,
    investigator_name,
    investigator_id,
    accident_date,
    accident_time,
    city,
    district,
    road_type,
    weather,
    road_status,
    lighting,
    injuries,
    damage,
    analysis_mode,
    cite_articles,
    show_ratios_only,
    party_facts,
    include_sketch_notes,
    sketch_notes,
    include_witnesses,
    witness_notes,
    investigator_notes,
):
    facts = "\n".join(
        [
            f"المحضر: {report_no or 'غير مذكور'}",
            f"المحقق: {investigator_name or 'غير مذكور'} | الرقم: {investigator_id or 'غير مذكور'}",
            f"التاريخ والوقت: {accident_date} {accident_time}",
            f"الموقع: {city or 'غير مذكور'} - {district or 'غير مذكور'}",
            f"نوع الموقع: {road_type}",
            f"الطقس: {weather} | الطريق: {road_status} | الإنارة: {lighting}",
            f"الإصابات: {injuries} | الأضرار: {damage}",
            f"مستوى الصرامة: {analysis_mode}",
            f"إلزام المواد النظامية: {'نعم' if cite_articles else 'لا'}",
            f"قصر النسب المعتمدة: {'نعم' if show_ratios_only else 'لا'}",
            "أطراف الحادث:",
            *party_facts,
        ]
    )
    if include_sketch_notes and sketch_notes.strip():
        facts += f"\nملاحظات الكروكي:\n{sketch_notes.strip()}"
    if include_witnesses and witness_notes.strip():
        facts += f"\nإفادات الشهود:\n{witness_notes.strip()}"
    if investigator_notes.strip():
        facts += f"\nملاحظات المحقق:\n{investigator_notes.strip()}"
    return facts


pages_count, traffic_law_text = load_traffic_law()
api_key, key_error = load_api_key()

st.markdown(
    """
    <div class="hasm-hero">
      <div class="hasm-mark">⬡</div>
      <div>
        <h1>حسم الذكي للحوادث المرورية</h1>
        <p>منصة استدلال نظامي لتحليل المسؤولية المرورية بالذكاء الاصطناعي</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if pages_count > 0 and traffic_law_text:
    st.success("✅ تم ربط النظام بنجاح (مرتبط بنظام المرور السعودي ولائحته التنفيذية)")
elif pages_count > 0:
    st.error("❌ تم العثور على traffic.pdf لكن تعذر استخراج النص منه.")
else:
    st.error("❌ لم يتم العثور على ملف traffic.pdf")

if key_error:
    st.error(f"❌ {key_error}")

with st.sidebar:
    st.header("لوحة تحكم المحقق")
    st.caption("خيارات التحكم المتقدم لبناء محضر التحليل")

    st.subheader("بيانات المحضر")
    investigator_name = st.text_input("اسم المحقق")
    investigator_id = st.text_input("الرقم الوظيفي / العسكري")
    report_no = st.text_input("رقم البلاغ / المحضر")
    accident_date = st.date_input("تاريخ الحادث")
    accident_time = st.time_input("وقت الحادث")
    city = st.text_input("المدينة")
    district = st.text_input("الحي / الشارع")

    st.subheader("ظروف الموقع")
    road_type = st.selectbox(
        "نوع الموقع",
        ["طريق مستقيم", "تقاطع", "دوار", "إشارة ضوئية", "مخرج / مدخل", "موقف / Reverse", "أخرى"],
    )
    weather = st.selectbox("حالة الطقس", ["صحو", "أمطار", "ضباب", "غبار / عاصفة", "أخرى"])
    road_status = st.selectbox("حالة الطريق", ["جاف", "مبلل", "زلِق", "أعمال صيانة", "حفر / عوائق"])
    lighting = st.selectbox("الإنارة", ["نهار", "ليل مضاء", "ليل غير مضاء"])
    injuries = st.selectbox("الإصابات", ["لا توجد", "إصابة بسيطة", "إصابة بليغة", "وفاة"])
    damage = st.selectbox("الأضرار المادية", ["بسيطة", "متوسطة", "جسيمة"])

    st.subheader("ضوابط التحليل")
    analysis_mode = st.selectbox("مستوى الصرامة", ["صارم نظامي", "مبدئي للمحقق", "مراجعة نهائية"])
    cite_articles = st.checkbox("إلزام جلب رقم المادة ومقتطفها من نظام المرور ولائحته التنفيذية", value=True)
    show_ratios_only = st.checkbox("قصر النسب على 0% / 25% / 50% / 75% / 100%", value=True)
    include_sketch_notes = st.checkbox("إدخال ملاحظات الكروكي ضمن التحليل", value=True)
    include_witnesses = st.checkbox("إدخال إفادة الشهود ضمن التحليل", value=False)

st.markdown("---")
st.subheader("أطراف الحادث وخيارات المناورة")
party_count = st.radio("عدد الأطراف", [2, 3, 4], horizontal=True, index=0)
party_facts = collect_party_facts(party_count)

st.markdown("---")
left, right = st.columns(2)
with left:
    sketch_notes = st.text_area("ملاحظات الكروكي / الرسم الميداني", height=120)
with right:
    witness_notes = st.text_area("إفادات الشهود", height=120)

accident_desc = st.text_area(
    "السرد الحر لتفاصيل الحادث (المركبات، الاتجاهات، الإشارات، التسلسل الزمني):",
    height=160,
)
investigator_notes = st.text_area("ملاحظات المحقق الخاصة", height=90)

if st.button("🔍 بدء التحليل النظامي"):
    if not accident_desc.strip():
        st.warning("الرجاء كتابة تفاصيل الحادث أولاً.")
    elif key_error:
        st.warning(f"لا يمكن بدء التحليل: {key_error}")
    elif not traffic_law_text:
        st.warning("لا يمكن بدء التحليل دون نص نظام المرور المستخرج من traffic.pdf.")
    else:
        facts = build_facts_block(
            report_no,
            investigator_name,
            investigator_id,
            accident_date,
            accident_time,
            city,
            district,
            road_type,
            weather,
            road_status,
            lighting,
            injuries,
            damage,
            analysis_mode,
            cite_articles,
            show_ratios_only,
            party_facts,
            include_sketch_notes,
            sketch_notes,
            include_witnesses,
            witness_notes,
            investigator_notes,
        )
        apply_chain_rules = is_chain_collision(facts, accident_desc, party_count)
        try:
            report = analyze_accident(traffic_law_text, facts, accident_desc, apply_chain_rules)
            st.session_state["official_report"] = report
            st.session_state["official_facts"] = clean_report_text(facts)
            st.session_state["apply_chain_rules"] = apply_chain_rules
        except Exception as error:
            st.error(f"فشل التحليل دون إيقاف التطبيق. السبب الحقيقي: {describe_error(error)}")

if st.session_state.get("official_report"):
    cleaned_report = clean_report_text(
        st.session_state["official_report"],
        strip_chain_terms=not st.session_state.get("apply_chain_rules", False),
    )
    cleaned_facts = st.session_state.get("official_facts", "")
    render_official_report(cleaned_facts, cleaned_report)
    print_col, save_col = st.columns(2)
    with print_col:
        components.html(
            """
            <style>
              html, body { margin: 0; padding: 0; background: transparent; }
              button {
                display: block;
                width: 100%;
                height: 48px;
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                border: 1px solid #0b2e47;
                border-radius: 8px;
                background: #0f3d5e;
                color: #ffffff;
                font-family: Tahoma, Arial, sans-serif;
              }
            </style>
            <button onclick="window.parent.print();">🖨️ طباعة التقرير الرسمي</button>
            """,
            height=48,
            scrolling=False,
        )
    with save_col:
        st.download_button(
            "💾 حفظ وتحميل التقرير",
            data=report_download_html(cleaned_facts, cleaned_report),
            file_name="hasm-official-report.html",
            mime="text/html",
            use_container_width=True,
        )
