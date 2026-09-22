import streamlit as st
import pandas as pd
import plotly.express as px
from models.student import get_student_by_user_id
from models.result import get_results_by_student
from models.grading import compute_grade
from utils.ui import page_header, inject_css, grade_badge
from utils.report_csv import generate_csv
from utils.report_pdf import generate_pdf

PASS_THRESHOLD_PCT = 40.0


def render(user: dict):
    inject_css()
    page_header("My Results", "Your academic performance at a glance", "📋")

    student = get_student_by_user_id(user["id"])
    if not student:
        st.warning(
            "Your student profile has not been linked yet. Please contact the administrator."
        )
        return

    st.markdown(
        f"""
        <div style='background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:1rem 1.5rem;margin-bottom:1rem'>
            <b>👤 {student['name']}</b> &nbsp;|&nbsp;
            Roll No: <b>{student['roll_number']}</b> &nbsp;|&nbsp;
            Class: <b>{student['class_year']}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    results = get_results_by_student(student["id"])
    if not results:
        st.info("No results published yet. Check back later.")
        return

    df = pd.DataFrame(results)
    df["Percentage"] = (df["marks_obtained"] / df["max_marks"] * 100).round(2)
    df["Grade"] = df["Percentage"].apply(compute_grade)
    df["Pass/Fail"] = df["Percentage"].apply(
        lambda p: "✅ Pass" if p >= PASS_THRESHOLD_PCT else "❌ Fail"
    )

    display_df = df[["subject_name", "marks_obtained", "max_marks", "Percentage", "Grade", "Pass/Fail"]].copy()
    display_df.columns = ["Subject", "Marks Obtained", "Max Marks", "Percentage %", "Grade", "Pass/Fail"]

    # ── KPI cards ─────────────────────────────────────────────────────────
    total_obtained = df["marks_obtained"].sum()
    total_max = df["max_marks"].sum()
    overall_pct = (total_obtained / total_max * 100) if total_max else 0
    overall_grade = compute_grade(overall_pct)
    subjects_passed = (df["Percentage"] >= PASS_THRESHOLD_PCT).sum()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("📝 Subjects", len(df))
    k2.metric("📊 Overall %", f"{overall_pct:.1f}%")
    k3.metric("🏅 Overall Grade", overall_grade)
    k4.metric("✅ Subjects Passed", f"{subjects_passed}/{len(df)}")
    st.divider()

    # ── Results table ──────────────────────────────────────────────────────
    st.subheader("📋 Subject-wise Results")
    st.dataframe(display_df, width="stretch", hide_index=True)

    # ── Performance radar/bar chart ────────────────────────────────────────
    st.subheader("📊 Performance Chart")
    fig = px.bar(
        display_df, x="Subject", y="Percentage %",
        color="Percentage %", color_continuous_scale="Greens",
        text="Percentage %", range_y=[0, 100],
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30),
    )
    # Pass threshold reference line
    fig.add_hline(y=PASS_THRESHOLD_PCT, line_dash="dot", line_color="red",
                  annotation_text="Pass Threshold", annotation_position="top right")
    st.plotly_chart(fig, width="stretch")

    # ── Download buttons ──────────────────────────────────────────────────
    st.divider()
    st.subheader("⬇️ Download My Report")
    dl1, dl2 = st.columns(2)
    with dl1:
        csv_bytes = generate_csv(display_df)
        st.download_button(
            "📥 Download CSV",
            data=csv_bytes,
            file_name=f"results_{student['roll_number']}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        pdf_bytes = generate_pdf(
            f"Result Report — {student['name']} ({student['roll_number']})",
            display_df,
        )
        st.download_button(
            "📄 Download PDF",
            data=pdf_bytes,
            file_name=f"results_{student['roll_number']}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
