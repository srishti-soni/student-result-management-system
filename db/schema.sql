CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL CHECK(role IN ('admin', 'teacher', 'student'))
);

CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    roll_number TEXT    NOT NULL UNIQUE,
    class_year  TEXT    NOT NULL,
    user_id     INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    max_marks  INTEGER NOT NULL DEFAULT 100
);

CREATE TABLE IF NOT EXISTS results (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id     INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id     INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    marks_obtained REAL    NOT NULL DEFAULT 0,
    UNIQUE(student_id, subject_id)
);

CREATE TABLE IF NOT EXISTS grading_scale (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    grade           TEXT    NOT NULL UNIQUE,
    min_percentage  REAL    NOT NULL,
    max_percentage  REAL    NOT NULL
);
