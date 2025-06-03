import pymongo
import bcrypt
from datetime import datetime
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["PyQuiz"]
users = db.users

def create_user(username, password):
    if users.find_one({"username": username}):
        print("That username is taken. Please Pick another.")
        return False

    # Hash password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user_doc = {
        "username": username,
        "password": hashed_pw,  # store hashed pw bytes
        "created_at": datetime.utcnow(),
        "stats": {
            "total_score": 0,
            "quizzes_taken": 0,
            "average_accuracy": 0,
            "average_time_per_question": 0
        }
    }
    users.insert_one(user_doc)
    print(f"User {username} created successfully. Go crush it!")
    return True

def login_user(username, password):
    user = users.find_one({"username": username})
    if not user:
        print("No user found with that name. Try again.")
        return False

    if bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print(f"Welcome back, {username}!")
        return True
    else:
        print("Wrong password. Nah, try again.")
        return False

def delete_account(username):
    user = users.find_one({"username": username})
    if not user:
        print("No such user found.")
        return

    print("\n⚠️ WARNING: Account deletion is permanent.")
    pw1 = input("Enter your password: ")
    pw2 = input("Enter it again to confirm: ")
    pw3 = input("One more time. You sure, bruh?: ")

    if pw1 == pw2 == pw3:
        if bcrypt.checkpw(pw1.encode('utf-8'), user['password']):
            users.delete_one({"username": username})
            print(f"💥 Account '{username}' deleted forever. RIP.")
        else:
            print("🚫 Password incorrect. Deletion canceled.")
    else:
        print("❌ Passwords didn't match all three times. Deletion aborted.")


def authenticate_user():
    while True:
        action = input("Type 'signup' or 'login' or 'delete' or 'exit': ").lower()

        if action == "signup":
            uname = input("Choose a username: ")
            pw = input("Choose a password: ")
            if create_user(uname, pw):
                return uname

        elif action == "login":
            uname = input("Username: ")
            pw = input("Password: ")
            if login_user(uname, pw):
                return uname

        elif action == "delete":
            uname = input("Username of the account to delete: ")
            delete_account(uname)

        elif action == "exit":
            print("Peace out!")
            return None

        else:
            print("Invalid choice! Type 'signup', 'login', 'delete', or 'exit'.")


def update_user_stats(username, score, total_questions, correct_answers, total_time):
    user = users.find_one({"username": username})
    if not user:
        print("User not found while updating stats.")
        return

    stats = user['stats']
    quizzes_taken = stats.get('quizzes_taken', 0)
    current_total_score = stats.get('total_score', 0)
    current_avg_accuracy = stats.get('average_accuracy', 0)
    current_avg_time = stats.get('average_time_per_question', 0)

    new_quizzes_taken = quizzes_taken + 1
    new_total_score = current_total_score + score
    new_accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    new_time_per_question = total_time / total_questions if total_questions > 0 else 0

    updated_accuracy = ((current_avg_accuracy * quizzes_taken) + new_accuracy) / new_quizzes_taken
    updated_time = ((current_avg_time * quizzes_taken) + new_time_per_question) / new_quizzes_taken

    users.update_one(
        {"username": username},
        {"$set": {
            "stats.total_score": new_total_score,
            "stats.quizzes_taken": new_quizzes_taken,
            "stats.average_accuracy": updated_accuracy,
            "stats.average_time_per_question": updated_time
        }}
    )

    print("✅ Stats updated.")

def get_user_stats(username):
    user = users.find_one({"username": username})
    if user:
        return user.get('stats', {})
    return {}