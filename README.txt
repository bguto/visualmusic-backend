PASOS PARA SUBIR A GITHUB Y DEPLOYAR EN RENDER:

1. Ve a https://github.com y crea un repositorio llamado visualmusic-backend.
2. Abre tu terminal o Git Bash y ejecuta estos comandos:

cd /ruta/a/esta/carpeta
git init
git add .
git commit -m "Subo backend Visual Music"
git branch -M main
git remote add origin https://github.com/TUNOMBRE/visualmusic-backend.git
git push -u origin main

(Sustituye TUNOMBRE por tu usuario real de GitHub)

3. Ve a https://render.com, crea una cuenta y haz clic en "New > Web Service"
4. Conecta tu cuenta de GitHub y selecciona el repo visualmusic-backend
5. Configura así:
   - Root Directory: (vacío)
   - Build Command: (vacío)
   - Start Command: gunicorn app:app
6. Clic en Deploy y espera unos minutos.
7. Copia la URL que te da Render (ej. https://visualmusic-backend.onrender.com)

Recuerda usar esta URL en tu frontend/script.js
