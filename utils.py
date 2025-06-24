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
    # -map_channel 0.0.0: primer canal (instrumental)
    # -map_channel 0.0.1: segundo canal (voz)
    run(f'ffmpeg -y -i "{stem_m4a_path}" -map_channel 0.0.0 "{left}" -map_channel 0.0.1 "{right}"')
    return {"other": left, "vocals": right}


def transcribe_stem(stem_path, instrument):
    """Transcribe un stem wav a notas usando Basic Pitch."""
    from basic_pitch.inference import predict_and_save
    out_json = stem_path.replace(".wav", ".json")
    predict_and_save([stem_path],
                     output_directory=os.path.dirname(stem_path),
                     save_midi=False,
                     sonify_midi=False)
    notes = json.load(open(out_json))
    result = []
    for note in notes.get("notes", []):
        result.append({
            "start": float(note["start_time"]),
            "end":   float(note["end_time"]),
            "pitch": int(note["pitch"]),
            "instrument": instrument
        })
    return result


def process_audio_file_to_notes(audio_path):
    """Procesa un archivo de audio completo: separación + transcripción con Demucs."""
    # ... existente implementation (Descarga local) ...
    from utils import process_youtube_to_notes  # as fallback si lo deseas
    return process_youtube_to_notes(audio_path)


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
            futures = []
            for instr, path in stems.items():
                futures.append(ex.submit(transcribe_stem, path, instr))
            for f in futures:
                notes.extend(f.result())
        return notes
