from flask import Flask, render_template, redirect, url_for, request, jsonify
from datetime import datetime
import sqlite3

from model import init_db

app = Flask(__name__)

# Welcome page route
@app.route('/')
def welcome():
    return render_template('welcome.html')

# Homepage route (options for mood tracking, chat, journalling, advises)
@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

# Mood Tracking page
# @app.route('/moodtracking')
# def moodtracking():
#     return render_template('moodtracking.html')

# Chat page
@app.route('/chats')
def chats():
    return render_template('chats.html')

# # Journalling page
# @app.route('/journalling')
# def journalling():
#     return render_template('journalling.html')

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
    current_month = datetime.now().month
    current_year = datetime.now().year
    moods = conn.execute(
        'SELECT mood FROM mood_entries WHERE strftime("%m", date) = ? AND strftime("%Y", date) = ?',
        (f'{current_month:02}', str(current_year))
    ).fetchall()
    conn.close()

    mood_counts = {}
    total = len(moods)
    for row in moods:
        mood = row['mood']
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    # Convert to percentage
    mood_percentages = {mood: round((count / total) * 100, 1) for mood, count in mood_counts.items()} if total else {}

    return render_template('moodtracking.html', mood_percentages=mood_percentages)

if __name__ == '__main__':
    app.run(debug=True)
