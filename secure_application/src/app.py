from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from src.database import get_connection, initialize_database


app = Flask(__name__)

app.secret_key = "group07-student-portal-lab-key"

initialize_database()


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "")
        password = request.form.get("password", "")

        connection = get_connection()

        # ====================================================
        # VULNERABILITY 1: SQL INJECTION
        # ====================================================
        #
        # User-controlled username is directly concatenated
        # into the SQL statement.
        #
        # This is intentionally vulnerable for the assignment.
        # ====================================================

        query = (
            "SELECT * FROM users "
            "WHERE username = '" + username + "'"
        )

        user = connection.execute(query).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):
            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        # Demonstration path for SQL injection:
        # If SQL injection changes the selected account,
        # the password check still protects normal logins.
        # For the assignment, use the injected username with
        # the known lab password of the selected account.

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],),
    ).fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        user=user,
    )


# ============================================================
# COURSES
# ============================================================

@app.route("/courses")
def courses():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    courses = connection.execute(
        """
        SELECT *
        FROM courses
        ORDER BY code
        """
    ).fetchall()

    registrations = connection.execute(
        """
        SELECT course_id
        FROM registrations
        WHERE user_id = ?
        """,
        (session["user_id"],),
    ).fetchall()

    registered_ids = {
        row["course_id"]
        for row in registrations
    }

    connection.close()

    return render_template(
        "courses.html",
        courses=courses,
        registered_ids=registered_ids,
    )


@app.route("/courses/register/<int:course_id>", methods=["POST"])
def register_course(course_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    course = connection.execute(
        """
        SELECT *
        FROM courses
        WHERE id = ?
        """,
        (course_id,),
    ).fetchone()

    if not course:
        connection.close()
        return "Course not found", 404

    try:
        connection.execute(
            """
            INSERT INTO registrations
            (user_id, course_id)
            VALUES (?, ?)
            """,
            (session["user_id"], course_id),
        )

        connection.commit()
        flash("Course registered successfully.", "success")

    except Exception:
        flash("You are already registered for this course.", "error")

    connection.close()

    return redirect(url_for("courses"))


# ============================================================
# GRADES
# ============================================================

@app.route("/grades")
def grades():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    grades = connection.execute(
        """
        SELECT
            courses.code,
            courses.name,
            grades.grade
        FROM grades
        JOIN courses
            ON grades.course_id = courses.id
        WHERE grades.user_id = ?
        ORDER BY courses.code
        """,
        (session["user_id"],),
    ).fetchall()

    connection.close()

    return render_template(
        "grades.html",
        grades=grades,
    )


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile/<int:user_id>")
def profile(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    # ========================================================
    # VULNERABILITY 2: IDOR
    # ========================================================
    #
    # The application accepts an arbitrary user_id.
    #
    # It does NOT verify that user_id belongs to the logged-in
    # user.
    #
    # Therefore:
    #
    # Alice -> /profile/1
    # Alice -> /profile/2
    #
    # can expose Bob's profile.
    # ========================================================

    user = connection.execute(
        """
        SELECT id, username, name, email, bio
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    ).fetchone()

    connection.close()

    if not user:
        return "User not found", 404

    return render_template(
        "profile.html",
        user=user,
    )


# ============================================================
# PROFILE UPDATE
# ============================================================

@app.route(
    "/profile/<int:user_id>/update",
    methods=["POST"],
)
def update_profile(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    name = request.form.get("name", "")
    email = request.form.get("email", "")
    bio = request.form.get("bio", "")

    connection = get_connection()

    connection.execute(
        """
        UPDATE users
        SET name = ?,
            email = ?,
            bio = ?
        WHERE id = ?
        """,
        (name, email, bio, user_id),
    )

    connection.commit()
    connection.close()

    flash("Profile updated.", "success")

    return redirect(
        url_for(
            "profile",
            user_id=user_id,
        )
    )


# ============================================================
# XSS DEMONSTRATION
# ============================================================

@app.route("/search")
def search():

    search_term = request.args.get("q", "")

    # ========================================================
    # VULNERABILITY 3: REFLECTED XSS
    # ========================================================
    #
    # User input is inserted into an HTML response without
    # HTML escaping.
    # ========================================================

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Student Portal Search</title>
        <link
            rel="stylesheet"
            href="/static/style.css"
        >
    </head>

    <body>

        <div class="container">

            <h1>Student Portal Search</h1>

            <p>
                Search results for:
                {search_term}
            </p>

            <p>
                No additional results were found.
            </p>

            <a href="/dashboard">
                Back to Dashboard
            </a>

        </div>

    </body>
    </html>
    """

    return html


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )