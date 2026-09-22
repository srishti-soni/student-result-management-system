from db.database import get_connection


def get_grading_scale() -> list[dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, grade, min_percentage, max_percentage FROM grading_scale ORDER BY min_percentage DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def upsert_grade_band(grade: str, min_pct: float, max_pct: float) -> None:
    conn = get_connection()
    conn.execute(
        """INSERT INTO grading_scale (grade, min_percentage, max_percentage)
           VALUES (?, ?, ?)
           ON CONFLICT(grade) DO UPDATE SET min_percentage=excluded.min_percentage,
                                            max_percentage=excluded.max_percentage""",
        (grade, min_pct, max_pct),
    )
    conn.commit()
    conn.close()


def compute_grade(percentage: float) -> str:
    """Return the grade letter for a given percentage based on the DB grading scale."""
    conn = get_connection()
    row = conn.execute(
        """SELECT grade FROM grading_scale
           WHERE ? >= min_percentage AND ? <= max_percentage
           LIMIT 1""",
        (percentage, percentage),
    ).fetchone()
    conn.close()
    if row:
        return row["grade"]
    # Fallback: if percentage is exactly 100 or a boundary edge case
    if percentage >= 90:
        return "A"
    return "F"
