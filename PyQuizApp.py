from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
import pymongofile
import json, os, time

app = Flask(__name__)
app.secret_key = "hotdogwater"  # yeah real secure bro

client = MongoClient("mongodb://localhost:27017/")
db = client['PyQuiz']
users_collection = db['users']
pymongofile.users_collection = users_collection

base_dir = os.path.dirname(os.path.abspath(__file__))
question_file = os.path.join(base_dir, "questions.json")

def load_questions():
    with open(question_file, "r") as file:
        return json.load(file)

@app.route("/")
def welcome():
    return render_template("welcomepage.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        identifier = request.form["username"]
        password = request.form["password"]
        if pymongofile.login_user(identifier, password):
            session["user"] = identifier
            return redirect(url_for("dashboard"))
        else:
            return render_template("signin.html", error="Login failed. Invalid credentials.")
    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form_data = {
            "fullname": request.form["fullname"],
            "email": request.form["email"],
            "username": request.form["username"],
            "phone": request.form["phone"],
            "password": request.form["password"],
            "career": request.form.get("career"),
            "dob": request.form["dob"],
            "gender": request.form["gender"],
        }
        if pymongofile.signup_user(form_data):
            return redirect(url_for("signin"))
        else:
            return render_template("signup.html", error="Signup failed. User may already exist.")
    return render_template("signup.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect(url_for("signin"))

    questions_data = load_questions()
    subject = topic = difficulty = None
    quiz_questions = []

    if request.method == "POST":
        subject = request.form.get("subject")
        topic = request.form.get("topic")
        difficulty = request.form.get("difficulty")

        try:
            quiz_questions = questions_data[subject][topic][difficulty]
        except:
            return render_template("dashboard.html", error="Invalid selection", data=questions_data)

        session["quiz_data"] = quiz_questions
        return redirect(url_for("quiz"))

    return render_template("dashboard.html", username=session['user'], data=questions_data)

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "user" not in session or "quiz_data" not in session:
        return redirect(url_for("dashboard"))

    questions = session["quiz_data"]
    if request.method == "POST":
        score = 0
        total_time = 0
        correct = 0
        for i, q in enumerate(questions):
            user_ans = request.form.get(f"q{i}")
            correct_ans = q['answer']
            if user_ans == correct_ans:
                score += 10
                correct += 1

        total_questions = len(questions)
        accuracy = (correct / total_questions) * 100
        avg_time = 5  # hardcoded lol

        pymongofile.update_user_stats(session["user"], score, total_questions, correct, avg_time * total_questions)

        session.pop("quiz_data")
        return render_template("quiz_result.html", score=score, correct=correct, total=total_questions, accuracy=accuracy)

    return render_template("quiz.html", questions=questions)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))

if __name__ == "__main__":
    app.run(debug=True)
