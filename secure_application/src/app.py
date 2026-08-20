import sqlite3
import os

# Database setup
DB_FILE = "student_portal.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            profile_info TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_name TEXT,
            grade TEXT
        )
    ''')
    
    # Insert dummy data
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, profile_info) VALUES (1, 'admin', 'admin123', 'admin', 'System Admin')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, profile_info) VALUES (2, 'alice', 'alice123', 'student', 'First Year CS')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password, role, profile_info) VALUES (3, 'bob', 'bob123', 'student', 'Second Year IT')")
    
    cursor.execute("INSERT OR IGNORE INTO courses (id, course_name) VALUES (1, 'Cryptography 101')")
    cursor.execute("INSERT OR IGNORE INTO courses (id, course_name) VALUES (2, 'Web Security')")
    
    cursor.execute("INSERT OR IGNORE INTO grades (student_id, course_name, grade) VALUES (2, 'Cryptography 101', 'A')")
    cursor.execute("INSERT OR IGNORE INTO grades (student_id, course_name, grade) VALUES (3, 'Web Security', 'B')")
    
    conn.commit()
    conn.close()

def login():
    print("\n--- Student Portal Login ---")
    username = input("Username: ")
    password = input("Password: ")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # VULNERABILITY 1: SQL Injection
    # A user can bypass authentication by providing a crafted payload like: ' OR '1'='1' --
    query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"
    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        return user
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.close()
        return None

def register_course(user):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("\n--- Register Course ---")
    cursor.execute("SELECT id, course_name FROM courses")
    courses = cursor.fetchall()
    for course in courses:
        print(f"{course[0]}. {course[1]}")
        
    course_id = input("Enter course ID to register: ")
    
    cursor.execute("INSERT INTO registrations (student_id, course_id) VALUES (?, ?)", (user[0], course_id))
    conn.commit()
    print("Registered successfully!")
    conn.close()

def view_grades(user):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("\n--- View Grades ---")
    # VULNERABILITY 2: Insecure Direct Object Reference (IDOR)
    # The application asks for student ID instead of using the logged-in user's ID
    # A student can enter another student's ID (e.g., 2 or 3) to view their grades.
    student_id_input = input(f"Enter Student ID to view grades (Your ID is {user[0]}): ")
    
    cursor.execute("SELECT course_name, grade FROM grades WHERE student_id = ?", (student_id_input,))
    grades = cursor.fetchall()
    
    if grades:
        for grade in grades:
            print(f"Course: {grade[0]}, Grade: {grade[1]}")
    else:
        print("No grades found.")
        
    conn.close()

def update_profile(user):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("\n--- Update Profile ---")
    new_info = input("Enter new profile information: ")
    
    cursor.execute("UPDATE users SET profile_info = ? WHERE id = ?", (new_info, user[0]))
    conn.commit()
    print("Profile updated successfully.")
    
    conn.close()
    
def admin_panel(user):
    # VULNERABILITY 3: Broken Access Control
    # Any user can access this functionality because the caller does not verify the user's role.
    print("\n--- Admin Panel ---")
    print("Welcome Admin. Here you can view all users in the system.")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, profile_info FROM users")
    users = cursor.fetchall()
    for u in users:
        print(f"ID: {u[0]}, Username: {u[1]}, Role: {u[2]}, Profile: {u[3]}")
    conn.close()

def main():
    if not os.path.exists(DB_FILE):
        init_db()
        
    print("Welcome to the Student Portal Console Application")
    user = login()
    
    if user:
        print(f"\nWelcome {user[1]}! Role: {user[2]}")
        while True:
            print("\n1. Register Course")
            print("2. View Grades")
            print("3. Update Profile")
            print("4. Admin Panel")
            print("5. Logout")
            
            choice = input("Select an option: ")
            
            if choice == '1':
                register_course(user)
            elif choice == '2':
                view_grades(user)
            elif choice == '3':
                update_profile(user)
            elif choice == '4':
                # No role verification performed! (Broken Access Control)
                admin_panel(user)
            elif choice == '5':
                print("Logging out...")
                break
            else:
                print("Invalid choice.")
    else:
        print("Login failed. Invalid username or password.")

if __name__ == "__main__":
    main()