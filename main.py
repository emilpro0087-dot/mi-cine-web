import os
from flask import Flask, render_template_string

app = Flask(__name__)

CONTRASEÑA_CORRECTA = "perrofeoxd"

# Enlace directo del archivo alojado en Internet Archive
VIDEO_URL = "https://archive.org/download/deadpool-and-wolverine_202611/Deadpool_and_Wolverine.mp4"

# Subtítulos base (puedes añadir o reemplazar las líneas de tiempo que desees)
SUBTITULOS_VTT = """WEBVTT

1
00:00:05.000 --> 00:00:09.000
Benvenuti al cinema privato.

2
00:00:10.000 --> 00:00:15.000
Deadpool & Wolverine - Sottotitoli in italiano.
"""

PORTADA_DEADPOOL = "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg"

PAGINA_WEB = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cine Privado // Cinema Vault</title>
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

        /* 1. Pantalla de Carga Futurista */
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

        /* 2. Login con Fondo Netflix Oblicuo */
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
                radial-gradient(circle at center, rgba(10, 10, 15, 0.72) 0%, rgba(5, 5, 8, 0.92) 100%),
                linear-gradient(rgba(10, 10, 15, 0.75), rgba(10, 10, 15, 0.85)),
                url('https://assets.nflxext.com/ffe/siteui/vlv3/797858c0-2f95-44cb-a664-9f2066d4821a/48dd642c-f64f-43fc-8785-3db3aa84f5aa/ES-es-20240902-TRIFECTA-perspective_alpha_website_large.jpg');
            background-size: cover;
            background-position: center;
            filter: blur(10px) brightness(0.65);
            transform: scale(1.08);
        }

        .login-card {
            position: relative;
            z-index: 10;
            background: rgba(18, 18, 24, 0.88);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 40px 35px;
            width: 380px;
            max-width: 88vw;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9);
        }

        .login-card h2 {
            font-size: 24px;
            letter-spacing: 2px;
            margin-bottom: 8px;
        }

        .login-card p {
            font-size: 13px;
            color: #aaa;
            margin-bottom: 25px;
        }

        .input-group input {
            width: 100%;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #333;
            background: rgba(0, 0, 0, 0.65);
            color: #00f0ff;
            font-size: 18px;
            text-align: center;
            letter-spacing: 6px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .input-group input:focus {
            border-color: #e50914;
            box-shadow: 0 0 15px rgba(229, 9, 20, 0.6);
        }

        .btn-submit {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #e50914 0%, #b80d17 100%);
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            letter-spacing: 1.5px;
            margin-top: 15px;
            transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(229, 9, 20, 0.4);
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(229, 9, 20, 0.6);
        }

        .error-label {
            color: #ff3344;
            font-size: 13px;
            margin-top: 15px;
            min-height: 18px;
            font-weight: 500;
        }

        /* 3. Catálogo y Cabecera de Películas */
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
            inset: -40px;
            z-index: 1;
            background-image: 
                radial-gradient(circle at center, rgba(14, 16, 24, 0.65) 0%, rgba(5, 6, 10, 0.94) 85%),
                linear-gradient(to bottom, rgba(5, 6, 10, 0.6), rgba(5, 6, 10, 0.95)),
                url('https://assets.nflxext.com/ffe/siteui/vlv3/797858c0-2f95-44cb-a664-9f2066d4821a/48dd642c-f64f-43fc-8785-3db3aa84f5aa/ES-es-20240902-TRIFECTA-perspective_alpha_website_large.jpg');
            background-size: cover;
            background-position: center;
            filter: contrast(1.15) brightness(0.6);
            pointer-events: none;
            transform: scale(1.04);
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
            color: #a0aec0;
            font-size: 14px;
            letter-spacing: 1px;
        }

        .movie-card {
            background: rgba(20, 22, 30, 0.75);
            backdrop-filter: blur(12px);
            border-radius: 14px;
            overflow: hidden;
            width: 270px;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.12);
            transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease, border-color 0.35s ease;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.8);
        }

        .movie-card:hover {
            transform: translateY(-10px) scale(1.03);
            border-color: #e50914;
            box-shadow: 0 20px 45px rgba(229, 9, 20, 0.5);
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
            background: rgba(255, 255, 255, 0.12);
            padding: 2px 7px;
            border-radius: 4px;
            color: #fff;
        }

        ::cue {
            background-color: rgba(0, 0, 0, 0.8);
            color: #ffd700;
            font-size: 19px;
            font-weight: bold;
            text-shadow: 1px 1px 2px #000;
        }

        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 6000;
            background: rgba(0, 0, 0, 0.95);
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
            box-shadow: 0 0 50px rgba(229, 9, 20, 0.3);
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

        @keyframes spinGear { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes spinGearRev { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }
        @keyframes seismicShake {
            0% { transform: translate(0, 0) rotate(0deg); }
            15% { transform: translate(-6px, 4px) rotate(-1deg); }
            30% { transform: translate(6px, -4px) rotate(1.2deg); }
            45% { transform: translate(-5px, -3px) rotate(-1deg); }
            60% { transform: translate(5px, 3px) rotate(0.8deg); }
            75% { transform: translate(-3px, 1px) rotate(-0.5deg); }
            100% { transform: translate(0, 0) rotate(0deg); }
        }

        .screen-shake { animation: seismicShake 0.45s ease-in-out forwards; }
        .slide-down-exit {
            transition: transform 0.85s cubic-bezier(0.7, 0, 0.3, 1), opacity 0.85s ease !important;
            transform: translateY(120vh) !important;
            opacity: 0 !important;
            pointer-events: none;
        }
    </style>
</head>
<body>

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

    <div id="loginScreen">
        <div class="movie-backdrop"></div>
        <div class="login-card" id="loginCard">
            <h2>ACCESO PRIVADO</h2>
            <p>Introduce la clave para desbloquear tu cine personal</p>
            
            <div class="input-group">
                <input type="password" id="passInput" placeholder="••••••••" autocomplete="off" oninput="playAudio('type')">
            </div>

            <button class="btn-submit" onclick="validarAcceso()">INGRESAR AL CINE</button>
            <div id="errorLabel" class="error-label"></div>
        </div>
    </div>

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

            <div class="movie-card" onclick="playAudio('open'); reproducir('{{ url_video }}')">
                <img src="{{ portada }}" alt="Deadpool & Wolverine">
                <div class="info">
                    <h3>Deadpool & Wolverine</h3>
                    <div class="badges">
                        <span class="badge-pill">4K ULTRA HD</span>
                        <span class="badge-pill">SUB: ITA</span>
                        <span>Acción • Comedia</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="videoModal" class="modal">
        <div class="modal-box">
            <span class="modal-close" onclick="cerrarVideo()">&times;</span>
            <video id="player" controls crossorigin="anonymous">
                <source id="videoSource" src="" type="video/mp4">
                <track id="videoTrack" label="Italiano" kind="subtitles" srclang="it" default>
            </video>
        </div>
    </div>

    <script id="embeddedSubtitles" type="text/vtt">{{ subtitulos_raw | safe }}</script>

    <script>
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        function playAudio(type) {
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }

            const now = audioCtx.currentTime;

            if (type === 'type') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(800, now);
                osc.frequency.exponentialRampToValueAtTime(1400, now + 0.04);
                gain.gain.setValueAtTime(0.08, now);
                gain.gain.linearRampToValueAtTime(0.001, now + 0.04);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.04);

            } else if (type === 'success') {
                [330, 440, 660, 880].forEach((freq, idx) => {
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(freq, now + (idx * 0.09));
                    gain.gain.setValueAtTime(0.12, now + (idx * 0.09));
                    gain.gain.exponentialRampToValueAtTime(0.001, now + (idx * 0.09) + 0.22);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start(now + (idx * 0.09));
                    osc.stop(now + (idx * 0.09) + 0.22);
                });

            } else if (type === 'error') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(260, now);
                osc.frequency.linearRampToValueAtTime(110, now + 0.28);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.linearRampToValueAtTime(0.001, now + 0.28);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.28);

            } else if (type === 'open') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(140, now);
                osc.frequency.exponentialRampToValueAtTime(45, now + 0.6);
                gain.gain.setValueAtTime(0.35, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.6);
            }
        }

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

        function validarAcceso() {
            const input = document.getElementById("passInput");
            const error = document.getElementById("errorLabel");
            const loginScreen = document.getElementById("loginScreen");

            if (input.value === "{{ clave }}") {
                error.innerText = "";
                playAudio('success');
                loginScreen.classList.add("screen-shake");
                
                setTimeout(() => {
                    loginScreen.classList.remove("screen-shake");
                    loginScreen.classList.add("slide-down-exit");
                }, 460);
            } else {
                playAudio('error');
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

        function reproducir(videoUrl) {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");
            const source = document.getElementById("videoSource");
            const track = document.getElementById("videoTrack");
            
            // Cargar subtítulos en memoria
            let vttRaw = document.getElementById("embeddedSubtitles").textContent;
            
            // Filtro: limpia ruidos entre corchetes, paréntesis o notas musicales
            vttRaw = vttRaw.replace(/\\[.*?\\]/g, "")
                           .replace(/\\(.*?\\)/g, "")
                           .replace(/♪.*?♪/g, "")
                           .replace(/[♪#]/g, "");

            const vttBlob = new Blob([vttRaw], { type: 'text/vtt' });
            track.src = URL.createObjectURL(vttBlob);

            source.src = videoUrl;
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
        subtitulos_raw=SUBTITULOS_VTT,
        portada=PORTADA_DEADPOOL
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
