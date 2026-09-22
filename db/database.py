import sqlite3
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "srms.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection() -> sqlite3.Connection:
    """Return a sqlite3 connection with row_factory set to Row."""
    conn = sqlite3.connect(os.path.abspath(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create all tables from schema.sql if they don't exist."""
    with open(SCHEMA_PATH, "r") as f:
        schema = f.read()
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()


def seed_defaults() -> None:
    """Seed the default admin user and grading scale if they don't already exist."""
    conn = get_connection()

    # Default admin user
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", ("admin",)
    ).fetchone()
    if not existing:
        pw_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", pw_hash, "admin"),
        )

    # Default teacher demo account
    existing_teacher = conn.execute(
        "SELECT id FROM users WHERE username = ?", ("teacher1",)
    ).fetchone()
    if not existing_teacher:
        pw_hash = bcrypt.hashpw("teacher123".encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("teacher1", pw_hash, "teacher"),
        )

    # Default student demo account + linked student record
    existing_student_user = conn.execute(
        "SELECT id FROM users WHERE username = ?", ("student1",)
    ).fetchone()
    if not existing_student_user:
        pw_hash = bcrypt.hashpw("student123".encode(), bcrypt.gensalt()).decode()
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("student1", pw_hash, "student"),
        )
        conn.commit()  # flush so we can read the new id back
        student_user_id = conn.execute(
            "SELECT id FROM users WHERE username = ?", ("student1",)
        ).fetchone()["id"]
        # Only insert the student record if it doesn't exist yet
        existing_sr = conn.execute(
            "SELECT id FROM students WHERE roll_number = ?", ("S001",)
        ).fetchone()
        if not existing_sr:
            conn.execute(
                "INSERT INTO students (name, roll_number, class_year, user_id) VALUES (?, ?, ?, ?)",
                ("Demo Student", "S001", "Class 10", student_user_id),
            )

    # Default grading scale
    existing_scale = conn.execute("SELECT COUNT(*) AS cnt FROM grading_scale").fetchone()
    if existing_scale["cnt"] == 0:
        default_scale = [
            ("A", 90.0, 100.0),
            ("B", 80.0, 89.99),
            ("C", 70.0, 79.99),
            ("D", 60.0, 69.99),
            ("E", 50.0, 59.99),
            ("F", 0.0,  49.99),
        ]
        conn.executemany(
            "INSERT INTO grading_scale (grade, min_percentage, max_percentage) VALUES (?, ?, ?)",
            default_scale,
        )

    conn.commit()
    conn.close()
