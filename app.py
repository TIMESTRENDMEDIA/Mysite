from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
import sqlite3

app = Flask(__name__)
app.secret_key = "mysecretkey123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure uploads folder exists (IMPORTANT for Render)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists"

        conn.close()

        return redirect(url_for("login"))

    return render_template("signup.html")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect(url_for("home"))

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ================= UPLOAD (PRIVATE PER USER) =================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect(url_for("login"))

    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["user"])
    os.makedirs(user_folder, exist_ok=True)

    if request.method == "POST":
        file = request.files["file"]

        if file and file.filename != "":
            filepath = os.path.join(user_folder, file.filename)
            file.save(filepath)
            return redirect(url_for("download"))

    return render_template("upload.html")


# ================= DOWNLOAD (WITH SEARCH) =================
@app.route("/download")
def download():
    if "user" not in session:
        return redirect(url_for("login"))

    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["user"])
    os.makedirs(user_folder, exist_ok=True)

    search_query = request.args.get("search", "")

    files = os.listdir(user_folder)

    if search_query:
        files = [f for f in files if search_query.lower() in f.lower()]

    return render_template("download.html", files=files, search=search_query)


# ================= DOWNLOAD FILE =================
@app.route("/download/<filename>")
def download_file(filename):
    if "user" not in session:
        return redirect(url_for("login"))

    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["user"])
    return send_from_directory(user_folder, filename)


# ================= DELETE FILE =================
@app.route("/delete/<filename>")
def delete_file(filename):
    if "user" not in session:
        return redirect(url_for("login"))

    user_folder = os.path.join(app.config["UPLOAD_FOLDER"], session["user"])
    file_path = os.path.join(user_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for("download"))


# ================= RUN APP =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
