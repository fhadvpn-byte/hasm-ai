import streamlit as st

from accident_kroky.brand import render_brand
from accident_kroky.pdf_builder import build_report_pdf
from accident_kroky.state import SAVED_MARKS_KEY, SAVED_SNAPSHOT_KEY, case_from_state
from accident_kroky.tables import PARTY_LOGICAL, marks_frame, normalize_items, rtl_frame

render_brand()
st.subheader("تقرير PDF")
st.caption("صفحة مستقلة عن المحرر. تجمع بيانات الجلسة الحالية في ملف PDF جاهز للتنزيل.")

case = case_from_state()
items = normalize_items(st.session_state.get(SAVED_MARKS_KEY) or [])
snapshot = st.session_state.get(SAVED_SNAPSHOT_KEY) or ""

st.dataframe(
    rtl_frame(case["parties"], PARTY_LOGICAL),
    hide_index=True,
    width="stretch",
    alt="جدول أطراف الحادث من اليمين إلى اليسار",
)
st.dataframe(
    marks_frame(items),
    hide_index=True,
    width="stretch",
    alt="جدول عناصر الكروكي من اليمين إلى اليسار",
)

try:
    report = build_report_pdf(case, items, snapshot)
except Exception as exc:
    st.error(f"تعذر بناء التقرير: {exc}")
else:
    stamp = case["report_no"] if case["report_no"] != "—" else "kroky"
    st.download_button(
        "تنزيل تقرير PDF",
        data=report,
        file_name=f"bayyinah-{stamp}.pdf",
        mime="application/pdf",
        icon=":material/download:",
        width="stretch",
    )
    try:
        import streamlit_pdf  # noqa: F401
    except ImportError:
        pass
    else:
        st.pdf(report, height=760, alt="معاينة تقرير بينة")
