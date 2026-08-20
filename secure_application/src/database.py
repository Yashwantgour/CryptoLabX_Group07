import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "student_portal.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            bio TEXT DEFAULT '',
            role TEXT DEFAULT 'student'
        );

        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            UNIQUE(user_id, course_id),
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            grade TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
        """
    )

    users = [
        (
            "alice",
            generate_password_hash("alice123"),
            "Alice Student",
            "alice@example.com",
            "Computer Science student",
        ),
        (
            "bob",
            generate_password_hash("bob123"),
            "Bob Student",
            "bob@example.com",
            "Cybersecurity student",
        ),
    ]

    for user in users:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users
            (username, password_hash, name, email, bio)
            VALUES (?, ?, ?, ?, ?)
            """,
            user,
        )

    courses = [
        (
            "CS301",
            "Cryptography",
            "Introduction to cryptographic algorithms.",
        ),
        (
            "CS302",
            "Network Security",
            "Fundamentals of network security.",
        ),
        (
            "CS303",
            "Web Security",
            "Web application security fundamentals.",
        ),
    ]

    for course in courses:
        cursor.execute(
            """
            INSERT OR IGNORE INTO courses
            (code, name, description)
            VALUES (?, ?, ?)
            """,
            course,
        )

    # Get Alice
    alice = cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        ("alice",),
    ).fetchone()

    crypto = cursor.execute(
        "SELECT id FROM courses WHERE code = ?",
        ("CS301",),
    ).fetchone()

    network = cursor.execute(
        "SELECT id FROM courses WHERE code = ?",
        ("CS302",),
    ).fetchone()

    if alice and crypto:
        cursor.execute(
            """
            INSERT OR IGNORE INTO grades
            (user_id, course_id, grade)
            VALUES (?, ?, ?)
            """,
            (alice["id"], crypto["id"], "A"),
        )

    if alice and network:
        cursor.execute(
            """
            INSERT OR IGNORE INTO grades
            (user_id, course_id, grade)
            VALUES (?, ?, ?)
            """,
            (alice["id"], network["id"], "B"),
        )

    # Get Bob
    bob = cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        ("bob",),
    ).fetchone()

    if bob and crypto:
        cursor.execute(
            """
            INSERT OR IGNORE INTO grades
            (user_id, course_id, grade)
            VALUES (?, ?, ?)
            """,
            (bob["id"], crypto["id"], "B"),
        )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")