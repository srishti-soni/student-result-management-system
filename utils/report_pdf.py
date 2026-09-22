import re
from datetime import datetime
import pandas as pd
from fpdf import FPDF

# Emoji / non-latin characters can't be rendered by the built-in Helvetica font.
# Strip them before writing any cell so fpdf2 doesn't raise UnicodeEncodeError.
_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FFFF"   # misc symbols, pictographs, emoticons, transport
    "\U00002702-\U000027B0"   # dingbats
    "\U000024C2-\U0001F251"   # enclosed chars
    "\u2600-\u26FF"           # misc symbols
    "\u2700-\u27BF"           # dingbats block
    "\u2000-\u206F"           # general punctuation (arrows etc.)
    "]+",
    flags=re.UNICODE,
)


def _safe(text: str) -> str:
    """Remove emoji/non-latin characters that Helvetica cannot encode."""
    return _EMOJI_RE.sub("", str(text)).strip()

HEADER_COLOUR = (79, 70, 229)   # Indigo
ROW_ALT_COLOUR = (243, 244, 246)  # Light grey
TEXT_COLOUR = (31, 41, 55)


class _ReportPDF(FPDF):
    def __init__(self, title: str):
        super().__init__(orientation="L", unit="mm", format="A4")
        self._title = title

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*HEADER_COLOUR)
        self.cell(0, 10, self._title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(107, 114, 128)
        self.cell(
            0, 6,
            f"Generated: {datetime.now().strftime('%d %b %Y  %H:%M')}",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(156, 163, 175)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")


def generate_pdf(title: str, df: pd.DataFrame) -> bytes:
    """Return PDF bytes for a DataFrame — suitable for st.download_button."""
    pdf = _ReportPDF(title)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    columns = list(df.columns)
    num_cols = len(columns)
    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / num_cols

    # ── Header row ──────────────────────────────────────────────────────────
    pdf.set_fill_color(*HEADER_COLOUR)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 8)
    for col in columns:
        pdf.cell(col_width, 8, _safe(col), border=0, fill=True, align="C")
    pdf.ln()

    # ── Data rows ───────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "", 8)
    for i, (_, row) in enumerate(df.iterrows()):
        if i % 2 == 0:
            pdf.set_fill_color(*ROW_ALT_COLOUR)
            fill = True
        else:
            fill = False
        pdf.set_text_color(*TEXT_COLOUR)
        for col in columns:
            pdf.cell(col_width, 7, _safe(row[col]), border=0, fill=fill, align="C")
        pdf.ln()

    return bytes(pdf.output())
