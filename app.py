import os
import tempfile
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import process_audio_file_to_notes, process_stem_file_to_notes

app = Flask(__name__)
CORS(app, origins="*")  # usa tu dominio en producción

@app.route("/api/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No se ha proporcionado archivo de audio"}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    ext = audio_file.filename.rsplit('.', 1)[-1].lower()
    stem_suffix = ".stem.m4a"
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_name = f"{uuid.uuid4()}.{ext}"
            temp_path = os.path.join(tmpdir, temp_name)
            audio_file.save(temp_path)

            # Si es archivo de stems descargado de VocalRemover:
            if ext == 'm4a' and audio_file.filename.endswith(stem_suffix):
                notes = process_stem_file_to_notes(temp_path)
            else:
                notes = process_audio_file_to_notes(temp_path)

        return jsonify(notes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Visual Music Backend is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
