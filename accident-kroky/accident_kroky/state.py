import streamlit as st

from accident_kroky.tables import logical_parties, normalize_items

CANVAS_KEY = "kroky_board"
PARTIES_KEY = "parties_editor"
SAVED_MARKS_KEY = "kroky_marks_saved"
SAVED_SNAPSHOT_KEY = "kroky_snapshot_saved"

TOOL_LABELS = {str(number): f"مركبة {number}" for number in range(1, 11)}
TOOL_LABELS.update(
    {
        "tree": "شجر",
        "pole": "عمود",
        "hole": "حفرة",
        "select": "تحريك",
        "erase": "مسح عنصر",
    }
)


def init_state() -> None:
    st.session_state.setdefault("kroky_tool", "1")


def clear_board() -> None:
    st.session_state[CANVAS_KEY] = {"marks": [], "snapshot": ""}
    st.session_state[SAVED_MARKS_KEY] = []
    st.session_state[SAVED_SNAPSHOT_KEY] = ""


def set_tool(name: str) -> None:
    st.session_state.kroky_tool = name


def _field(state, key: str):
    if isinstance(state, dict) and key in state:
        return state[key]
    return None


def board_payload(result=None) -> tuple[list[dict], str]:
    stored = st.session_state.get(CANVAS_KEY, {})
    raw_items = _field(result, "marks")
    snapshot = _field(result, "snapshot")
    if raw_items is None:
        raw_items = _field(stored, "marks")
    if snapshot is None:
        snapshot = _field(stored, "snapshot")
    if raw_items is None:
        raw_items = st.session_state.get(SAVED_MARKS_KEY) or []
        snapshot = snapshot or st.session_state.get(SAVED_SNAPSHOT_KEY) or ""
        return normalize_items(raw_items), snapshot or ""
    marks = normalize_items(raw_items)
    st.session_state[SAVED_MARKS_KEY] = marks
    if snapshot:
        st.session_state[SAVED_SNAPSHOT_KEY] = snapshot
    return marks, snapshot or ""


def case_from_state() -> dict:
    moment = st.session_state.get("case_date")
    clock = st.session_state.get("case_time")
    when = "—"
    if hasattr(moment, "isoformat") and hasattr(clock, "strftime"):
        when = f"{moment.isoformat()} {clock.strftime('%H:%M')}"
    elif hasattr(moment, "isoformat"):
        when = moment.isoformat()

    def text(key: str) -> str:
        value = st.session_state.get(key, "")
        cleaned = "" if value is None else str(value).strip()
        return cleaned or "—"

    return {
        "report_no": text("case_report_no"),
        "investigator": text("case_investigator"),
        "rank": text("case_rank"),
        "city": text("case_city"),
        "site": text("case_site"),
        "weather": text("case_weather"),
        "road": text("case_road"),
        "lighting": text("case_lighting"),
        "when": when,
        "narrative": st.session_state.get("case_narrative") or "",
        "parties": logical_parties(st.session_state.get(PARTIES_KEY)),
    }
