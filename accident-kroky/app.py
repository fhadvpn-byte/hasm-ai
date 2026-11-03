import streamlit as st

from accident_kroky.brand import page_icon, render_brand
from accident_kroky.canvas import kroky_board
from accident_kroky.paths import LOGO_PATH
from accident_kroky.state import (
    CANVAS_KEY,
    PARTIES_KEY,
    TOOL_LABELS,
    board_payload,
    clear_board,
    init_state,
    set_tool,
)
from accident_kroky.tables import DIRECTIONS, MANEUVERS, default_parties, marks_frame

st.set_page_config(
    page_title="بينة",
    page_icon=page_icon(),
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_state()
st.logo(str(LOGO_PATH), icon_image=str(LOGO_PATH), size="large")

SITES = ["طريق مستقيم", "تقاطع", "دوار", "منحنى", "كتف الطريق"]
WEATHER = ["صحو", "ممطر", "ضباب", "غبار"]
ROADS = ["جاف", "مبتل", "غير معبد"]
LIGHTS = ["نهار", "ليل بإنارة", "ليل بلا إنارة"]


def render_kroky():
    render_brand()

    with st.container(border=True):
        st.subheader("بيانات المحضر")
        top = list(reversed(st.columns(4)))
        with top[0]:
            st.text_input("رقم البلاغ", key="case_report_no", placeholder="رقم البلاغ")
        with top[1]:
            st.text_input("اسم المحقق", key="case_investigator", placeholder="اسم المحقق")
        with top[2]:
            st.text_input("الرتبة", key="case_rank", placeholder="الرتبة")
        with top[3]:
            st.text_input("المدينة", key="case_city", placeholder="المدينة")
        bottom = list(reversed(st.columns(4)))
        with bottom[0]:
            st.selectbox("نوع الموقع", SITES, key="case_site")
        with bottom[1]:
            st.selectbox("الطقس", WEATHER, key="case_weather")
        with bottom[2]:
            st.selectbox("حالة الطريق", ROADS, key="case_road")
        with bottom[3]:
            st.selectbox("الإنارة", LIGHTS, key="case_lighting")
        when_right, when_left = list(reversed(st.columns(2)))
        with when_right:
            st.date_input("التاريخ", key="case_date")
        with when_left:
            st.time_input("الوقت", key="case_time")
        st.text_area("وصف الواقعة", key="case_narrative", height=90, placeholder="صف الحادث باختصار")

    with st.container(border=True):
        st.subheader("أطراف الحادث")
        st.caption("عشرة أطراف مرقمة من 1 إلى 10. أول عمود يظهر في أقصى اليمين.")
        st.data_editor(
            default_parties(),
            key=PARTIES_KEY,
            hide_index=True,
            num_rows="fixed",
            width="stretch",
            alt="جدول أطراف الحادث من اليمين إلى اليسار",
            column_config={
                "الرقم": st.column_config.NumberColumn("الرقم", min_value=1, max_value=10, step=1, disabled=True, width="small"),
                "الاسم": st.column_config.TextColumn("الاسم"),
                "رقم اللوحة": st.column_config.TextColumn("رقم اللوحة"),
                "نوع المركبة": st.column_config.TextColumn("نوع المركبة"),
                "الاتجاه": st.column_config.SelectboxColumn("الاتجاه", options=DIRECTIONS, required=True),
                "المناورة": st.column_config.SelectboxColumn("المناورة", options=MANEUVERS, required=True),
            },
        )

    with st.container(border=True):
        st.subheader("لوحة الكروكي")
        st.caption("اختر رقماً من 1 إلى 10 أو رمزاً، ثم انقر داخل الطريق. الرقم نفسه ينتقل إذا وُضع مرة أخرى.")
        numbers = st.columns(10)
        for index, column in enumerate(numbers, start=1):
            tool = str(index)
            with column:
                st.button(
                    tool,
                    key=f"tool_number_{tool}",
                    type="primary" if st.session_state.kroky_tool == tool else "secondary",
                    width="stretch",
                    on_click=set_tool,
                    args=(tool,),
                )
        symbols = st.columns(5)
        symbol_buttons = [
            ("tree", "شجر", ":material/park:"),
            ("pole", "عمود", ":material/signpost:"),
            ("hole", "حفرة", ":material/radio_button_unchecked:"),
            ("select", "تحريك", ":material/open_with:"),
            ("erase", "مسح عنصر", ":material/backspace:"),
        ]
        for column, (tool, label, icon) in zip(symbols, symbol_buttons):
            with column:
                st.button(
                    label,
                    key=f"tool_{tool}",
                    icon=icon,
                    type="primary" if st.session_state.kroky_tool == tool else "secondary",
                    width="stretch",
                    on_click=set_tool,
                    args=(tool,),
                )
        st.button("مسح اللوحة", icon=":material/delete_sweep:", on_click=clear_board)
        st.caption(f"الأداة الحالية: {TOOL_LABELS.get(st.session_state.kroky_tool, '')}")

        stored = st.session_state.get(CANVAS_KEY, {})
        current_marks = stored.get("marks", []) if isinstance(stored, dict) else []
        result = kroky_board(
            marks=current_marks,
            tool=st.session_state.kroky_tool,
            key=CANVAS_KEY,
        )
        items, _snapshot = board_payload(result)

    with st.container(border=True):
        st.subheader("العناصر المرسومة")
        st.caption("الجدول معكوس ليُقرأ من اليمين إلى اليسار.")
        st.dataframe(
            marks_frame(items),
            hide_index=True,
            width="stretch",
            alt="جدول عناصر الكروكي من اليمين إلى اليسار",
        )


page = st.navigation(
    [
        st.Page(render_kroky, title="محرر الكروكي", icon=":material/edit_road:", default=True),
        st.Page("app_pages/pdf_report.py", title="تقرير PDF", icon=":material/picture_as_pdf:"),
    ],
    position="top",
)
page.run()
