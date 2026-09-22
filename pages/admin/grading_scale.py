import streamlit as st
from models.grading import get_grading_scale, upsert_grade_band
from utils.ui import page_header, inject_css

GRADE_COLOURS = {
    "A": "#16a34a", "B": "#2563eb", "C": "#7c3aed",
    "D": "#d97706", "E": "#ea580c", "F": "#dc2626",
}


def render():
    inject_css()
    page_header("Grading Scale", "Configure grade thresholds — changes apply immediately to all reports", "📊")

    scale = get_grading_scale()

    st.subheader("Current Grading Scale")
    if scale:
        cols = st.columns([1, 3, 3, 3])
        for h, label in zip(cols, ["Grade", "Min %", "Max %", "Update"]):
            h.markdown(f"**{label}**")
        st.divider()
        for band in scale:
            colour = GRADE_COLOURS.get(band["grade"], "#374151")
            c1, c2, c3, c4 = st.columns([1, 3, 3, 3])
            c1.markdown(
                f"<span style='background:{colour};color:#fff;padding:2px 10px;border-radius:4px;font-weight:700'>"
                f"{band['grade']}</span>",
                unsafe_allow_html=True,
            )
            new_min = c2.number_input(
                "Min %", min_value=0.0, max_value=100.0,
                value=float(band["min_percentage"]),
                key=f"min_{band['grade']}", label_visibility="collapsed"
            )
            new_max = c3.number_input(
                "Max %", min_value=0.0, max_value=100.0,
                value=float(band["max_percentage"]),
                key=f"max_{band['grade']}", label_visibility="collapsed"
            )
            with c4:
                if st.button("Save", key=f"save_{band['grade']}"):
                    upsert_grade_band(band["grade"], new_min, new_max)
                    st.success(f"Grade {band['grade']} updated.")
                    st.rerun()
    else:
        st.info("No grading scale configured.")

    st.divider()

    # ── Add a new grade band ────────────────────────────────────────────────
    st.subheader("➕ Add Custom Grade Band")
    with st.form("form_add_grade", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        new_grade = col1.text_input("Grade Letter (e.g. A+)")
        new_min = col2.number_input("Min Percentage", min_value=0.0, max_value=100.0, value=0.0)
        new_max = col3.number_input("Max Percentage", min_value=0.0, max_value=100.0, value=100.0)
        if st.form_submit_button("Add Grade Band", use_container_width=True):
            if new_grade:
                upsert_grade_band(new_grade.strip(), new_min, new_max)
                st.success(f"Grade band '{new_grade}' saved.")
                st.rerun()
            else:
                st.warning("Grade letter is required.")
