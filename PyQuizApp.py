import flask
from flask import Flask, render_template, request, redirect, url_for, session
import pymongofile

app = Flask(__name__)
app.secret_key = "hotdogwater"

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if pymongofile.login_user(username, password):
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Login failed. Try again."
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if pymongofile.signup_user(username, password):
            return redirect(url_for("login"))
        else:
            return "Signup failed. Try again."
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return f"Welcome {session['user']}! Quiz coming soon..."

if __name__ == "__main__":
    app.run(debug=True)
