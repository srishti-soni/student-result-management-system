import streamlit as st
from auth.auth import get_current_user, logout


def render_admin_sidebar() -> str:
    """Render the admin sidebar and return the selected page key."""
    user = get_current_user()
    with st.sidebar:
        st.markdown(
            f"""
            <div style='text-align:center;padding:1rem 0 0.5rem'>
                <div style='font-size:2.5rem'>🛡️</div>
                <div style='font-weight:700;font-size:1.1rem;color:#4F46E5'>{user['username']}</div>
                <div style='font-size:0.75rem;color:#6B7280;text-transform:uppercase;letter-spacing:.05em'>Administrator</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        page = st.radio(
            "Navigation",
            options=[
                "👥  Manage Users",
                "🎓  Manage Students",
                "📚  Manage Subjects",
                "✏️  Enter / Edit Marks",
                "📊  Grading Scale",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        if st.button("🚪  Logout", use_container_width=True):
            logout()
            st.rerun()
    return page
