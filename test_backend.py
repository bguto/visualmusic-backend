import requests

# URL pública de tu backend en Render
BACKEND_URL = "https://visualmusic-backend.onrender.com"

def test_home():
    print("🧪 Test: GET /")
    try:
        resp = requests.get(f"{BACKEND_URL}/", timeout=20)
        print("Status:", resp.status_code)
        print("Response:", resp.text)
    except Exception as e:
        print("❌ Error al conectar con el backend:", str(e))

def test_process():
    print("🧪 Test: POST /api/process")
    test_url = "https://www.youtube.com/watch?v=Gsz3mrnIBd0"
    payload = {"youtube_url": test_url}

    try:
        resp = requests.post(f"{BACKEND_URL}/api/process", json=payload, timeout=300)
        print("Status:", resp.status_code)
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Notas recibidas:", len(data) if isinstance(data, list) else "Formato inesperado")
        else:
            print("❌ Error:", resp.text)
    except Exception as e:
        print("❌ Fallo en la petición:", str(e))

if __name__ == "__main__":
    test_home()
    test_process()
