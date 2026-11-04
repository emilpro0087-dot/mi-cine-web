import os
import requests
from flask import Flask, render_template_string, Response, request

app = Flask(__name__)

CONTRASEÑA_CORRECTA = "perrofeoxd"

# Enlace al archivo de video (reemplaza si es necesario con el enlace directo .mp4 de Archive.org)
VIDEO_URL_ORIGINAL = "https://archive.org/download/deadpool-and-wolverine_202611/miproyecto_1.mp4"

PORTADA_DEADPOOL = "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg"

SUBTITULOS_VTT_BASE = """WEBVTT

1
00:00:08.000 --> 00:00:13.000
[Musica drammatica] Ciao a tutti, bentornati. (applausi)

2
00:00:19.000 --> 00:00:23.000
♪ Suono di chitarra ♪ Credevate davvero che sarei rimasto tranquillo a casa?

3
00:00:24.000 --> 00:00:28.000
[RUMORE DI TUONO] Non finché il multiverso è in pericolo.
"""

PAGINA_WEB = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cinema Privato // Cinema & Arcade Vault</title>
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

        /* Insignia de versión en la esquina superior izquierda */
        .version-badge {
            position: fixed;
            top: 14px;
            left: 14px;
            z-index: 9999;
            background: rgba(10, 16, 26, 0.85);
            border: 1px solid rgba(0, 240, 255, 0.4);
            border-radius: 6px;
            padding: 5px 12px;
            font-family: monospace;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: #00f0ff;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.2);
            backdrop-filter: blur(8px);
            user-select: none;
            pointer-events: none;
        }

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

        .catalog-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            width: 100%;
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

        .movie-card.game-card:hover {
            border-color: #00f0ff;
            box-shadow: 0 20px 45px rgba(0, 240, 255, 0.5);
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
            background-color: rgba(0, 0, 0, 0.85);
            color: #ffd700;
            font-size: 22px;
            font-weight: bold;
            text-shadow: 2px 2px 4px #000;
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
            z-index: 25;
        }

        .subtitle-controls {
            position: absolute;
            top: 12px;
            left: 20px;
            z-index: 25;
            display: flex;
            align-items: center;
            gap: 10px;
            background: rgba(10, 12, 18, 0.75);
            padding: 6px 14px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(8px);
        }

        .subtitle-controls label {
            font-size: 12px;
            font-weight: 600;
            color: #eee;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .subtitle-controls input[type="checkbox"] {
            accent-color: #e50914;
            cursor: pointer;
            width: 15px;
            height: 15px;
        }

        video {
            width: 100%;
            display: block;
            outline: none;
            background: #000;
        }

        #gameCanvas {
            background: #05070f;
            display: block;
            margin: 0 auto;
            border-radius: 8px;
            box-shadow: 0 0 25px rgba(0, 240, 255, 0.2);
        }

        .game-controls-bar {
            text-align: center;
            padding: 12px;
            background: #0d111a;
            color: #00f0ff;
            font-family: monospace;
            font-size: 13px;
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

    <!-- Insignia fija v0.0 en la esquina superior izquierda -->
    <div class="version-badge">v0.0</div>

    <div id="loaderOverlay">
        <div class="door-frame">
            <div class="door-graphics"></div>
            <div class="loader-title">ACCESSO CASSETTA DI SICUREZZA</div>
            <div class="progress-bar-container">
                <div id="progressBar" class="progress-bar-fill"></div>
            </div>
            <div id="statusLabel" class="status-text">Avvio protocollo porte... (0%)</div>
        </div>
    </div>

    <div id="loginScreen">
        <div class="movie-backdrop"></div>
        <div class="login-card" id="loginCard">
            <h2>ACCESSO PRIVATO</h2>
            <p>Inserisci la chiave per accedere al cinema personale</p>
            
            <div class="input-group">
                <input type="password" id="passInput" placeholder="••••••••" autocomplete="off" oninput="playAudio('type')">
            </div>

            <button class="btn-submit" onclick="validarAcceso()">ENTRA NEL CINEMA</button>
            <div id="errorLabel" class="error-label"></div>
        </div>
    </div>

    <div id="catalogSection">
        <div class="netflix-wall-bg"></div>

        <div class="catalog-content">
            <div class="elaborate-header">
                <div class="meta-tagline">
                    <span></span> SERVER PRIVATO ESCLUSIVO
                </div>
                <h1 class="cinema-title">CINEMA & <em>ARCADE</em></h1>
                <div class="title-divider"></div>
                <p class="sub-description">Catalogo selezionato • Streaming Ultra HD & Giochi Web</p>
            </div>

            <div class="catalog-grid">
                <!-- Tarjeta 1: Película Deadpool & Wolverine -->
                <div class="movie-card" onclick="playAudio('open'); reproducir('/stream-video')">
                    <img src="{{ portada }}" alt="Deadpool & Wolverine">
                    <div class="info">
                        <h3>Deadpool & Wolverine</h3>
                        <div class="badges">
                            <span class="badge-pill">4K ULTRA HD</span>
                            <span class="badge-pill">SUB (SOLO VOCE)</span>
                            <span>Azione • Commedia</span>
                        </div>
                    </div>
                </div>

                <!-- Tarjeta 2: Apartado de JUEGO WEB -->
                <div class="movie-card game-card" onclick="playAudio('open'); abrirJuego()">
                    <div style="height: 390px; background: radial-gradient(circle, #0e1e38 0%, #060911 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px;">
                        <span style="font-size: 80px; filter: drop-shadow(0 0 20px #00f0ff);">🎮</span>
                        <span style="font-family: monospace; font-size: 13px; letter-spacing: 3px; color: #00f0ff;">ZONA ARCADE</span>
                    </div>
                    <div class="info">
                        <h3>SEZIONE GIOCO</h3>
                        <div class="badges">
                            <span class="badge-pill" style="border-color: #00f0ff; color: #00f0ff;">WEB CANVAS</span>
                            <span class="badge-pill">INTERATTIVO</span>
                            <span>Arcade 2D</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal del Reproductor de Video -->
    <div id="videoModal" class="modal">
        <div class="modal-box">
            <div class="subtitle-controls">
                <label>
                    <input type="checkbox" id="toggleAutoSub" checked onchange="toggleSubtitles(this.checked)">
                    Sottotitoli (Solo Voce)
                </label>
            </div>

            <span class="modal-close" onclick="cerrarVideo()">&times;</span>

            <video id="player" controls playsinline></video>
        </div>
    </div>

    <!-- Modal del Juego Web Canvas -->
    <div id="gameModal" class="modal">
        <div class="modal-box" style="border-color: #00f0ff; max-width: 840px;">
            <span class="modal-close" onclick="cerrarJuego()">&times;</span>
            <div style="padding: 15px; text-align: center;">
                <canvas id="gameCanvas" width="800" height="450"></canvas>
            </div>
            <div class="game-controls-bar">
                Usa [FRECCE ← →] o [A / D] per muovere la navetta • SPAZIO per iniziare/ricominciare
            </div>
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
                label.innerText = `Sincronizzazione in corso... (${progress}%)`;

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
                error.innerText = "Password errata. Accesso non autorizzato.";
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

        function parseVttTime(timeString) {
            const parts = timeString.trim().split(':');
            let h = 0, m = 0, s = 0;
            if (parts.length === 3) {
                h = parseFloat(parts[0]);
                m = parseFloat(parts[1]);
                s = parseFloat(parts[2].replace(',', '.'));
            } else if (parts.length === 2) {
                m = parseFloat(parts[0]);
                s = parseFloat(parts[1].replace(',', '.'));
            }
            return (h * 3600) + (m * 60) + s;
        }

        // Limpieza de subtítulos: SOLO VOZ HABLADA
        function cargarSubtitulosEnPlayer(player) {
            while (player.firstChild) {
                player.removeChild(player.firstChild);
            }

            const rawText = document.getElementById("embeddedSubtitles").textContent;
            const track = player.addTextTrack("subtitles", "Italiano (Solo Voce)", "it");
            track.mode = document.getElementById("toggleAutoSub").checked ? "showing" : "disabled";

            const bloques = rawText.replace(/\\r\\n/g, '\\n').replace(/\\r/g, '\\n').split('\\n\\n');

            for (const bloque of bloques) {
                const lineas = bloque.trim().split('\\n');
                if (!lineas || lineas.length === 0) continue;

                const timingIndex = lineas.findIndex(l => l.includes("-->"));
                if (timingIndex === -1) continue;

                const [startStr, endStr] = lineas[timingIndex].split("-->");
                const startTime = parseVttTime(startStr);
                const endTime = parseVttTime(endStr);

                const textoLineas = lineas.slice(timingIndex + 1);
                const dialogos = [];

                for (let txt of textoLineas) {
                    txt = txt.replace(/[♪♫#♬♩]/g, "");
                    txt = txt.replace(/\\[.*?\\]/g, "");
                    txt = txt.replace(/\\(.*?\\)/g, "");
                    txt = txt.replace(/^[A-ZÀ-Ú0-9_\\s]+:\\s*/g, "");
                    txt = txt.trim();

                    if (txt.length > 0) {
                        dialogos.push(txt);
                    }
                }

                if (dialogos.length > 0 && !isNaN(startTime) && !isNaN(endTime)) {
                    try {
                        track.addCue(new VTTCue(startTime, endTime, dialogos.join('\\n')));
                    } catch (e) {
                        console.warn("Cue warning:", e);
                    }
                }
            }
        }

        function toggleSubtitles(activar) {
            const player = document.getElementById("player");
            if (player.textTracks && player.textTracks.length > 0) {
                for (let i = 0; i < player.textTracks.length; i++) {
                    player.textTracks[i].mode = activar ? "showing" : "disabled";
                }
            }
        }

        function reproducir(videoEndpoint) {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");

            modal.style.display = "flex";
            player.src = videoEndpoint;
            
            cargarSubtitulosEnPlayer(player);

            const playPromise = player.play();
            if (playPromise !== undefined) {
                playPromise.catch(err => {
                    console.warn("Interazione utente richiesta dal browser:", err);
                });
            }
        }

        function cerrarVideo() {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");

            modal.style.display = "none";
            player.pause();
            player.removeAttribute("src");
            player.load();
        }

        // Lógica del Videojuego Web Canvas
        let gameLoopId = null;
        let paddle = { x: 350, y: 410, w: 100, h: 14, dx: 7 };
        let ball = { x: 400, y: 200, r: 8, dx: 4, dy: -4 };
        let rightPressed = false;
        let leftPressed = false;
        let gameRunning = false;

        function abrirJuego() {
            const modal = document.getElementById("gameModal");
            modal.style.display = "flex";
            resetGame();
            if (!gameLoopId) {
                gameLoop();
            }
        }

        function cerrarJuego() {
            const modal = document.getElementById("gameModal");
            modal.style.display = "none";
            gameRunning = false;
            if (gameLoopId) {
                cancelAnimationFrame(gameLoopId);
                gameLoopId = null;
            }
        }

        function resetGame() {
            paddle.x = 350;
            ball.x = 400;
            ball.y = 250;
            ball.dx = 4 * (Math.random() > 0.5 ? 1 : -1);
            ball.dy = -4;
            gameRunning = true;
        }

        window.addEventListener("keydown", (e) => {
            if (e.key === "Right" || e.key === "ArrowRight" || e.key === "d" || e.key === "D") rightPressed = true;
            if (e.key === "Left" || e.key === "ArrowLeft" || e.key === "a" || e.key === "A") leftPressed = true;
            if (e.code === "Space" && document.getElementById("gameModal").style.display === "flex") {
                resetGame();
            }
        });

        window.addEventListener("keyup", (e) => {
            if (e.key === "Right" || e.key === "ArrowRight" || e.key === "d" || e.key === "D") rightPressed = false;
            if (e.key === "Left" || e.key === "ArrowLeft" || e.key === "a" || e.key === "A") leftPressed = false;
        });

        function gameLoop() {
            const canvas = document.getElementById("gameCanvas");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");

            ctx.fillStyle = "#05070f";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            if (rightPressed && paddle.x < canvas.width - paddle.w) paddle.x += paddle.dx;
            if (leftPressed && paddle.x > 0) paddle.x -= paddle.dx;

            if (gameRunning) {
                ball.x += ball.dx;
                ball.y += ball.dy;

                if (ball.x + ball.r > canvas.width || ball.x - ball.r < 0) ball.dx = -ball.dx;
                if (ball.y - ball.r < 0) ball.dy = -ball.dy;

                if (
                    ball.y + ball.r >= paddle.y &&
                    ball.x >= paddle.x &&
                    ball.x <= paddle.x + paddle.w
                ) {
                    ball.dy = -Math.abs(ball.dy);
                    playAudio('type');
                }

                if (ball.y + ball.r > canvas.height) {
                    gameRunning = false;
                    playAudio('error');
                }
            }

            ctx.fillStyle = "#00f0ff";
            ctx.shadowColor = "#00f0ff";
            ctx.shadowBlur = 12;
            ctx.fillRect(paddle.x, paddle.y, paddle.w, paddle.h);

            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
            ctx.fillStyle = "#ff0055";
            ctx.shadowColor = "#ff0055";
            ctx.shadowBlur = 15;
            ctx.fill();
            ctx.closePath();
            ctx.shadowBlur = 0;

            if (!gameRunning) {
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 20px monospace";
                ctx.textAlign = "center";
                ctx.fillText("PREMI SPAZIO PER GIOCARE", canvas.width / 2, canvas.height / 2);
            }

            gameLoopId = requestAnimationFrame(gameLoop);
        }
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(
        PAGINA_WEB, 
        clave=CONTRASEÑA_CORRECTA, 
        subtitulos_raw=SUBTITULOS_VTT_BASE,
        portada=PORTADA_DEADPOOL
    )

@app.route('/stream-video')
def stream_video():
    range_header = request.headers.get('Range', None)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    if range_header:
        headers['Range'] = range_header

    try:
        req = requests.get(VIDEO_URL_ORIGINAL, headers=headers, stream=True, timeout=15)
        response_headers = {
            'Content-Type': req.headers.get('Content-Type', 'video/mp4'),
            'Accept-Ranges': 'bytes'
        }
        if 'Content-Range' in req.headers:
            response_headers['Content-Range'] = req.headers['Content-Range']
        if 'Content-Length' in req.headers:
            response_headers['Content-Length'] = req.headers['Content-Length']

        def generate():
            for chunk in req.iter_content(chunk_size=1024 * 128):
                if chunk:
                    yield chunk

        return Response(generate(), status=req.status_code, headers=response_headers)
    except Exception as e:
        return Response(f"Error cargando video: {str(e)}", status=502)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
