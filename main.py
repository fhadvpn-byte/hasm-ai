import html
import re
import time

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
      .official-report {
        line-height: 1.85;
        text-align: right;
        direction: rtl;
      }
      .official-report table {
        width: 100%;
        border-collapse: collapse;
        margin: 0.8rem 0;
      }
      .official-report table, .official-report th, .official-report td {
        border: 1px solid rgba(160, 180, 200, 0.35);
        padding: 8px;
      }
      @media print {
        header, footer, [data-testid="stHeader"], [data-testid="stToolbar"],
        [data-testid="stDecoration"], [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"], .hasm-hero,
        .no-print, .stDownloadButton, [data-testid="stDownloadButton"],
        .stButton, [data-testid="stChatInput"], iframe,
        [data-testid="stTextInput"], [data-testid="stTextArea"],
        [data-testid="stSelectbox"], [data-testid="stRadio"],
        [data-testid="stCheckbox"], [data-testid="stDateInput"],
        [data-testid="stTimeInput"], [data-testid="stAlert"],
        [data-testid="stNotification"], [data-testid="stWidgetLabel"] {
          display: none !important;
        }
        .block-container {
          padding: 0 !important;
          max-width: 100% !important;
        }
        .official-report, .print-case-facts {
          display: block !important;
          color: #000 !important;
        }
      }
    </style>
    """,
    unsafe_allow_html=True,
)

GROQ_MODEL = "openai/gpt-oss-120b"
API_KEY_NAME = "GROQ_API_KEY"
APPROVED_RATIOS = ("100%", "75%", "50%", "25%")
PDF_PATH = "traffic.pdf"
CHUNK_SIZE = 2200
CHUNK_OVERLAP = 180
MAX_MAP_CHUNKS = 6
MAX_EXTRACT_CHARS = 8000
MAX_QUERY_CHARS = 1500
REQUEST_PAUSE_SEC = 1.4
MAX_RETRIES = 4
LAW_KEYWORDS = (
    "حادث", "مسؤولية", "خطأ", "تقاطع", "إشارة", "تجاوز", "أولوية", "مسار",
    "انعطف", "انعطاف", "سرعة", "مشاة", "وقوف", "متوقف", "رجوع", "دوار",
    "يسار", "يمين", "حمراء", "خضراء", "كتف", "مخرج", "مدخل", "عكس",
    "مركبة", "سائق", "تصادم", "اصطدام", "مادة",
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


def clean_report_text(text):
    cleaned = str(text or "")
    cleaned = re.sub(r"(?i)<br\s*/?>", "، ", cleaned)
    cleaned = cleaned.replace("**", "")
    cleaned = re.sub(r"(?i)traffic\.pdf", "نظام المرور ولائحته التنفيذية", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def report_download_html(facts, report):
    facts_html = html.escape(clean_report_text(facts)).replace("\n", "<br>\n")
    report_html = html.escape(clean_report_text(report)).replace("\n", "<br>\n")
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <title>التقرير الرسمي للحادث</title>
  <style>
    body {{ font-family: Tahoma, Arial, sans-serif; direction: rtl; text-align: right; padding: 28px; line-height: 1.8; color: #111; }}
    h1, h2 {{ margin-bottom: 0.4rem; }}
    .box {{ border: 1px solid #ccc; padding: 16px; margin-bottom: 18px; }}
    @media print {{ body {{ padding: 0; }} }}
  </style>
</head>
<body>
  <h1>حسم الذكي للحوادث المرورية</h1>
  <h2>بيانات المحضر</h2>
  <div class="box">{facts_html}</div>
  <h2>التقرير النظامي</h2>
  <div class="box">{report_html}</div>
</body>
</html>
"""


@st.cache_data
def load_traffic_law():
    try:
        with open(PDF_PATH, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(part.strip() for part in pages if part and part.strip())
            return len(reader.pages), text
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


def extract_articles(client, chunk, query):
    messages = [
        {
            "role": "system",
            "content": (
                "استخرج فقط المواد النظامية ذات الصلة بالحادث من الجزء المرفق. "
                "إن لم توجد مادة منطبقة فاكتب: لا يوجد. لا تحدد نسب المسؤولية هنا."
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
            max_tokens=2048,
            allow_empty=True,
        )
    except Exception:
        return ""


def build_final_prompt(law_excerpts, facts, narrative):
    ratios = " / ".join(APPROVED_RATIOS)
    return f"""أنت خبير تحقيق حوادث مرورية وفق نظام المرور السعودي المعتمد في المواد المستخرجة فقط.

المهمة:
حلّل الحادث اعتماداً على وقائع المحقق والمواد المجمّعة من نظام المرور ولائحته التنفيذية، ثم حدد نسب المسؤولية النظامية المعتمدة فقط.

قواعد ملزمة:
1) اعتمد حصرياً على المواد المرفقة. ممنوع الاجتهاد خارج النص.
2) نسب المسؤولية المسموحة فقط: {ratios}.
3) التركيبات المعتمدة مثل: 100% لطرف، أو 75% و25%، أو 50% و50%.
4) اذكر رقم المادة ومقتطفها لكل نسبة.
5) إذا نقصت الوقائع، بيّن النقص ولا تخترع مادة أو نسبة.
6) أسلوب رسمي ومباشر.

صيغة التقرير:
- بيانات المحضر والوقائع
- التكييف النظامي
- المخطئ / المخطئون
- نسب المسؤولية المعتمدة مع سند المادة
- الخلاصة النظامية

المواد المستخرجة من نظام المرور ولائحته التنفيذية:
---
{law_excerpts}
---

بيانات المحقق:
---
{facts}
---

السرد الحر:
{narrative}
"""


def analyze_accident(law_text, facts, narrative):
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
            excerpt = extract_articles(client, chunk, query) or ""
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
            "content": (
                "أنت خبير تحقيق حوادث مرورية. "
                f"التزم بالمواد المرفقة وبالنسب {', '.join(APPROVED_RATIOS)} فقط. "
                "لا تذكر أسماء ملفات أو نماذج برمجية في التقرير."
            ),
        },
        {"role": "user", "content": build_final_prompt(law_excerpts, facts, narrative)},
    ]
    report = groq_chat(client, messages, temperature=0.1, max_tokens=2048)
    progress.empty()
    return report


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
    st.success(f"✅ تم ربط النظام بنجاح (تمت قراءة {pages_count} صفحة من نظام المرور)")
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
    show_ratios_only = st.checkbox("قصر النسب على 100% / 75% / 50% / 25%", value=True)
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
        try:
            report = analyze_accident(traffic_law_text, facts, accident_desc)
            st.session_state["official_report"] = clean_report_text(report)
            st.session_state["official_facts"] = clean_report_text(facts)
        except Exception as error:
            st.error(f"فشل التحليل دون إيقاف التطبيق. السبب الحقيقي: {describe_error(error)}")

if st.session_state.get("official_report"):
    cleaned_report = st.session_state["official_report"]
    cleaned_facts = st.session_state.get("official_facts", "")
    st.markdown("### التقرير النظامي للحادث")
    st.markdown(
        f'<div class="print-case-facts"><h4>بيانات المحضر</h4><p>{html.escape(cleaned_facts).replace(chr(10), "<br>")}</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div id="official-report" class="official-report">{cleaned_report.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )
    print_col, save_col = st.columns(2)
    with print_col:
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        components.html(
            """
            <button onclick="window.parent.print();"
                    style="width:100%;padding:11px 14px;font-size:16px;font-weight:700;cursor:pointer;border-radius:8px;">
              🖨️ طباعة التقرير الرسمي
            </button>
            """,
            height=58,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with save_col:
        st.download_button(
            "💾 حفظ وتحميل التقرير",
            data=report_download_html(cleaned_facts, cleaned_report),
            file_name="hasm-official-report.html",
            mime="text/html",
            use_container_width=True,
        )
