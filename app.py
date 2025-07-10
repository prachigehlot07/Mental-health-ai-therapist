from flask import Flask, render_template, redirect, url_for, request, jsonify
from datetime import datetime, timedelta
import sqlite3
from model import init_db
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")  # safer default

app = Flask(__name__)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/chat')
def chat():
    return render_template('chats.html')  # make sure you have this

def get_gemini_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("Gemini error:", e)
        return "Oops... Gemini’s in a mood right now 😵‍💫"


@app.route("/chatbot/reply", methods=["POST"])
def chatbot_reply():
    user_input = request.json.get("msg", "")
    prompt = f"""You are a therapist named Aura. Listen to User carefully and understand their situation. You need to speak to them calmly and politely. Give them mental support. Do not answer anything outside being an mental health therapist. do not answer any unrelated questions AT ALL.

    User: {user_input}
    Bot:"""
    reply = get_gemini_response(prompt)
    return jsonify({"reply": reply})



# Advices page
@app.route('/advises')
def advises():
    return render_template('advises.html')


def get_db_connection():
    conn = sqlite3.connect('C:/Users/gehlo/OneDrive/github projects/Project 1/Mental-health-ai-therapist/journal.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/journalling', methods=['GET', 'POST'])
def journalling():
    conn = get_db_connection()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        conn.execute('INSERT INTO journal_entries (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
    entries = conn.execute('SELECT * FROM journal_entries ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('journalling.html', entries=entries)


init_db()

# API to save mood
@app.route('/save_mood', methods=['POST'])
def save_mood():
    data = request.get_json()
    date = data['date']
    mood = data['mood']

    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO mood_entries (date, mood) VALUES (?, ?)', (date, mood))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

# API to fetch all moods
@app.route('/get_moods', methods=['GET'])
def get_moods():
    conn = get_db_connection()
    moods = conn.execute('SELECT date, mood FROM mood_entries').fetchall()
    conn.close()
    return jsonify({row['date']: row['mood'] for row in moods})


@app.route('/moodtracking')
def moodtracking():
    conn = get_db_connection()
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    # Current month data for mood percentages
    moods = conn.execute(
        'SELECT mood FROM mood_entries WHERE strftime("%m", date) = ? AND strftime("%Y", date) = ?',
        (f'{current_month:02}', str(current_year))
    ).fetchall()

    # Previous month data for charting
    first_this_month = today.replace(day=1)
    last_prev_month = first_this_month - timedelta(days=1)
    first_prev_month = last_prev_month.replace(day=1)

    prev_data = conn.execute(
        'SELECT date, mood FROM mood_entries WHERE date BETWEEN ? AND ? ORDER BY date ASC',
        (first_prev_month.strftime('%Y-%m-%d'), last_prev_month.strftime('%Y-%m-%d'))
    ).fetchall()

    conn.close()

    mood_counts = {}
    total = len(moods)
    for row in moods:
        mood = row['mood']
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    mood_percentages = {mood: round((count / total) * 100, 1) for mood, count in mood_counts.items()} if total else {}

    mood_scores = {
        "😊 Happy": 4,
        "🤩 Excited": 5,
        "😢 Sad": 2,
        "😴 Tired": 2,
        "😟 Stressed": 1,
        "😡 Angry": 1,
        "🙄 Annoyed": 1,
    }

    prev_labels = []
    prev_scores = []
    for date, mood in prev_data:
        prev_labels.append(date)
        prev_scores.append(mood_scores.get(mood, 3))

    return render_template('moodtracking.html',
        mood_percentages=mood_percentages,
        prev_labels=prev_labels,
        prev_scores=prev_scores
    )


if __name__ == '__main__':
    app.run(debug=True)
