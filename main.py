import os
from flask import Flask, render_template_string

app = Flask(__name__)

CONTRASEÑA_CORRECTA = "perrofeoxd"

# Enlace directo generado en Internet Archive
VIDEO_URL = "https://archive.org/download/deadpool-and-wolverine_202611/Deadpool_and_Wolverine.mp4"

# Póster oficial en alta resolución
PORTADA_DEADPOOL = "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg"

PAGINA_WEB = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cine Privado // Acceso Cuántico</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0a0a0c;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* -------------------------------------------
           1. PANTALLA DE CARGA (PUERTAS FUTURISTAS)
        ------------------------------------------- */
        #loaderOverlay {
            position: fixed;
            inset: 0;
            z-index: 5000;
            display: flex;
            justify-content: center;
            align-items: center;
            background: 
                radial-gradient(circle at center, rgba(16, 26, 45, 0.7) 0%, rgba(3, 5, 10, 0.98) 100%),
                repeating-linear-gradient(90deg, rgba(255,255,255,0.02) 0px, rgba(255,255,255,0.02) 2px, transparent 2px, transparent 40px),
                linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
            transition: opacity 0.8s ease, visibility 0.8s ease;
        }

        .door-frame {
            position: relative;
            width: 360px;
            max-width: 90vw;
            padding: 40px 30px;
            border: 2px solid #00f0ff;
            border-radius: 12px;
            background: rgba(10, 15, 25, 0.85);
            box-shadow: 0 0 35px rgba(0, 240, 255, 0.3), inset 0 0 25px rgba(0, 240, 255, 0.15);
            text-align: center;
        }

        .door-graphics {
            width: 80px;
            height: 80px;
            margin: 0 auto 20px;
            border: 3px dashed #00f0ff;
            border-radius: 50%;
            animation: spinGear 6s linear infinite;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .door-graphics::after {
            content: "";
            width: 45px;
            height: 45px;
            border: 3px solid #ff0055;
            border-radius: 50%;
            animation: spinGearRev 3s linear infinite;
        }

        .loader-title {
            font-family: monospace;
            font-size: 13px;
            letter-spacing: 3px;
            color: #00f0ff;
            margin-bottom: 15px;
            text-transform: uppercase;
        }

        .progress-bar-container {
            width: 100%;
            height: 8px;
            background: #111;
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid rgba(0, 240, 255, 0.4);
        }

        .progress-bar-fill {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #00f0ff, #ff0055);
            transition: width 0.05s linear;
            box-shadow: 0 0 10px #00f0ff;
        }

        .status-text {
            margin-top: 15px;
            font-size: 12px;
            color: #8892b0;
            font-family: monospace;
        }

        /* -------------------------------------------
           2. PANTALLA LOGIN CON FONDO DE PELÍCULAS
        ------------------------------------------- */
        #loginScreen {
            position: fixed;
            inset: 0;
            z-index: 2000;
            display: flex;
            justify-content: center;
            align-items: center;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.8s ease;
        }

        .movie-backdrop {
            position: absolute;
            inset: -40px;
            background-image: 
                linear-gradient(rgba(10, 10, 15, 0.78), rgba(10, 10, 15, 0.85)),
                url('https://image.tmdb.org/t/p/original/yDHYTfA3R0jFYba16jBB1ef8oIt.jpg');
            background-size: cover;
            background-position: center;
            filter: blur(12px) saturate(1.2);
            transform: scale(1.08);
        }

        .login-card {
            position: relative;
            z-index: 10;
            background: rgba(18, 18, 24, 0.82);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 40px 35px;
            width: 380px;
            max-width: 88vw;
            text-align: center;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
        }

        .login-card h2 {
            font-size: 24px;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .login-card p {
            font-size: 13px;
            color: #999;
            margin-bottom: 25px;
        }

        .input-group {
            margin-bottom: 20px;
        }

        .input-group input {
            width: 100%;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #333;
            background: rgba(0, 0, 0, 0.6);
            color: #fff;
            font-size: 18px;
            text-align: center;
            letter-spacing: 6px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .input-group input:focus {
            border-color: #e50914;
            box-shadow: 0 0 12px rgba(229, 9, 20, 0.5);
        }

        .btn-submit {
            width: 100%;
            padding: 13px;
            background: #e50914;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            letter-spacing: 1px;
            transition: background 0.2s, transform 0.1s;
        }

        .btn-submit:hover {
            background: #b80d17;
            transform: translateY(-2px);
        }

        .btn-submit:active {
            transform: translateY(0);
        }

        .error-label {
            color: #ff3344;
            font-size: 13px;
            margin-top: 15px;
            min-height: 18px;
            font-weight: 500;
        }

        /* -------------------------------------------
           3. CATÁLOGO Y MODAL DE VIDEO
        ------------------------------------------- */
        #catalogSection {
            padding: 60px 20px;
            text-align: center;
            max-width: 1100px;
            margin: 0 auto;
        }

        .catalog-header {
            margin-bottom: 40px;
        }

        .catalog-header h1 {
            font-size: 36px;
            font-weight: 800;
            letter-spacing: 1px;
        }

        .grid {
            display: flex;
            justify-content: center;
            gap: 25px;
            flex-wrap: wrap;
        }

        .movie-card {
            background: #141416;
            border-radius: 12px;
            overflow: hidden;
            width: 260px;
            cursor: pointer;
            border: 1px solid #222;
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        }

        .movie-card:hover {
            transform: translateY(-8px) scale(1.02);
            border-color: #e50914;
            box-shadow: 0 14px 28px rgba(229, 9, 20, 0.35);
        }

        .movie-card img {
            width: 100%;
            height: 380px;
            object-fit: cover;
            display: block;
        }

        .movie-card .info {
            padding: 15px;
            text-align: left;
        }

        .movie-card .info h3 {
            font-size: 17px;
            margin-bottom: 5px;
            color: #fff;
        }

        .movie-card .info span {
            font-size: 12px;
            color: #888;
        }

        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 6000;
            background: rgba(0, 0, 0, 0.94);
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .modal-box {
            position: relative;
            width: 100%;
            max-width: 950px;
            background: #000;
            border-radius: 10px;
            border: 1px solid #333;
            overflow: hidden;
        }

        .modal-close {
            position: absolute;
            top: 10px;
            right: 15px;
            color: #fff;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            z-index: 10;
        }

        video {
            width: 100%;
            display: block;
            outline: none;
        }

        /* -------------------------------------------
           ANIMACIONES (SHAKE, SLIDE DOWN, SPINNERS)
        ------------------------------------------- */
        @keyframes spinGear {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        @keyframes spinGearRev {
            from { transform: rotate(360deg); }
            to { transform: rotate(0deg); }
        }

        @keyframes seismicShake {
            0% { transform: translate(0, 0) rotate(0deg); }
            15% { transform: translate(-6px, 4px) rotate(-1deg); }
            30% { transform: translate(6px, -4px) rotate(1.2deg); }
            45% { transform: translate(-5px, -3px) rotate(-1deg); }
            60% { transform: translate(5px, 3px) rotate(0.8deg); }
            75% { transform: translate(-3px, 1px) rotate(-0.5deg); }
            100% { transform: translate(0, 0) rotate(0deg); }
        }

        .screen-shake {
            animation: seismicShake 0.45s ease-in-out forwards;
        }

        .slide-down-exit {
            transition: transform 0.85s cubic-bezier(0.7, 0, 0.3, 1), opacity 0.85s ease !important;
            transform: translateY(120vh) !important;
            opacity: 0 !important;
            pointer-events: none;
        }
    </style>
</head>
<body>

    <!-- 1. Pantalla de carga futurista -->
    <div id="loaderOverlay">
        <div class="door-frame">
            <div class="door-graphics"></div>
            <div class="loader-title">DESENCRIPTANDO BÓVEDA</div>
            <div class="progress-bar-container">
                <div id="progressBar" class="progress-bar-fill"></div>
            </div>
            <div id="statusLabel" class="status-text">Iniciando protocolo de compuertas... (0%)</div>
        </div>
    </div>

    <!-- 2. Pantalla de login sobre mural de películas desenfocado -->
    <div id="loginScreen">
        <div class="movie-backdrop"></div>
        <div class="login-card" id="loginCard">
            <h2>ACCESO PRIVADO</h2>
            <p>Ingresa la contraseña para desbloquear el catálogo</p>
            
            <div class="input-group">
                <input type="password" id="passInput" placeholder="••••••••" autocomplete="off">
            </div>

            <button class="btn-submit" onclick="validarAcceso()">INGRESAR AL CINE</button>
            <div id="errorLabel" class="error-label"></div>
        </div>
    </div>

    <!-- 3. Catálogo final -->
    <div id="catalogSection">
        <div class="catalog-header">
            <h1>🍿 Tu Cine Privado</h1>
            <p style="color: #777; margin-top: 6px;">Catálogo personal disponible</p>
        </div>

        <div class="grid">
            <div class="movie-card" onclick="reproducir('{{ url_video }}')">
                <img src="{{ portada }}" alt="Deadpool & Wolverine">
                <div class="info">
                    <h3>Deadpool & Wolverine</h3>
                    <span>Acción / Aventura • Calidad HD</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal del reproductor -->
    <div id="videoModal" class="modal">
        <div class="modal-box">
            <span class="modal-close" onclick="cerrarVideo()">&times;</span>
            <video id="player" controls>
                <source id="videoSource" src="" type="video/mp4">
            </video>
        </div>
    </div>

    <script>
        // Simulación de carga futurista
        window.addEventListener("DOMContentLoaded", () => {
            const bar = document.getElementById("progressBar");
            const label = document.getElementById("statusLabel");
            const loader = document.getElementById("loaderOverlay");
            const login = document.getElementById("loginScreen");

            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.floor(Math.random() * 7) + 3;
                if (progress > 100) progress = 100;

                bar.style.width = progress + "%";
                label.innerText = `Alineando compuertas magnéticas... (${progress}%)`;

                if (progress === 100) {
                    clearInterval(interval);
                    setTimeout(() => {
                        loader.style.opacity = "0";
                        setTimeout(() => {
                            loader.style.visibility = "hidden";
                            login.style.visibility = "visible";
                            login.style.opacity = "1";
                            document.getElementById("passInput").focus();
                        }, 500);
                    }, 400);
                }
            }, 60);
        });

        // Verificación de credenciales con efecto Shake + Slide Down
        function validarAcceso() {
            const input = document.getElementById("passInput");
            const error = document.getElementById("errorLabel");
            const loginScreen = document.getElementById("loginScreen");

            if (input.value === "{{ clave }}") {
                error.innerText = "";
                // 1. Efecto de sacudida (shake)
                loginScreen.classList.add("screen-shake");
                
                // 2. Deslizar hacia abajo tras el shake
                setTimeout(() => {
                    loginScreen.classList.remove("screen-shake");
                    loginScreen.classList.add("slide-down-exit");
                }, 460);
            } else {
                error.innerText = "Contraseña incorrecta. Intento bloqueado.";
                input.value = "";
                // Pequeña vibración en el botón o tarjeta de error
                const card = document.getElementById("loginCard");
                card.style.transform = "translateX(-8px)";
                setTimeout(() => { card.style.transform = "translateX(8px)"; }, 80);
                setTimeout(() => { card.style.transform = "translateX(-4px)"; }, 160);
                setTimeout(() => { card.style.transform = "translateX(0)"; }, 240);
            }
        }

        // Permitir presionar tecla Enter
        document.getElementById("passInput").addEventListener("keypress", (e) => {
            if (e.key === "Enter") validarAcceso();
        });

        // Controles de reproducción de video
        function reproducir(url) {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");
            const source = document.getElementById("videoSource");
            source.src = url;
            player.load();
            modal.style.display = "flex";
            player.play();
        }

        function cerrarVideo() {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");
            modal.style.display = "none";
            player.pause();
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(
        PAGINA_WEB, 
        clave=CONTRASEÑA_CORRECTA, 
        url_video=VIDEO_URL,
        portada=PORTADA_DEADPOOL
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
