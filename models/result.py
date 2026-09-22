from db.database import get_connection


def get_results_by_student(student_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.id, r.student_id, r.subject_id, r.marks_obtained,
                  s.name AS subject_name, s.max_marks
           FROM results r
           JOIN subjects s ON r.subject_id = s.id
           WHERE r.student_id = ?
           ORDER BY s.name""",
        (student_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_results_by_subject(subject_id: int) -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        """SELECT r.id, r.student_id, r.subject_id, r.marks_obtained,
                  st.name AS student_name, st.roll_number, s.max_marks
           FROM results r
           JOIN students st ON r.student_id = st.id
           JOIN subjects  s ON r.subject_id = s.id
           WHERE r.subject_id = ?
           ORDER BY st.roll_number""",
        (subject_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_result(student_id: int, subject_id: int, marks_obtained: float) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT INTO results (student_id, subject_id, marks_obtained)
           VALUES (?, ?, ?)
           ON CONFLICT(student_id, subject_id) DO UPDATE SET marks_obtained=excluded.marks_obtained""",
        (student_id, subject_id, marks_obtained),
    )
    conn.commit()
    conn.close()


def get_class_results() -> list[dict]:
    """Return all results joined with student and subject info — suitable for DataFrame construction."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT st.id AS student_id, st.name AS student_name, st.roll_number,
                  st.class_year,
                  s.id AS subject_id, s.name AS subject_name, s.max_marks,
                  COALESCE(r.marks_obtained, NULL) AS marks_obtained
           FROM students st
           CROSS JOIN subjects s
           LEFT JOIN results r ON r.student_id = st.id AND r.subject_id = s.id
           ORDER BY st.roll_number, s.name"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
