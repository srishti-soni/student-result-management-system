import os
import streamlit as st

_CSS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")

GRADE_COLOURS: dict[str, str] = {
    "A": "grade-A",
    "B": "grade-B",
    "C": "grade-C",
    "D": "grade-D",
    "E": "grade-E",
    "F": "grade-F",
}


def inject_css() -> None:
    """Load and inject the custom stylesheet into the Streamlit page."""
    with open(os.path.abspath(_CSS_PATH), "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "📌") -> None:
    """Render a full-width gradient hero header."""
    st.markdown(
        f"""
        <div class="srms-page-header">
            <div class="icon">{icon}</div>
            <div>
                <h1>{title}</h1>
                {"<p>" + subtitle + "</p>" if subtitle else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def grade_badge(grade: str) -> str:
    """Return an HTML badge string for a grade letter."""
    css_class = GRADE_COLOURS.get(grade, "grade-F")
    return f'<span class="grade-badge {css_class}">{grade}</span>'


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    """Thin wrapper around st.metric — styling is handled by CSS."""
    st.metric(label=label, value=value, delta=delta)
