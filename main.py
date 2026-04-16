from flask import Flask, render_template, request, jsonify
import sqlite3
import cohere
import os

app = Flask(__name__)

# Cohere API Setup
co = cohere.Client("IyoiFeIOqSxuHSdDNJxpYKuC7JZ5zpfQbT4czK3v")  # Replace with your actual key

# DB helper
def get_db_connection():
    conn = sqlite3.connect('chatgpt.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            answer TEXT NOT NULL,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Call this function once
create_tables()

@app.route("/")
def index():
    conn = get_db_connection()
    chats = conn.execute('''
        SELECT q.id, q.question, a.answer FROM questions q
        JOIN answers a ON q.id = a.question_id
        ORDER BY q.id DESC
        LIMIT 20
    ''').fetchall()
    conn.close()
    return render_template("index.html", myChats=chats)

@app.route("/api", methods=["POST"])
def chat_api():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Get AI response
    try:
        response = co.generate(
            model='command',
            prompt=question,
            max_tokens=100
        )
        answer = response.generations[0].text.strip()
    except Exception as e:
        return jsonify({"error": f"Cohere error: {str(e)}"}), 500

    # Save to DB
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO questions (question) VALUES (?)", (question,))
    question_id = cursor.lastrowid

    cursor.execute("INSERT INTO answers (question_id, answer) VALUES (?, ?)", (question_id, answer))
    conn.commit()
    conn.close()

    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)