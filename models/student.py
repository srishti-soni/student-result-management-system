from db.database import get_connection


def get_all_students() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT s.id, s.name, s.roll_number, s.class_year, s.user_id,
                  u.username
           FROM students s
           LEFT JOIN users u ON s.user_id = u.id
           ORDER BY s.roll_number"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_by_user_id(user_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, roll_number, class_year, user_id FROM students WHERE user_id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_student(name: str, roll_number: str, class_year: str, user_id: int | None = None) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (name, roll_number, class_year, user_id) VALUES (?, ?, ?, ?)",
        (name, roll_number, class_year, user_id),
    )
    conn.commit()
    conn.close()


def update_student(student_id: int, name: str, roll_number: str, class_year: str, user_id: int | None) -> None:
    conn = get_connection()
    conn.execute(
        "UPDATE students SET name=?, roll_number=?, class_year=?, user_id=? WHERE id=?",
        (name, roll_number, class_year, user_id, student_id),
    )
    conn.commit()
    conn.close()


def delete_student(student_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
