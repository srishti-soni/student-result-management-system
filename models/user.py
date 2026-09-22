import bcrypt
from db.database import get_connection


def get_all_users() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT id, username, role FROM users ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_user(username: str, password: str, role: str) -> None:
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, pw_hash, role),
    )
    conn.commit()
    conn.close()


def update_user(user_id: int, username: str, role: str, password: str | None = None) -> None:
    conn = get_connection()
    if password:
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "UPDATE users SET username=?, role=?, password_hash=? WHERE id=?",
            (username, role, pw_hash, user_id),
        )
    else:
        conn.execute(
            "UPDATE users SET username=?, role=? WHERE id=?",
            (username, role, user_id),
        )
    conn.commit()
    conn.close()


def delete_user(user_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
