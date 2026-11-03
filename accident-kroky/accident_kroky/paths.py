from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT / "bayyinah_logo.jpg"

FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\tahoma.ttf"),
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\segoeui.ttf"),
)


def arabic_font() -> Path:
    for path in FONT_CANDIDATES:
        if path.is_file():
            return path
    raise FileNotFoundError("لم يُعثر على خط عربي لبناء ملف PDF.")
