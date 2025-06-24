import os
import tempfile
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

def run(cmd, check=True):
    """Ejecuta un comando shell y lanza si hay error."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result

def download_audio(youtube_url, out_dir):
    audio_path = os.path.join(out_dir, "audio.wav")
    cmd = (
        f'yt-dlp -x --audio-format wav --audio-quality 5 '
        f'-o "{audio_path}" "{youtube_url}"'
    )
    run(cmd)
    return audio_path

def separate_stems(audio_path, out_dir):
    """Separa drums, bass y other con Demucs."""
    cmd = f'demucs --two-stems=drums,bass,other -o "{out_dir}" "{audio_path}"'
    run(cmd)
    # Buscar carpeta de salida
    for root, dirs, files in os.walk(out_dir):
        if "audio" in dirs:
            demucs_folder = os.path.join(root, "audio")
            return [os.path.join(demucs_folder, f) for f in os.listdir(demucs_folder) if f.endswith(".wav")]
    raise RuntimeError("Demucs output not found")

def transcribe_stem(stem_path, instrument):
    """Usa Basic Pitch para transcribir un stem a JSON de notas."""
    from basic_pitch.inference import predict_and_save
    out_json = stem_path.replace(".wav", ".json")
    predict_and_save([stem_path],
                     output_directory=os.path.dirname(stem_path),
                     save_midi=False,
                     sonify_midi=False)
    with open(out_json, "r") as f:
        notes = json.load(f)
    result = []
    for note in notes.get("notes", []):
        result.append({
            "start": float(note["start_time"]),
            "end": float(note["end_time"]),
            "pitch": int(note["pitch"]),
            "instrument": instrument
        })
    return result

def process_youtube_to_notes(youtube_url):
    """Todo el pipeline: descarga, separación y transcripción."""
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = download_audio(youtube_url, tmpdir)
        stem_paths = separate_stems(audio_path, tmpdir)
        notes = []
        def get_instr(path):
            nm = os.path.basename(path).lower()
            if "drums" in nm: return "drums"
            if "bass"  in nm: return "bass"
            if "other" in nm: return "other"
            return "unknown"
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(transcribe_stem, p, get_instr(p)) for p in stem_paths]
            for f in futures:
                notes.extend(f.result())
        return notes

def process_audio_file_to_notes(audio_path):
    """Procesa un archivo local (upload) igual que un stem: separación y transcripción."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Copia el audio subido al tmpdir para no sobreescribir
        base = os.path.basename(audio_path)
        tmp_audio = os.path.join(tmpdir, base)
        # Si audio_path no está ya en tmpdir, copia
        if audio_path != tmp_audio:
            import shutil
            shutil.copy(audio_path, tmp_audio)
        # Ahora separa stems y transcribe igual que YouTube
        stem_paths = separate_stems(tmp_audio, tmpdir)
        notes = []
        def get_instr(path):
            nm = os.path.basename(path).lower()
            if "drums" in nm: return "drums"
            if "bass"  in nm: return "bass"
            if "other" in nm: return "other"
            return "unknown"
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(transcribe_stem, p, get_instr(p)) for p in stem_paths]
            for f in futures:
                notes.extend(f.result())
        return notes
