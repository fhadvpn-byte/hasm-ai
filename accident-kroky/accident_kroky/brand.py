import streamlit as st
from PIL import Image

from accident_kroky.paths import LOGO_PATH


def page_icon() -> Image.Image:
    if not LOGO_PATH.is_file():
        raise FileNotFoundError(f"شعار بينة غير موجود: {LOGO_PATH.name}")
    return Image.open(LOGO_PATH)


def render_brand() -> None:
    logo = str(LOGO_PATH)
    mark, text = st.columns([1, 6], vertical_alignment="center")
    with mark:
        st.image(logo, width=96, alt="شعار بينة")
    with text:
        st.header("بينة")
        st.caption("كروكي الحوادث المرورية")
