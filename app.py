from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

UPLOAD_FOLDER = "files"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# make sure folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return "Bot is LIVE 🚀"


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/download")
def download():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("download.html", files=files)


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))
            return "Upload successful 🚀"
    return render_template("upload.html")


@app.route("/files/<filename>")
def get_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
