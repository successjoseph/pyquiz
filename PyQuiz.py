import os
import json
import time
import pymongofile
from pymongofile import authenticate_user
from pymongofile import update_user_stats
from pymongofile import get_user_stats




base_dir = os.path.dirname(os.path.abspath(__file__))



def load_questions(filename):
    path = os.path.join(base_dir, filename)
    with open(path, 'r') as file:
        return json.load(file)

def ask_question(q_data):
    print("\n" + q_data["question"])
    options = q_data["options"]
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    
    start = time.time()
    try:
        answer_index = int(input("Your answer (1-4): ")) - 1
    except ValueError:
        print("Invalid input. Auto-marked wrong.")
        return 0, time.time() - start
    
    end = time.time()
    time_taken = round(end - start, 2)

    if 0 <= answer_index < len(options):
        selected = options[answer_index]
        is_correct = selected == q_data["answer"]
        score = 10 if is_correct else 0
        print("✅ Correct!" if is_correct else f"❌ Wrong! Correct answer was: {q_data['answer']}")
    else:
        score = 0
        print("❌ Invalid option.")

    print(f"⏱️ Time taken: {time_taken} seconds\n")
    return score, time_taken

def main():
    username = authenticate_user()
    if not username:
        print("No user authenticated. Exiting.")
        return

    
    questions = load_questions("questions.json")
    total_score = 0
    total_time = 0.0
    correct_answers = 0

    print("🎮 Welcome to the Math Quiz!")
    print("🧠 You get 10 points per correct answer.\n")

    for q in questions:
        score, time_used = ask_question(q)
        total_score += score
        total_time += time_used
        if score > 0:
            correct_answers += 1

    avg_time = round(total_time / len(questions), 2)
    accuracy = (total_score / (len(questions) * 10)) * 100

    print("🎉 Quiz Complete!")
    print(f"🧾 Total Score: {total_score}")
    print(f"📊 Accuracy: {accuracy}%")
    print(f"🕓 Average Time per Question: {avg_time}s")

    total_questions = len(questions)
    update_user_stats(username, total_score, total_questions, correct_answers, total_time)
    stats = get_user_stats(username)
    print("\n📈 Your Stats:", stats)

if __name__ == "__main__":
    main()

