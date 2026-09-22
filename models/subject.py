from db.database import get_connection


def get_all_subjects() -> list[dict]:
    conn = get_connection()
    rows = conn.execute("SELECT id, name, max_marks FROM subjects ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_subject(name: str, max_marks: int) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO subjects (name, max_marks) VALUES (?, ?)",
        (name, max_marks),
    )
    conn.commit()
    conn.close()


def update_subject(subject_id: int, name: str, max_marks: int) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE subjects SET name=?, max_marks=? WHERE id=?",
        (name, max_marks, subject_id),
    )
    conn.commit()
    conn.close()


def delete_subject(subject_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM subjects WHERE id=?", (subject_id,))
    conn.commit()
    conn.close()
