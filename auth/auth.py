import bcrypt
import streamlit as st
from db.database import get_connection


def login(username: str, password: str) -> dict | None:
    """Verify credentials and return user dict, or None if invalid."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id, username, password_hash, role FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None


def logout() -> None:
    """Clear the session state user."""
    st.session_state.pop("user", None)
    st.session_state.pop("page", None)


def get_current_user() -> dict | None:
    """Return the currently logged-in user dict from session state, or None."""
    return st.session_state.get("user", None)
