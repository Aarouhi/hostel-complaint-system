from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "hostel_secret_key"

def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_number TEXT,
        category TEXT,
        student_name TEXT,
        anonymous TEXT,
        complaint TEXT,
        status TEXT

    )
    """)

    conn.commit()
    conn.close()

init_db()


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin"] = True
            return redirect(url_for("dashboard"))

        else:

            return """
            <h2>Invalid Username or Password</h2>
            <a href='/login'>Try Again</a>
            """

    return render_template("login.html")


# LOGOUT
@app.route("/logout")
def logout():

    session.pop("admin", None)

    return """
    <h2>Logged Out Successfully</h2>
    <a href='/'>Go To Home Page</a>
    """


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        room_number = request.form["room_number"]
        category = request.form["category"]
        student_name = request.form["student_name"]
        anonymous = request.form["anonymous"]
        complaint = request.form["complaint"]

        if anonymous == "Yes":
            student_name = "Anonymous"

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO complaints
        (room_number, category, student_name,
         anonymous, complaint, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            room_number,
            category,
            student_name,
            anonymous,
            complaint,
            "Pending"
        ))

        conn.commit()
        conn.close()

        return """
<!DOCTYPE html>
<html>

<head>

<meta http-equiv="refresh" content="2;url=/">

<style>

body{
font-family:'Segoe UI',sans-serif;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
background:#f8fafc;
margin:0;
}

.box{
background:white;
padding:40px;
border-radius:20px;
box-shadow:0 10px 30px rgba(0,0,0,0.08);
text-align:center;
width:400px;
}

h2{
color:#166534;
margin-bottom:15px;
}

p{
color:#64748b;
}

</style>

</head>

<body>

<div class="box">

<h2>✅ Complaint Registered Successfully</h2>

<p>Redirecting to Home Page...</p>

</div>

</body>

</html>
"""

    return render_template("register.html")
# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status='Pending'"
    )
    pending = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status='In Progress'"
    )
    in_progress = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM complaints WHERE status='Resolved'"
    )
    resolved = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        complaints=complaints,
        total=total,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved
    )


# SEARCH
@app.route("/search", methods=["POST"])
def search():

    if "admin" not in session:
        return redirect(url_for("login"))

    room_number = request.form["room_number"]

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM complaints WHERE room_number=?",
        (room_number,)
    )

    complaints = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        complaints=complaints,
        total=len(complaints),
        pending=0,
        in_progress=0,
        resolved=0
    )


# MARK IN PROGRESS
@app.route("/progress/<int:id>")
def progress(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status='In Progress' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# MARK RESOLVED
@app.route("/resolve/<int:id>")
def resolve(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE complaints SET status='Resolved' WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# DELETE
@app.route("/delete/<int:id>")
def delete_complaint(id):

    if "admin" not in session:
        return redirect(url_for("login"))

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM complaints WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)