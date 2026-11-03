import pandas as pd

PARTY_LOGICAL = ["الرقم", "الاسم", "رقم اللوحة", "نوع المركبة", "الاتجاه", "المناورة"]
MARK_LOGICAL = ["الرمز", "النوع", "الأفقي", "الرأسي"]

DIRECTIONS = ["شمال", "جنوب", "شرق", "غرب", "شمال شرقي", "شمال غربي", "جنوب شرقي", "جنوب غربي"]
MANEUVERS = [
    "سير مستقيم",
    "انعطاف يمين",
    "انعطاف يسار",
    "دوران للخلف",
    "تغيير مسار",
    "توقف",
    "رجوع للخلف",
    "تجاوز",
]

KIND_LABELS = {
    "vehicle": "مركبة",
    "tree": "شجر",
    "pole": "عمود",
    "hole": "حفرة",
}


def rtl_frame(frame: pd.DataFrame, logical_columns: list[str]) -> pd.DataFrame:
    """يعكس الأعمدة حتى يظهر أول عمود منطقي في أقصى اليمين."""
    present = [column for column in logical_columns if column in frame.columns]
    if not present:
        return frame
    return frame.loc[:, list(reversed(present))]


def default_parties() -> pd.DataFrame:
    rows = [
        {
            "الرقم": number,
            "الاسم": "",
            "رقم اللوحة": "",
            "نوع المركبة": "",
            "الاتجاه": "شمال",
            "المناورة": "سير مستقيم",
        }
        for number in range(1, 11)
    ]
    return rtl_frame(pd.DataFrame(rows, columns=PARTY_LOGICAL), PARTY_LOGICAL)


def logical_parties(frame: pd.DataFrame | None) -> pd.DataFrame:
    if frame is None or not isinstance(frame, pd.DataFrame) or frame.empty:
        source = default_parties()
    else:
        source = frame.copy()
    for column in PARTY_LOGICAL:
        if column not in source.columns:
            source[column] = ""
    ordered = source.loc[:, PARTY_LOGICAL].reset_index(drop=True)
    if len(ordered) < 10:
        extra = logical_parties(default_parties()).iloc[len(ordered) :]
        ordered = pd.concat([ordered, extra], ignore_index=True)
    return ordered.head(10)


def normalize_items(raw) -> list[dict]:
    if not isinstance(raw, list):
        return []
    items = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        kind = entry.get("kind")
        if kind not in KIND_LABELS:
            continue
        try:
            x = min(1.0, max(0.0, float(entry.get("x", 0))))
            y = min(1.0, max(0.0, float(entry.get("y", 0))))
            number = int(entry.get("n") or 0)
        except (TypeError, ValueError):
            continue
        if kind == "vehicle" and not 1 <= number <= 10:
            continue
        items.append(
            {
                "id": str(entry.get("id") or f"{kind}-{len(items) + 1}"),
                "kind": kind,
                "n": number,
                "x": x,
                "y": y,
            }
        )
    vehicles = sorted((item for item in items if item["kind"] == "vehicle"), key=lambda item: item["n"])
    others = [item for item in items if item["kind"] != "vehicle"]
    return vehicles + others


def marks_frame(items: list[dict]) -> pd.DataFrame:
    rows = []
    for item in normalize_items(items):
        kind = item["kind"]
        token = str(item["n"]) if kind == "vehicle" else KIND_LABELS[kind]
        rows.append(
            {
                "الرمز": token,
                "النوع": KIND_LABELS[kind],
                "الأفقي": f"{item['x'] * 100:.0f}%",
                "الرأسي": f"{item['y'] * 100:.0f}%",
            }
        )
    frame = pd.DataFrame(rows, columns=MARK_LOGICAL)
    return rtl_frame(frame, MARK_LOGICAL)
