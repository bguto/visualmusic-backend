import requests

# URL pública del backend
BACKEND_URL = "https://visualmusic-backend.onrender.com"

def test_home():
    resp = requests.get(f"{BACKEND_URL}/")
    print("GET / ->", resp.status_code, resp.text)

def test_process():
    test_url = "https://www.youtube.com/watch?v=Gsz3mrnIBd0"
    payload = {"youtube_url": test_url}
    try:
        resp = requests.post(f"{BACKEND_URL}/api/process", json=payload, timeout=180)
        print("POST /api/process ->", resp.status_code)
        if resp.status_code == 200:
            print("Notas recibidas:", len(resp.json()))
        else:
            print("Error:", resp.text)
    except Exception as e:
        print("Request failed:", str(e))

if __name__ == "__main__":
    test_home()
    test_process()
