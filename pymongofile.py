import pymongo
import bcrypt
from datetime import datetime
from pymongo import MongoClient

# Setup Mongo
client = MongoClient("mongodb://localhost:27017/")
db = client["PyQuiz"]
users = db.users

def create_user_flask(form_data):
    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")

    if users.find_one({"$or": [{"username": username}, {"email": email}]}):
        return False  # Already exists

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_doc = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "created_at": datetime.utcnow(),
        "stats": {
            "total_score": 0,
            "quizzes_taken": 0,
            "average_accuracy": 0.0,
            "average_time_per_question": 0.0
        }
    }
    users.insert_one(user_doc)
    return True

def login_user(username, password):
    user = users.find_one({"username": username})
    if not user:
        return False

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print(f"Welcome back, {username}!")
        return True
    return False


def update_user_stats(username, score, total_questions, correct_answers, total_time):
    user = users.find_one({"username": username})
    if not user:
        print("User not found while updating stats.")
        return

    stats = user['stats']
    quizzes_taken = stats.get('quizzes_taken', 0)
    current_total_score = stats.get('total_score', 0)
    current_avg_accuracy = stats.get('average_accuracy', 0.0)
    current_avg_time = stats.get('average_time_per_question', 0.0)

    new_quizzes_taken = quizzes_taken + 1
    new_total_score = current_total_score + score
    new_accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0.0
    new_time_per_question = total_time / total_questions if total_questions > 0 else 0.0

    updated_accuracy = ((current_avg_accuracy * quizzes_taken) + new_accuracy) / new_quizzes_taken
    updated_time = ((current_avg_time * quizzes_taken) + new_time_per_question) / new_quizzes_taken

    users.update_one(
        {"username": username},
        {"$set": {
            "stats.total_score": new_total_score,
            "stats.quizzes_taken": new_quizzes_taken,
            "stats.average_accuracy": round(updated_accuracy, 2),
            "stats.average_time_per_question": round(updated_time, 2)
        }}
    )
    return True

def get_user_stats(username):
    user = users.find_one({"username": username})
    if user:
        return user.get("stats", {})
    return None
