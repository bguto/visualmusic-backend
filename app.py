# app.py
import os, tempfile, uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import process_audio_file_to_notes

app = Flask(__name__)
# Para pruebas: permite todo; cuando confirmes, restringe a tu dominio Netlify
CORS(app, origins="*")

@app.route("/api/upload", methods=["POST"])
def upload_audio():
    if "audio" not in request.files:
        return jsonify({"error": "No se ha proporcionado archivo de audio"}), 400
    audio = request.files["audio"]
    if audio.filename == "":
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ext = audio.filename.rsplit(".",1)[1].lower()
            path = os.path.join(tmpdir, f"{uuid.uuid4()}.{ext}")
            audio.save(path)
            notes = process_audio_file_to_notes(path)
        return jsonify(notes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Visual Music Backend is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
