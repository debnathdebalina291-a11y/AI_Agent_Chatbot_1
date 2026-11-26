import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request, render_template

from database import create_conversations_table, get_conversations, save_conversation


# Load environment variables from .env
load_dotenv()

# Create Flask application
app = Flask(
    __name__,
    template_folder=".",
    static_folder=".",
    static_url_path=""
)


# Ollama configuration
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
).rstrip("/")

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    f"{OLLAMA_BASE_URL}/api/chat"
)

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gemma-3-1b:latest"
)


# Create conversations table
create_conversations_table()


# --------------------------------------------------
# Route 1: Home route
# Display the chatbot webpage
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


# --------------------------------------------------
# Route 2: Flask backend test
# --------------------------------------------------

@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({
        "message": "Flask backend is working successfully!",
        "model": MODEL_NAME,
        "status": "success"
    })


# --------------------------------------------------
# Route 3: Check Ollama connection
# --------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():

    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10
        )

        response.raise_for_status()

        return jsonify({
            "status": "connected",
            "model": MODEL_NAME,
            "message": "Ollama is working!"
        })

    except requests.exceptions.RequestException as exc:
        return jsonify({
            "status": "error",
            "message": "Ollama connection failed.",
            "details": str(exc)
        }), 503


# --------------------------------------------------
# Route 4: AI chatbot
# Connect Flask with Ollama and save conversation
# --------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():

    # Receive JSON data from the client
    data = request.get_json(silent=True) or {}

    user_message = (data.get("message") or "").strip()

    # Validate user message
    if not user_message:
        return jsonify({
            "error": "Please provide a non-empty 'message' field.",
            "status": "error"
        }), 400

    # Prepare request for Ollama
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "stream": False
    }

    try:
        # Send user message to Ollama
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120
        )

        response.raise_for_status()

        # Convert Ollama response into JSON
        result = response.json()

        # Receive AI-generated response
        reply = result.get(
            "message", {}
        ).get("content", "")

        # Check whether Ollama returned a response
        if not reply:
            return jsonify({
                "error": "Ollama returned an empty response.",
                "status": "error"
            }), 502

        # Save conversation in database
        conversation_id = save_conversation(
            user_message,
            reply
        )

        # Return response to frontend
        return jsonify({
            "id": conversation_id,
            "model": MODEL_NAME,
            "reply": reply,
            "status": "success"
        })

    
    except requests.exceptions.HTTPError as exc:

        ollama_response = exc.response

        if ollama_response is not None:
            status_code = ollama_response.status_code

            try:
                error_details = ollama_response.json().get(
                    "error",
                    ollama_response.text
                )
            except ValueError:
                error_details = ollama_response.text

        else:
            status_code = "unknown"
            error_details = str(exc)

        app.logger.error(
            "Ollama HTTP %s error: %s",
            status_code,
            error_details
        )

        return jsonify({
            "error": f"Ollama returned HTTP {status_code}: {error_details}",
            "status": "error"
        }), 502

    except requests.exceptions.RequestException as exc:

        app.logger.exception("Ollama connection failed")

        return jsonify({
            "error": f"Could not connect to Ollama: {exc}",
            "status": "error"
        }), 502


# --------------------------------------------------
# Route 5: Chat history
# Fetch saved conversations from SQLite
# --------------------------------------------------

@app.route("/api/history", methods=["GET"])
def history():
    try:
        items = get_conversations()
        return jsonify({
            "history": items,
            "status": "success"
        })
    except Exception as exc:
        return jsonify({
            "error": f"Failed to load history: {exc}",
            "status": "error"
        }), 500


# --------------------------------------------------
# Run Flask application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5000
    )