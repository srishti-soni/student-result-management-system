import streamlit as st
import pandas as pd
import plotly.express as px
from models.result import get_class_results
from models.grading import compute_grade
from utils.ui import page_header, inject_css, grade_badge
from utils.report_csv import generate_csv
from utils.report_pdf import generate_pdf

PASS_THRESHOLD_PCT = 40.0


def render():
    inject_css()
    page_header("Class Analytics", "Class-wide performance overview with charts and downloads", "📈")

    raw = get_class_results()
    if not raw:
        st.info("No results data available yet. Enter marks to see analytics.")
        return

    df = pd.DataFrame(raw)
    # Only rows with marks entered
    df_filled = df.dropna(subset=["marks_obtained"]).copy()

    if df_filled.empty:
        st.info("No marks have been entered yet.")
        return

    df_filled["percentage"] = (df_filled["marks_obtained"] / df_filled["max_marks"] * 100).round(2)
    df_filled["grade"] = df_filled["percentage"].apply(compute_grade)
    df_filled["pass_fail"] = df_filled["percentage"].apply(
        lambda p: "Pass" if p >= PASS_THRESHOLD_PCT else "Fail"
    )

    # ── KPI cards ─────────────────────────────────────────────────────────
    total_students = df_filled["student_id"].nunique()
    class_avg = df_filled["percentage"].mean()
    highest = df_filled["percentage"].max()
    pass_rate = (df_filled["pass_fail"] == "Pass").mean() * 100

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("👥 Total Students", total_students)
    k2.metric("📊 Class Average", f"{class_avg:.1f}%")
    k3.metric("🏆 Highest Score", f"{highest:.1f}%")
    k4.metric("✅ Pass Rate", f"{pass_rate:.1f}%")
    st.divider()

    # ── Subject-wise average bar chart ────────────────────────────────────
    st.subheader("Subject-wise Average Marks")
    subj_avg = df_filled.groupby("subject_name")["percentage"].mean().reset_index()
    subj_avg.columns = ["Subject", "Average %"]
    fig_bar = px.bar(
        subj_avg, x="Subject", y="Average %",
        color="Average %", color_continuous_scale="Blues",
        text="Average %", range_y=[0, 100],
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_bar.update_layout(coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", margin=dict(t=30))
    st.plotly_chart(fig_bar, width="stretch")

    # ── Student overall performance pivot ─────────────────────────────────
    st.subheader("Student Overall Performance")
    student_summary = (
        df_filled.groupby(["student_id", "student_name", "roll_number"])
        .agg(total_obtained=("marks_obtained", "sum"), total_max=("max_marks", "sum"))
        .reset_index()
    )
    student_summary["Overall %"] = (student_summary["total_obtained"] / student_summary["total_max"] * 100).round(2)
    student_summary["Grade"] = student_summary["Overall %"].apply(compute_grade)
    student_summary["Pass/Fail"] = student_summary["Overall %"].apply(
        lambda p: "✅ Pass" if p >= PASS_THRESHOLD_PCT else "❌ Fail"
    )
    display_cols = student_summary[["roll_number", "student_name", "total_obtained", "total_max", "Overall %", "Grade", "Pass/Fail"]]
    display_cols = display_cols.rename(columns={"roll_number": "Roll No.", "student_name": "Name", "total_obtained": "Total Marks", "total_max": "Max Marks"})
    st.dataframe(display_cols, width="stretch", hide_index=True)

    # ── Top 5 / Bottom 5 ──────────────────────────────────────────────────
    col_top, col_bot = st.columns(2)
    with col_top:
        st.subheader("🏆 Top 5 Performers")
        top5 = student_summary.nlargest(5, "Overall %")[["student_name", "roll_number", "Overall %", "Grade"]]
        top5.columns = ["Name", "Roll No.", "Overall %", "Grade"]
        st.dataframe(top5, width="stretch", hide_index=True)
    with col_bot:
        st.subheader("⚠️ Bottom 5 Performers")
        bot5 = student_summary.nsmallest(5, "Overall %")[["student_name", "roll_number", "Overall %", "Grade"]]
        bot5.columns = ["Name", "Roll No.", "Overall %", "Grade"]
        st.dataframe(bot5, width="stretch", hide_index=True)

    # ── Download buttons ──────────────────────────────────────────────────
    st.divider()
    st.subheader("⬇️ Download Reports")
    dl1, dl2 = st.columns(2)
    report_df = display_cols.copy()
    with dl1:
        csv_bytes = generate_csv(report_df)
        st.download_button(
            "📥 Download CSV",
            data=csv_bytes,
            file_name="class_analytics.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with dl2:
        pdf_bytes = generate_pdf("Class Analytics Report", report_df)
        st.download_button(
            "📄 Download PDF",
            data=pdf_bytes,
            file_name="class_analytics.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
