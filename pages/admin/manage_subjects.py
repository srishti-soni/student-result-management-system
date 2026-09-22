import streamlit as st
from models.subject import get_all_subjects, create_subject, update_subject, delete_subject
from utils.ui import page_header, inject_css


def render():
    inject_css()
    page_header("Manage Subjects", "Add, edit and remove subjects with their maximum marks", "📚")

    subjects = get_all_subjects()

    # ── Subject list ────────────────────────────────────────────────────────
    st.subheader("All Subjects")
    if subjects:
        cols = st.columns([1, 4, 2, 1, 1])
        for h, label in zip(cols, ["ID", "Subject Name", "Max Marks", "Edit", "Delete"]):
            h.markdown(f"**{label}**")
        st.divider()
        for s in subjects:
            c1, c2, c3, c4, c5 = st.columns([1, 4, 2, 1, 1])
            c1.write(s["id"])
            c2.write(s["name"])
            c3.write(s["max_marks"])
            with c4:
                if st.button("✏️", key=f"edit_sub_{s['id']}"):
                    st.session_state["edit_subject"] = s
            with c5:
                if st.button("🗑️", key=f"del_sub_{s['id']}"):
                    delete_subject(s["id"])
                    st.success(f"Subject '{s['name']}' deleted.")
                    st.rerun()
    else:
        st.info("No subjects found.")

    st.divider()

    # ── Edit form ───────────────────────────────────────────────────────────
    edit_target = st.session_state.get("edit_subject")
    if edit_target:
        st.subheader(f"Edit Subject — {edit_target['name']}")
        with st.form("form_edit_subject"):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Subject Name", value=edit_target["name"])
            new_max = col2.number_input("Max Marks", min_value=1, max_value=1000, value=int(edit_target["max_marks"]))
            col_save, col_cancel = st.columns(2)
            submitted = col_save.form_submit_button("💾 Save", use_container_width=True)
            cancelled = col_cancel.form_submit_button("✖ Cancel", use_container_width=True)
        if submitted:
            update_subject(edit_target["id"], new_name, new_max)
            st.success("Subject updated.")
            st.session_state.pop("edit_subject", None)
            st.rerun()
        if cancelled:
            st.session_state.pop("edit_subject", None)
            st.rerun()

    # ── Create subject ──────────────────────────────────────────────────────
    st.subheader("➕ Add New Subject")
    with st.form("form_create_subject", clear_on_submit=True):
        col1, col2 = st.columns(2)
        new_name = col1.text_input("Subject Name")
        new_max = col2.number_input("Max Marks", min_value=1, max_value=1000, value=100)
        if st.form_submit_button("Add Subject", use_container_width=True):
            if new_name:
                try:
                    create_subject(new_name, int(new_max))
                    st.success(f"Subject '{new_name}' added.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Subject name is required.")
