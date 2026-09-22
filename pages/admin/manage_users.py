import streamlit as st
from models.user import get_all_users, create_user, update_user, delete_user
from utils.ui import page_header, inject_css


def render():
    inject_css()
    page_header("Manage Users", "Create, edit and remove system accounts", "👥")

    users = get_all_users()

    # ── Display existing users ──────────────────────────────────────────────
    st.subheader("All Users")
    if users:
        cols = st.columns([1, 3, 2, 1, 1])
        for h, label in zip(cols, ["ID", "Username", "Role", "Edit", "Delete"]):
            h.markdown(f"**{label}**")
        st.divider()
        for u in users:
            c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 1, 1])
            c1.write(u["id"])
            c2.write(u["username"])
            c3.write(u["role"].capitalize())
            with c4:
                if st.button("✏️", key=f"edit_u_{u['id']}"):
                    st.session_state["edit_user"] = u
            with c5:
                if u["username"] != "admin":
                    if st.button("🗑️", key=f"del_u_{u['id']}"):
                        delete_user(u["id"])
                        st.success(f"User '{u['username']}' deleted.")
                        st.rerun()
    else:
        st.info("No users found.")

    st.divider()

    # ── Edit form ───────────────────────────────────────────────────────────
    edit_target = st.session_state.get("edit_user")
    if edit_target:
        st.subheader(f"Edit User — {edit_target['username']}")
        with st.form("form_edit_user"):
            new_username = st.text_input("Username", value=edit_target["username"])
            new_role = st.selectbox(
                "Role",
                ["admin", "teacher", "student"],
                index=["admin", "teacher", "student"].index(edit_target["role"]),
            )
            new_password = st.text_input("New Password (leave blank to keep current)", type="password")
            col_save, col_cancel = st.columns(2)
            submitted = col_save.form_submit_button("💾 Save", use_container_width=True)
            cancelled = col_cancel.form_submit_button("✖ Cancel", use_container_width=True)
        if submitted:
            update_user(edit_target["id"], new_username, new_role, new_password or None)
            st.success("User updated successfully.")
            st.session_state.pop("edit_user", None)
            st.rerun()
        if cancelled:
            st.session_state.pop("edit_user", None)
            st.rerun()

    # ── Create new user ─────────────────────────────────────────────────────
    st.subheader("➕ Create New User")
    with st.form("form_create_user", clear_on_submit=True):
        col1, col2 = st.columns(2)
        new_u = col1.text_input("Username")
        new_r = col2.selectbox("Role", ["admin", "teacher", "student"])
        new_p = st.text_input("Password", type="password")
        if st.form_submit_button("Create User", use_container_width=True):
            if new_u and new_p:
                try:
                    create_user(new_u, new_p, new_r)
                    st.success(f"User '{new_u}' created.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Username and password are required.")
