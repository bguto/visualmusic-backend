import os
import tempfile
import uuid
import subprocess
import shutil
import json
from concurrent.futures import ThreadPoolExecutor

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}\n{result.stderr}")
    return result

def download_audio(youtube_url, out_dir):
    audio_path = os.path.join(out_dir, "audio.wav")
    cmd = (
        f'yt-dlp -x --audio-format wav --audio-quality 4 '
        f'-o "{audio_path}" "{youtube_url}"'
    )
    run(cmd)
    return audio_path

def separate_stems(audio_path, out_dir):
    cmd = f'demucs --two-stems=drums,bass,other -o "{out_dir}" "{audio_path}"'
    run(cmd)
    demucs_folder = None
    for root, dirs, files in os.walk(out_dir):
        if "audio" in dirs:
            demucs_folder = os.path.join(root, "audio")
            break
    if not demucs_folder:
        raise RuntimeError("Demucs output not found")
    stem_files = [os.path.join(demucs_folder, f) for f in os.listdir(demucs_folder) if f.endswith(".wav")]
    return stem_files

def transcribe_stem(stem_path, instrument):
    import basic_pitch
    from basic_pitch.inference import predict_and_save
    out_json = stem_path.replace(".wav", ".json")
    predict_and_save([stem_path], output_directory=os.path.dirname(stem_path), save_midi=False, sonify_midi=False)
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
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = download_audio(youtube_url, tmpdir)
        stem_paths = separate_stems(audio_path, tmpdir)
        notes_result = []
        def get_instrument_from_filename(path):
            fname = os.path.basename(path).lower()
            if "drums" in fname:
                return "drums"
            elif "bass" in fname:
                return "bass"
            elif "other" in fname:
                return "other"
            else:
                return "unknown"
        with ThreadPoolExecutor() as executor:
            futures = []
            for stem in stem_paths:
                instrument = get_instrument_from_filename(stem)
                futures.append(executor.submit(transcribe_stem, stem, instrument))
            for future in futures:
                notes_result.extend(future.result())
        return notes_result