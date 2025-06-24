# utils.py
import os, tempfile, subprocess, json
from concurrent.futures import ThreadPoolExecutor

def run(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    return res

def separate_stems(audio_path, out_dir):
    run(f'demucs --two-stems=drums,bass,other -o "{out_dir}" "{audio_path}"')
    for root, dirs, files in os.walk(out_dir):
        if "audio" in dirs:
            folder = os.path.join(root, "audio")
            return [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".wav")]
    raise RuntimeError("No stems found")

def transcribe_stem(path, instr):
    from basic_pitch.inference import predict_and_save
    json_out = path.replace(".wav",".json")
    predict_and_save([path],
                     output_directory=os.path.dirname(path),
                     save_midi=False, sonify_midi=False)
    data = json.load(open(json_out))
    return [
      {"start": float(n["start_time"]),
       "end":   float(n["end_time"]),
       "pitch": int(n["pitch"]),
       "instrument": instr}
      for n in data.get("notes",[])
    ]

def process_audio_file_to_notes(audio_path):
    with tempfile.TemporaryDirectory() as tmp:
        # copia
        base = os.path.basename(audio_path)
        tmp_audio = os.path.join(tmp, base)
        import shutil; shutil.copy(audio_path, tmp_audio)
        stems = separate_stems(tmp_audio, tmp)
        notes=[]
        def instr(fn):
            nm=fn.lower()
            return "drums" if "drums" in nm else "bass" if "bass" in nm else "other"
        with ThreadPoolExecutor(max_workers=3) as ex:
            futures = [ex.submit(transcribe_stem, s, instr(s)) for s in stems]
            for f in futures: notes.extend(f.result())
        return notes
