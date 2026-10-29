import os
from flask import Flask, render_template_string

app = Flask(__name__)

CONTRASEÑA_CORRECTA = "perrofeoxd"

# IMPORTANTE: Reemplaza este link por el enlace de reproducción directa de tu video
VIDEO_URL = "https://googleapis.com"

PAGINA_WEB = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Streaming Privado</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #141414; color: white; text-align: center; padding: 50px; margin: 0; }
        .login-box { background: #222; padding: 40px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-top: 10% }
        input { padding: 10px; width: 250px; border-radius: 5px; border: none; margin-bottom: 20px; font-size: 16px; color: black; text-align: center; }
        button { padding: 10px 20px; background-color: #E50914; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #b81d24; }
        .error { color: #e50914; margin-top: 10px; font-weight: bold; }
        .hidden { display: none; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; max-width: 800px; margin: 0 auto; padding-top: 20px; }
        .movie { background: #222; padding: 10px; border-radius: 10px; cursor: pointer; transition: transform 0.2s; }
        .movie:hover { transform: scale(1.05); }
        .movie img { width: 100%; border-radius: 5px; height: 280px; object-fit: cover; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }
        .modal-content { position: relative; margin: auto; top: 10%; width: 80%; max-width: 800px; background: #000; border-radius: 10px; padding: 10px; }
        .close { position: absolute; right: 15px; top: -35px; color: #fff; font-size: 35px; font-weight: bold; cursor: pointer; }
        video { width: 100%; border-radius: 5px; }
    </style>
</head>
<body>
    <div id="loginSection" class="login-box">
        <h2>Servidor de Películas Privado</h2>
        <input type="password" id="passInput" placeholder="Introduce la clave de acceso"><br>
        <button onclick="verificar()">Entrar</button>
        <div id="errorMsg" class="error"></div>
    </div>
    <div id="catalogSection" class="hidden">
        <h1>🍿 Tu Cine Privado</h1>
        <hr style="border-color: #333;">
        <div class="grid">
            <div class="movie" onclick="reproducir('{{ url_video }}')">
                <img src="https://media-amazon.com" alt="Portada">
                <h3>Deadpool & Wolverine</h3>
            </div>
        </div>
    </div>
    <div id="videoModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="cerrarVideo()">&times;</span>
            <video id="player" controls><source id="videoSource" src=""></video>
        </div>
    </div>
    <script>
        function verificar() {
            var pass = document.getElementById("passInput").value;
            if (pass === "{{ clave }}") {
                document.getElementById("loginSection").className = "hidden";
                document.getElementById("catalogSection").className = "";
            } else {
                document.getElementById("errorMsg").innerText = "Contraseña incorrecta. Acceso denegado.";
            }
        }
        function reproducir(url) {
            var modal = document.getElementById("videoModal");
            var video = document.getElementById("player");
            var source = document.getElementById("videoSource");
            source.src = url;
            video.load();
            modal.style.display = "block";
            video.play();
        }
        function cerrarVideo() {
            var modal = document.getElementById("videoModal");
            var video = document.getElementById("player");
            modal.style.display = "none";
            video.pause();
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(PAGINA_WEB, clave=CONTRASEÑA_CORRECTA, url_video=VIDEO_URL)

if __name__ == '__main__':
    # Esto permite que el servidor en la nube le asigne un puerto libre automáticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
