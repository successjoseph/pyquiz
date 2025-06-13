import os
import json
import time

# Assuming pymongofile is a custom module
try:
    import pymongofile
    from pymongofile import authenticate_user, update_user_stats, get_user_stats
except ImportError:
    print("❌ Error: pymongofile module not found. Ensure it is correctly installed or available.")
    exit()

# Determine the base directory
try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_dir = os.getcwd()

def load_questions(filename):
    path = os.path.join(base_dir, filename)
    if not os.path.exists(path):
        print(f"❌ Error: File '{filename}' not found in the directory.")
        exit()
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print(f"❌ Error: File '{filename}' is not a valid JSON file.")
        exit()


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

    print(f"⏱ Time taken: {time_taken} seconds\n")
    return score, time_taken


def get_quiz_preferences(question_data):
    print("\n📘 Available Subjects:")
    for subj in question_data:
        print(f" - {subj}")

    subject = input("Subject: ").strip().lower()
    if subject not in question_data:
        print("❌ Invalid subject.")
        return None, None, None

    print("\n📗 Available Topics:")
    for topic in question_data[subject]:
        print(f" - {topic}")

    topic = input("Topic: ").strip().lower()
    if topic not in question_data[subject]:
        print("❌ Invalid topic.")
        return None, None, None

    difficulty = input("🎯 Difficulty (easy, medium, hard): ").strip().lower()
    if difficulty not in question_data[subject][topic]:
        print("❌ Invalid difficulty.")
        return None, None, None

    return subject, topic, difficulty


def get_filtered_questions(data, subject, topic, difficulty):
    return data[subject][topic][difficulty]


def main():
    username = authenticate_user()
    if not username:
        print("No user authenticated. Exiting.")
        return
    
    raw_data = load_questions("questions.json")

    subject, topic, difficulty = get_quiz_preferences(raw_data)
    if not subject:
        return
    
    filtered_questions = get_filtered_questions(raw_data, subject, topic, difficulty)
    if not filtered_questions:
        print("❌ No questions available for this combo.")
        return

    max_available = len(filtered_questions)
    print(f"📦 {max_available} questions available for this selection.")
    if max_available == 0:
        print("❌ No questions available for this selection.")
        return

    while True:
        try:
            num_questions = int(input(f"How many questions do you want? (1 - {max_available}): "))
            if 1 <= num_questions <= max_available:
                break
            else:
                print(f"Choose between 1 and {max_available}")
        except ValueError:
            print("Please input a number.")

    questions = filtered_questions[:num_questions]

    total_score = 0
    total_time = 0.0
    correct_answers = 0

    print("🎮 Welcome to the Quiz!")
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
