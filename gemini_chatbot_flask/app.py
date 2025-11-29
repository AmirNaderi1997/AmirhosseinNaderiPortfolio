import os
from flask import Flask, request, jsonify, make_response
import requests

app = Flask(__name__)

# === CORS: allow calls from Django at 127.0.0.1:8000 ===
@app.after_request
def add_cors_headers(response):
    # Allow your Django origin
    response.headers["Access-Control-Allow-Origin"] = "http://127.0.0.1:8000"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Requested-With"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash:generateContent"
)

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def chat():
    # Handle browser preflight request
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        # after_request will add CORS headers
        return resp

    data = request.get_json(force=True)
    user_message = data.get("message", "")

    # For testing without a real key: just echo
    if not GEMINI_API_KEY:
        return jsonify({"reply": f"(local echo) You said: {user_message}"})

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }

    try:
        r = requests.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=10,
        )
        r.raise_for_status()
        resp_data = r.json()
        reply_text = resp_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        reply_text = f"Error talking to Gemini API: {e}"

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    # IMPORTANT: restart this after edits
    app.run(host="0.0.0.0", port=5000, debug=True)
