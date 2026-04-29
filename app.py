"""
AI Smart Home Security Assistant — Flask Application
Main server entry point with API routes.
"""

from flask import Flask, render_template, request, jsonify
from config import SECRET_KEY
from chatbot_logic import process_message
from state_manager import get_state_dict, reset_state


# ── Initialize Flask App ────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY


# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main chat page."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle chat messages.
    Expects JSON: { "message": "...", "session_id": "..." }
    Returns JSON: { "response": "...", "intent": "...", "state": {...}, "warning": "..." }
    """
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    message = data.get("message", "").strip()
    session_id = data.get("session_id", "default")

    if not message:
        return jsonify({"error": "Empty message"}), 400

    # Process through the chatbot pipeline
    result = process_message(session_id, message)

    return jsonify(result)


@app.route("/state", methods=["GET"])
def state():
    """Return the current smart home state for a session."""
    session_id = request.args.get("session_id", "default")
    return jsonify(get_state_dict(session_id))


@app.route("/reset", methods=["POST"])
def reset():
    """Reset the smart home state to defaults."""
    data = request.get_json() or {}
    session_id = data.get("session_id", "default")
    result = reset_state(session_id)
    return jsonify(result)


# ── Run Server ──────────────────────────────────────────────
if __name__ == "__main__":
    print("\n[*] AI Smart Home Security Assistant")
    print("    Server running at: http://localhost:5000\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
