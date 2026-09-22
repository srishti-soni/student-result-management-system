import sys
import os

# Ensure the project root is on sys.path so all modules resolve correctly
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

st.set_page_config(
    page_title="SRMS — Student Result Management",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

from db.database import init_db, seed_defaults
from auth.auth import login, get_current_user
from utils.ui import inject_css

# ── Initialise DB once per session ───────────────────────────────────────────
@st.cache_resource
def _bootstrap():
    init_db()
    seed_defaults()

_bootstrap()


# ── Login page ────────────────────────────────────────────────────────────────
def show_login():
    inject_css()
    col_left, col_center, col_right = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown(
            """
            <div style='text-align:center;padding:2.5rem 0 1rem'>
                <div style='font-size:3.5rem'>🎓</div>
                <h1 style='font-size:1.8rem;font-weight:800;color:#1e1b4b;margin:0.25rem 0'>
                    Student Result Management
                </h1>
                <p style='color:#6B7280;margin:0.25rem 0 1.5rem'>
                    Secure · Organised · Insightful
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("👤  Username", placeholder="Enter your username")
            password = st.text_input("🔑  Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if username and password:
                user = login(username, password)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")

        st.markdown(
            "<p style='text-align:center;color:#9ca3af;font-size:0.78rem;margin-top:1.5rem'>"
            "Default admin: <b>admin</b> / <b>admin123</b></p>",
            unsafe_allow_html=True,
        )


# ── Role routing ──────────────────────────────────────────────────────────────
def main():
    user = get_current_user()

    if not user:
        show_login()
        return

    role = user["role"]

    if role == "admin":
        from pages.admin.dashboard import render_admin_sidebar
        from pages.admin import manage_users, manage_students, manage_subjects, manage_marks, grading_scale
        page = render_admin_sidebar()
        if "Manage Users" in page:
            manage_users.render()
        elif "Manage Students" in page:
            manage_students.render()
        elif "Manage Subjects" in page:
            manage_subjects.render()
        elif "Enter / Edit Marks" in page:
            manage_marks.render()
        elif "Grading Scale" in page:
            grading_scale.render()

    elif role == "teacher":
        from pages.teacher.dashboard import render_teacher_sidebar
        from pages.teacher import enter_marks, analytics
        page = render_teacher_sidebar()
        if "Enter / Edit Marks" in page:
            enter_marks.render()
        elif "Class Analytics" in page:
            analytics.render()

    elif role == "student":
        from pages.student.dashboard import render_student_sidebar
        from pages.student import my_results
        render_student_sidebar()
        my_results.render(user)

    else:
        st.error("Unknown role. Please contact the administrator.")


if __name__ == "__main__":
    main()
else:
    main()
