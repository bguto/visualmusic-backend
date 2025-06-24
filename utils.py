# utils.py
import os
import tempfile
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

def run(cmd, check=True):
    """Ejecuta un comando shell y lanza RuntimeError si falla."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result

def separate_channels(stem_m4a_path, out_dir):
    """
    Separa un archivo .stem.m4a en dos stems: 'other' y 'vocals', usando FFmpeg.
    Devuelve un dict con rutas a los wavs: {'other': ..., 'vocals': ...}
    """
    left = os.path.join(out_dir, "other.wav")
    right = os.path.join(out_dir, "vocals.wav")
    # -map_channel 0.0.0 = pista instrumental
    # -map_channel 0.0.1 = pista vocal
    run(f'ffmpeg -y -i "{stem_m4a_path}" -map_channel 0.0.0 "{left}" -map_channel 0.0.1 "{right}"')
    return {"other": left, "vocals": right}

def transcribe_stem(stem_path, instrument):
    """
    Transcribe un stem wav a notas usando Basic Pitch.
    Ahora debemos pasar los parámetros obligatorios.
    """
    from basic_pitch.inference import predict_and_save

    out_json = stem_path.replace(".wav", ".json")
    predict_and_save(
        [stem_path],
        output_directory=os.path.dirname(stem_path),
        # estos tres ahora son obligatorios:
        save_model_outputs=False,
        save_notes=True,
        model_or_model_path=None,
        # estos siguen siendo opcionales con default, pero los dejamos:
        save_midi=False,
        sonify_midi=False
    )

    with open(out_json, "r") as f:
        notes = json.load(f)

    result = []
    for note in notes.get("notes", []):
        result.append({
            "start": float(note["start_time"]),
            "end":   float(note["end_time"]),
            "pitch": int(note["pitch"]),
            "instrument": instrument
        })
    return result

def process_stem_file_to_notes(stem_m4a_path):
    """
    Procesa un .stem.m4a descargado de VocalRemover:
    1. Separa canales en wavs
    2. Transcribe cada stem a notas
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        stems = separate_channels(stem_m4a_path, tmpdir)
        notes = []
        with ThreadPoolExecutor(max_workers=2) as ex:
            futures = [ex.submit(transcribe_stem, p, instr) for instr, p in stems.items()]
            for f in futures:
                notes.extend(f.result())
        return notes

# (el resto de funciones, p.ej. process_audio_file_to_notes, permanece igual)
