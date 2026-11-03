import io

import pandas as pd
from fpdf import FPDF
from PIL import Image

from accident_kroky.paths import LOGO_PATH, arabic_font
from accident_kroky.scene import sketch_bytes
from accident_kroky.tables import MARK_LOGICAL, PARTY_LOGICAL

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:  # pragma: no cover - يظهر عند فتح صفحة التقرير
    arabic_reshaper = None
    get_display = None


def _shape(value) -> str:
    if arabic_reshaper is None or get_display is None:
        raise RuntimeError("ثبّت arabic-reshaper و python-bidi لبناء تقرير PDF العربي.")
    text = "" if value is None else str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    return get_display(arabic_reshaper.reshape(text))


def _cell(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    return text or "—"


def _lines(value: str, width: int = 78) -> list[str]:
    words = _cell(value).split()
    if not words or words == ["—"]:
        return []
    rows: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if len(trial) > width and current:
            rows.append(current)
            current = word
        else:
            current = trial
    if current:
        rows.append(current)
    return rows


class _Report(FPDF):
    def footer(self):
        self.set_y(-12)
        self.set_font("Bayyinah", size=9)
        self.set_text_color(80, 96, 112)
        self.cell(0, 6, _shape(f"بينة — صفحة {self.page_no()}"), align="C")


def _rtl_row(pdf: FPDF, y: float, height: float, widths: list[float], texts: list[str], header: bool = False) -> float:
    if header:
        pdf.set_fill_color(8, 47, 73)
        pdf.set_text_color(255, 255, 255)
    else:
        pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(15, 28, 42)
    x = pdf.w - pdf.r_margin
    for width, text in zip(widths, texts):
        x -= width
        pdf.set_xy(x, y)
        pdf.cell(width, height, _shape(text), border=1, align="R", fill=header)
    return y + height


def _room(pdf: FPDF, y: float, needed: float) -> float:
    if y + needed <= pdf.h - pdf.b_margin:
        return y
    pdf.add_page()
    return pdf.t_margin


def build_report_pdf(case: dict, items: list[dict], snapshot: str) -> bytes:
    pdf = _Report(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_font("Bayyinah", "", str(arabic_font()))
    pdf.add_page()
    usable = pdf.w - pdf.l_margin - pdf.r_margin

    if LOGO_PATH.is_file():
        pdf.image(str(LOGO_PATH), x=pdf.w - pdf.r_margin - 22, y=10, h=20)
    pdf.set_xy(pdf.l_margin, 12)
    pdf.set_font("Bayyinah", size=18)
    pdf.set_text_color(8, 47, 73)
    pdf.cell(usable - 26, 10, _shape("بينة"), align="R")
    pdf.set_xy(pdf.l_margin, 22)
    pdf.set_font("Bayyinah", size=12)
    pdf.set_text_color(14, 116, 144)
    pdf.cell(usable - 26, 8, _shape("تقرير كروكي حادث مروري"), align="R")

    y = 36.0
    pdf.set_font("Bayyinah", size=11)
    meta = [
        ("رقم البلاغ", case.get("report_no", "—")),
        ("التاريخ والوقت", case.get("when", "—")),
        ("المحقق", f"{case.get('investigator', '—')} | {case.get('rank', '—')}"),
        ("المدينة", case.get("city", "—")),
        ("الموقع", case.get("site", "—")),
        ("الظروف", f"{case.get('weather', '—')} | {case.get('road', '—')} | {case.get('lighting', '—')}"),
    ]
    label_w = 38
    value_w = usable - label_w
    for label, value in meta:
        y = _room(pdf, y, 8)
        y = _rtl_row(pdf, y, 8, [label_w, value_w], [label, _cell(value)])

    y += 4
    y = _room(pdf, y, 16)
    pdf.set_xy(pdf.l_margin, y)
    pdf.set_font("Bayyinah", size=13)
    pdf.set_text_color(8, 47, 73)
    pdf.cell(usable, 8, _shape("أطراف الحادث"), align="R")
    y = pdf.get_y() + 9
    pdf.set_font("Bayyinah", size=9)
    fixed = [16, 36, 32, 32, 28]
    party_widths = [fixed[0], fixed[1], fixed[2], fixed[3], fixed[4], usable - sum(fixed)]
    y = _rtl_row(pdf, y, 8, party_widths, PARTY_LOGICAL, header=True)
    parties = case.get("parties")
    records = parties.to_dict("records") if isinstance(parties, pd.DataFrame) else []
    for row in records:
        y = _room(pdf, y, 8)
        values = [_cell(row.get(column)) for column in PARTY_LOGICAL]
        y = _rtl_row(pdf, y, 8, party_widths, values)

    story = _lines(case.get("narrative", ""))
    if story:
        y += 4
        y = _room(pdf, y, 16)
        pdf.set_xy(pdf.l_margin, y)
        pdf.set_font("Bayyinah", size=13)
        pdf.set_text_color(8, 47, 73)
        pdf.cell(usable, 8, _shape("وصف الواقعة"), align="R")
        y = pdf.get_y() + 9
        pdf.set_font("Bayyinah", size=11)
        pdf.set_text_color(15, 28, 42)
        for line in story:
            y = _room(pdf, y, 7)
            pdf.set_xy(pdf.l_margin, y)
            pdf.cell(usable, 7, _shape(line), align="R")
            y += 7

    y += 6
    y = _room(pdf, y, 24)
    pdf.set_xy(pdf.l_margin, y)
    pdf.set_font("Bayyinah", size=13)
    pdf.set_text_color(8, 47, 73)
    pdf.cell(usable, 8, _shape("الكروكي"), align="R")
    y = pdf.get_y() + 10
    image = Image.open(io.BytesIO(sketch_bytes(items, snapshot))).convert("RGB")
    sketch_h = usable * image.height / image.width
    y = _room(pdf, y, sketch_h)
    pdf.image(image, x=pdf.l_margin, y=y, w=usable, h=sketch_h)
    y += sketch_h + 4

    if items:
        y = _room(pdf, y, 16)
        pdf.set_font("Bayyinah", size=13)
        pdf.set_text_color(8, 47, 73)
        pdf.set_xy(pdf.l_margin, y)
        pdf.cell(usable, 8, _shape("العناصر المرسومة"), align="R")
        y = pdf.get_y() + 9
        pdf.set_font("Bayyinah", size=10)
        mark_w = usable / len(MARK_LOGICAL)
        y = _rtl_row(pdf, y, 8, [mark_w] * len(MARK_LOGICAL), MARK_LOGICAL, header=True)
        for item_row in _mark_rows(items):
            y = _room(pdf, y, 8)
            y = _rtl_row(pdf, y, 8, [mark_w] * len(MARK_LOGICAL), item_row)

    y = _room(pdf, y + 8, 12)
    pdf.set_font("Bayyinah", size=11)
    pdf.set_text_color(15, 28, 42)
    pdf.set_xy(pdf.l_margin, y)
    pdf.cell(
        usable,
        8,
        _shape("المحقق: ____________________          الاعتماد: ____________________"),
        align="R",
    )

    return bytes(pdf.output())


def _mark_rows(items: list[dict]) -> list[list[str]]:
    from accident_kroky.tables import KIND_LABELS, normalize_items

    rows = []
    for item in normalize_items(items):
        kind = item["kind"]
        token = str(item["n"]) if kind == "vehicle" else KIND_LABELS[kind]
        rows.append([token, KIND_LABELS[kind], f"{item['x'] * 100:.0f}%", f"{item['y'] * 100:.0f}%"])
    return rows
