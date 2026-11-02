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
    <title>Cine Privado // Cinema Vault</title>
    <!-- Icono de la pestaña (Favicon de Palomitas) -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍿</text></svg>">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #0b0c10;
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
           2. LOGIN CON MURAL DESENFOCADO
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
            filter: blur(14px) saturate(1.2);
            transform: scale(1.08);
        }

        .login-card {
            position: relative;
            z-index: 10;
            background: rgba(18, 18, 24, 0.85);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
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
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        .login-card p {
            font-size: 13px;
            color: #999;
            margin-bottom: 25px;
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
            margin-top: 15px;
            transition: background 0.2s, transform 0.1s;
        }

        .btn-submit:hover {
            background: #b80d17;
            transform: translateY(-2px);
        }

        .error-label {
            color: #ff3344;
            font-size: 13px;
            margin-top: 15px;
            min-height: 18px;
            font-weight: 500;
        }

        /* -------------------------------------------
           3. CATÁLOGO CON FONDO NETFLIX Y TÍTULO PRO
        ------------------------------------------- */
        #catalogSection {
            position: relative;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 50px 20px 80px;
            overflow: hidden;
        }

        .netflix-wall-bg {
            position: fixed;
            inset: -20px;
            z-index: 1;
            background-image: 
                radial-gradient(circle at center, rgba(14, 16, 24, 0.82) 0%, rgba(5, 6, 10, 0.96) 80%),
                linear-gradient(to bottom, rgba(5, 6, 10, 0.7), rgba(5, 6, 10, 0.95)),
                url('https://assets.nflxext.com/ffe/siteui/vlv3/797858c0-2f95-44cb-a664-9f2066d4821a/48dd642c-f64f-43fc-8785-3db3aa84f5aa/ES-es-20240902-TRIFECTA-perspective_alpha_website_large.jpg');
            background-size: cover;
            background-position: center;
            filter: blur(4px) brightness(0.65);
            pointer-events: none;
        }

        .catalog-content {
            position: relative;
            z-index: 2;
            width: 100%;
            max-width: 1100px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .elaborate-header {
            text-align: center;
            margin-bottom: 45px;
        }

        .meta-tagline {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 5px 14px;
            border-radius: 20px;
            background: rgba(229, 9, 20, 0.15);
            border: 1px solid rgba(229, 9, 20, 0.4);
            color: #ff4d5a;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .meta-tagline span {
            width: 6px;
            height: 6px;
            background: #e50914;
            border-radius: 50%;
            box-shadow: 0 0 8px #ff4d5a;
        }

        .cinema-title {
            font-size: clamp(34px, 5vw, 54px);
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 4px;
            background: linear-gradient(180deg, #ffffff 25%, #cfd4dc 70%, #828a99 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 10px 30px rgba(0, 0, 0, 0.9);
            line-height: 1.1;
            margin-bottom: 10px;
        }

        .cinema-title em {
            font-style: normal;
            background: linear-gradient(180deg, #ff4d5a 0%, #e50914 55%, #8b0007 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .title-divider {
            width: 120px;
            height: 3px;
            background: linear-gradient(90deg, transparent, #e50914, transparent);
            margin: 10px auto 14px;
            box-shadow: 0 0 12px #e50914;
        }

        .sub-description {
            color: #8c96a7;
            font-size: 14px;
            letter-spacing: 1px;
        }

        .movie-card {
            background: rgba(20, 22, 30, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 14px;
            overflow: hidden;
            width: 270px;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease, border-color 0.35s ease;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7);
        }

        .movie-card:hover {
            transform: translateY(-10px) scale(1.03);
            border-color: #e50914;
            box-shadow: 0 20px 40px rgba(229, 9, 20, 0.45);
        }

        .movie-card img {
            width: 100%;
            height: 390px;
            object-fit: cover;
            display: block;
        }

        .movie-card .info {
            padding: 16px;
            text-align: left;
            background: linear-gradient(180deg, rgba(20, 22, 30, 0.95), #0f1015);
        }

        .movie-card .info h3 {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 6px;
            color: #ffffff;
        }

        .movie-card .badges {
            display: flex;
            gap: 8px;
            font-size: 11px;
            font-weight: 600;
            color: #b3b3b3;
        }

        .badge-pill {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 7px;
            border-radius: 4px;
            color: #fff;
        }

        /* Modal Reproductor */
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
            max-width: 960px;
            background: #000;
            border-radius: 12px;
            border: 1px solid #333;
            overflow: hidden;
            box-shadow: 0 0 50px rgba(229, 9, 20, 0.25);
        }

        .modal-close {
            position: absolute;
            top: 10px;
            right: 15px;
            color: #fff;
            font-size: 34px;
            font-weight: bold;
            cursor: pointer;
            z-index: 10;
        }

        video {
            width: 100%;
            display: block;
            outline: none;
        }

        /* Animaciones */
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

    <!-- 1. Carga futurista -->
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

    <!-- 2. Login sobre pósters desenfocados -->
    <div id="loginScreen">
        <div class="movie-backdrop"></div>
        <div class="login-card" id="loginCard">
            <h2>ACCESO PRIVADO</h2>
            <p>Introduce la clave para desbloquear tu cine personal</p>
            
            <div class="input-group">
                <input type="password" id="passInput" placeholder="••••••••" autocomplete="off">
            </div>

            <button class="btn-submit" onclick="validarAcceso()">INGRESAR AL CINE</button>
            <div id="errorLabel" class="error-label"></div>
        </div>
    </div>

    <!-- 3. Catálogo con fondo Netflix y Título Elaborado -->
    <div id="catalogSection">
        <div class="netflix-wall-bg"></div>

        <div class="catalog-content">
            <div class="elaborate-header">
                <div class="meta-tagline">
                    <span></span> SERVIDOR PRIVADO EXCLUSIVO
                </div>
                <h1 class="cinema-title">CINE <em>PRIVADO</em></h1>
                <div class="title-divider"></div>
                <p class="sub-description">Catálogo seleccionado • Transmisión en Ultra HD</p>
            </div>

            <div class="movie-card" onclick="reproducir('{{ url_video }}')">
                <img src="{{ portada }}" alt="Deadpool & Wolverine">
                <div class="info">
                    <h3>Deadpool & Wolverine</h3>
                    <div class="badges">
                        <span class="badge-pill">4K ULTRA HD</span>
                        <span>Acción • Comedia</span>
                    </div>
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
        // Carga de compuertas
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

        // Acceso con Shake y Slide Down
        function validarAcceso() {
            const input = document.getElementById("passInput");
            const error = document.getElementById("errorLabel");
            const loginScreen = document.getElementById("loginScreen");

            if (input.value === "{{ clave }}") {
                error.innerText = "";
                loginScreen.classList.add("screen-shake");
                
                setTimeout(() => {
                    loginScreen.classList.remove("screen-shake");
                    loginScreen.classList.add("slide-down-exit");
                }, 460);
            } else {
                error.innerText = "Contraseña denegada. Intento no autorizado.";
                input.value = "";
                const card = document.getElementById("loginCard");
                card.style.transform = "translateX(-8px)";
                setTimeout(() => { card.style.transform = "translateX(8px)"; }, 80);
                setTimeout(() => { card.style.transform = "translateX(-4px)"; }, 160);
                setTimeout(() => { card.style.transform = "translateX(0)"; }, 240);
            }
        }

        document.getElementById("passInput").addEventListener("keypress", (e) => {
            if (e.key === "Enter") validarAcceso();
        });

        // Modal de reproducción
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
