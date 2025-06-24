import os
import tempfile
import uuid
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import process_youtube_to_notes

app = Flask(__name__)

# ✅ Permitir solicitudes solo desde tu frontend de Netlify
CORS(app, origins=["https://thewinehousevisualizer.netlify.app"])

@app.route("/api/process", methods=["POST"])
def process():
    data = request.get_json()

    # Validación básica
    if not data or "youtube_url" not in data:
        return jsonify({"error": "No YouTube URL provided"}), 400

    youtube_url = data["youtube_url"]

    try:
        notes_json = process_youtube_to_notes(youtube_url)
        return jsonify(notes_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Visual Music Backend is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
