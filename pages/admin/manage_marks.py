import streamlit as st
from models.student import get_all_students
from models.subject import get_all_subjects
from models.result import upsert_result, get_results_by_student
from utils.ui import page_header, inject_css


def render():
    inject_css()
    page_header("Enter / Edit Marks", "Record or update marks for any student and subject", "✏️")

    students = get_all_students()
    subjects = get_all_subjects()

    if not students:
        st.warning("No students found. Add students first.")
        return
    if not subjects:
        st.warning("No subjects found. Add subjects first.")
        return

    col1, col2 = st.columns(2)
    student_names = [f"{s['roll_number']} — {s['name']}" for s in students]
    selected_student_label = col1.selectbox("Select Student", student_names)
    selected_student = students[student_names.index(selected_student_label)]

    subject_names = [s["name"] for s in subjects]
    selected_subject_label = col2.selectbox("Select Subject", subject_names)
    selected_subject = subjects[subject_names.index(selected_subject_label)]

    # Current marks for this student
    existing_results = {r["subject_id"]: r["marks_obtained"] for r in get_results_by_student(selected_student["id"])}
    current_marks = existing_results.get(selected_subject["id"], 0.0)

    st.markdown(
        f"**Max Marks for {selected_subject['name']}:** {selected_subject['max_marks']}"
    )

    with st.form("form_enter_marks"):
        marks = st.number_input(
            "Marks Obtained",
            min_value=0.0,
            max_value=float(selected_subject["max_marks"]),
            value=float(current_marks),
            step=0.5,
        )
        if st.form_submit_button("💾 Save Marks", use_container_width=True):
            upsert_result(selected_student["id"], selected_subject["id"], marks)
            st.success(
                f"Marks saved: {selected_student['name']} | {selected_subject['name']} → {marks}/{selected_subject['max_marks']}"
            )
            st.rerun()

    # ── Full marks table for this student ───────────────────────────────────
    st.divider()
    st.subheader(f"All Marks for {selected_student['name']}")
    results = get_results_by_student(selected_student["id"])
    if results:
        import pandas as pd
        df = pd.DataFrame(results)[["subject_name", "marks_obtained", "max_marks"]]
        df.columns = ["Subject", "Marks Obtained", "Max Marks"]
        df["Percentage"] = (df["Marks Obtained"] / df["Max Marks"] * 100).round(2)
        st.dataframe(df, width="stretch", hide_index=True)
    else:
        st.info("No marks entered yet.")
