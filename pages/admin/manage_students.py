import streamlit as st
from models.student import get_all_students, create_student, update_student, delete_student
from models.user import get_all_users
from utils.ui import page_header, inject_css


def render():
    inject_css()
    page_header("Manage Students", "Add, edit and remove student records", "🎓")

    students = get_all_students()
    users = get_all_users()
    student_users = [u for u in users if u["role"] == "student"]
    user_options = {u["id"]: u["username"] for u in student_users}
    user_options[0] = "— None —"

    # ── Student list ────────────────────────────────────────────────────────
    st.subheader("All Students")
    if students:
        cols = st.columns([1, 3, 2, 2, 2, 1, 1])
        for h, label in zip(cols, ["ID", "Name", "Roll No.", "Class/Year", "Account", "Edit", "Del"]):
            h.markdown(f"**{label}**")
        st.divider()
        for s in students:
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1, 3, 2, 2, 2, 1, 1])
            c1.write(s["id"])
            c2.write(s["name"])
            c3.write(s["roll_number"])
            c4.write(s["class_year"])
            c5.write(s.get("username") or "—")
            with c6:
                if st.button("✏️", key=f"edit_s_{s['id']}"):
                    st.session_state["edit_student"] = s
            with c7:
                if st.button("🗑️", key=f"del_s_{s['id']}"):
                    delete_student(s["id"])
                    st.success(f"Student '{s['name']}' deleted.")
                    st.rerun()
    else:
        st.info("No students found.")

    st.divider()

    # ── Edit form ───────────────────────────────────────────────────────────
    edit_target = st.session_state.get("edit_student")
    if edit_target:
        st.subheader(f"Edit Student — {edit_target['name']}")
        uid_keys = list(user_options.keys())
        uid_labels = [user_options[k] for k in uid_keys]
        current_uid = edit_target.get("user_id") or 0
        uid_idx = uid_keys.index(current_uid) if current_uid in uid_keys else 0
        with st.form("form_edit_student"):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Name", value=edit_target["name"])
            new_roll = col2.text_input("Roll Number", value=edit_target["roll_number"])
            col3, col4 = st.columns(2)
            new_class = col3.text_input("Class / Year", value=edit_target["class_year"])
            new_uid_label = col4.selectbox("Linked User Account", uid_labels, index=uid_idx)
            new_uid = uid_keys[uid_labels.index(new_uid_label)]
            col_save, col_cancel = st.columns(2)
            submitted = col_save.form_submit_button("💾 Save", use_container_width=True)
            cancelled = col_cancel.form_submit_button("✖ Cancel", use_container_width=True)
        if submitted:
            update_student(edit_target["id"], new_name, new_roll, new_class, new_uid if new_uid != 0 else None)
            st.success("Student updated.")
            st.session_state.pop("edit_student", None)
            st.rerun()
        if cancelled:
            st.session_state.pop("edit_student", None)
            st.rerun()

    # ── Create student ──────────────────────────────────────────────────────
    st.subheader("➕ Add New Student")
    uid_keys = list(user_options.keys())
    uid_labels = [user_options[k] for k in uid_keys]
    with st.form("form_create_student", clear_on_submit=True):
        col1, col2 = st.columns(2)
        new_name = col1.text_input("Full Name")
        new_roll = col2.text_input("Roll Number")
        col3, col4 = st.columns(2)
        new_class = col3.text_input("Class / Year")
        new_uid_label = col4.selectbox("Linked User Account (optional)", uid_labels)
        new_uid = uid_keys[uid_labels.index(new_uid_label)]
        if st.form_submit_button("Add Student", use_container_width=True):
            if new_name and new_roll and new_class:
                try:
                    create_student(new_name, new_roll, new_class, new_uid if new_uid != 0 else None)
                    st.success(f"Student '{new_name}' added.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Name, Roll Number and Class/Year are required.")
