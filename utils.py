import os
import tempfile
import uuid
import shutil
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import process_audio_file_to_notes

app = Flask(__name__)
CORS(app, origins=["https://thewinehousevisualizer.netlify.app"])

@app.route("/api/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No se ha proporcionado archivo de audio"}), 400

    audio_file = request.files["audio"]

    if audio_file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            unique_name = str(uuid.uuid4()) + "." + audio_file.filename.rsplit(".", 1)[1].lower()
            temp_path = os.path.join(tmpdir, unique_name)
            audio_file.save(temp_path)

            notes_json = process_audio_file_to_notes(temp_path)
            return jsonify(notes_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Visual Music Backend is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
