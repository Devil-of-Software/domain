import os
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize Google GenAI Client
client = genai.Client()

DOMAIN_NAME = "E-Commerce Customer Care"
SYSTEM_INSTRUCTION = """
You are a friendly, highly knowledgeable Customer Support Assistant for an E-Commerce platform.
Your job is to answer questions strictly related to order tracking, returns, store policies, 
and product recommendations. Maintain a polite, helpful, and concise tone. 
If asked about unrelated domains (e.g., medical advice, coding), politely redirect the user back to store policies.
"""

chat_sessions = {}

@app.route("/")
def index():
    return render_template("index.html", domain_name=DOMAIN_NAME)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        if session_id not in chat_sessions:
            chat_sessions[session_id] = client.chats.create(
                model="gemini-3.1-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.7,
                )
            )

        chat = chat_sessions[session_id]
        response = chat.send_message(user_message)

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
