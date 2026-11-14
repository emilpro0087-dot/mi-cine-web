import os
import requests
from flask import Flask, render_template_string, Response, request

app = Flask(__name__)

# CONTROL DE VERSIÓN DE LA WEB (Sube +0.1 en cada actualización)
APP_VERSION = "v0.1"

CONTRASEÑA_CORRECTA = "perrofeoxd"
VIDEO_URL_ORIGINAL = "https://archive.org/download/deadpool-and-wolverine_202611/Deadpool_and_Wolverine.mp4"
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Cinema Privato // Cinema & Doors 3D ({{ version }})</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🚪</text></svg>">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; -webkit-user-select: none; }
        body { 
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #0b0c10;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* INSIGNIA DE VERSIÓN EN ESQUINA SUPERIOR IZQUIERDA */
        .version-badge {
            position: fixed;
            top: 12px;
            left: 12px;
            z-index: 9500;
            background: rgba(10, 15, 25, 0.85);
            border: 1px solid #00f0ff;
            color: #00f0ff;
            font-family: monospace;
            font-size: 12px;
            font-weight: bold;
            padding: 4px 10px;
            border-radius: 6px;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.35);
            pointer-events: none;
        }

        #loaderOverlay {
            position: fixed;
            inset: 0;
            z-index: 5000;
            display: flex;
            justify-content: center;
            align-items: center;
            background: radial-gradient(circle at center, rgba(16, 26, 45, 0.7) 0%, rgba(3, 5, 10, 0.98) 100%);
            transition: opacity 0.8s ease, visibility 0.8s ease;
        }

        .door-frame {
            width: 360px;
            max-width: 90vw;
            padding: 40px 30px;
            border: 2px solid #00f0ff;
            border-radius: 12px;
            background: rgba(10, 15, 25, 0.9);
            box-shadow: 0 0 35px rgba(0, 240, 255, 0.3);
            text-align: center;
        }

        .loader-title {
            font-family: monospace;
            font-size: 13px;
            letter-spacing: 3px;
            color: #00f0ff;
            margin-bottom: 15px;
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
            background: rgba(5, 6, 10, 0.96);
        }

        .login-card {
            background: rgba(18, 18, 24, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 40px 35px;
            width: 380px;
            max-width: 88vw;
            text-align: center;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.9);
        }

        .login-card h2 { font-size: 24px; letter-spacing: 2px; margin-bottom: 8px; }
        .login-card p { font-size: 13px; color: #aaa; margin-bottom: 25px; }

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
            margin-top: 15px;
        }

        .error-label { color: #ff3344; font-size: 13px; margin-top: 15px; min-height: 18px; }

        #catalogSection {
            position: relative;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 60px 20px 80px;
            background: radial-gradient(circle at top, #151926 0%, #07080c 100%);
        }

        .elaborate-header { text-align: center; margin-bottom: 45px; }
        .cinema-title {
            font-size: clamp(32px, 5vw, 52px);
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 4px;
            margin-bottom: 10px;
        }
        .cinema-title em { font-style: normal; color: #e50914; }
        .sub-description { color: #a0aec0; font-size: 14px; }

        .catalog-grid {
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            width: 100%;
            max-width: 1000px;
        }

        .movie-card {
            background: rgba(20, 22, 30, 0.85);
            border-radius: 14px;
            overflow: hidden;
            width: 270px;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.12);
            transition: transform 0.3s ease, border-color 0.3s ease;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.8);
        }

        .movie-card:hover { transform: translateY(-8px); border-color: #e50914; }
        .movie-card.game-card:hover { border-color: #00f0ff; box-shadow: 0 15px 40px rgba(0, 240, 255, 0.35); }
        .movie-card img { width: 100%; height: 380px; object-fit: cover; display: block; }
        .movie-card .info { padding: 16px; text-align: left; }
        .movie-card .info h3 { font-size: 18px; margin-bottom: 6px; }
        .movie-card .badges { display: flex; gap: 8px; font-size: 11px; color: #b3b3b3; }
        .badge-pill { background: rgba(255, 255, 255, 0.12); padding: 2px 7px; border-radius: 4px; color: #fff; }

        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 6000;
            background: rgba(0, 0, 0, 0.96);
            justify-content: center;
            align-items: center;
        }

        .modal-box {
            position: relative;
            width: 100%;
            max-width: 960px;
            background: #000;
            border-radius: 12px;
            border: 1px solid #333;
            overflow: hidden;
        }

        .modal-close {
            position: absolute;
            top: 10px;
            right: 16px;
            color: #fff;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            z-index: 50;
            text-shadow: 0 0 8px #000;
        }

        video { width: 100%; display: block; background: #000; }

        /* CONTENEDOR DOORS 3D */
        #gameModalBox {
            width: 95vw;
            max-width: 1040px;
            height: 82vh;
            border: 2px solid #00f0ff;
            position: relative;
            background: #050508;
        }

        #doors3DContainer {
            width: 100%;
            height: 100%;
            position: relative;
            overflow: hidden;
        }

        #doorsHUD {
            position: absolute;
            top: 14px;
            left: 14px;
            z-index: 20;
            display: flex;
            flex-direction: column;
            gap: 6px;
            pointer-events: none;
            font-family: monospace;
        }

        .hud-pill {
            background: rgba(8, 12, 20, 0.8);
            border: 1px solid rgba(0, 240, 255, 0.4);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            color: #fff;
        }

        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 8px;
            height: 8px;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            z-index: 15;
            pointer-events: none;
            box-shadow: 0 0 6px #00f0ff;
        }

        #promptText {
            position: absolute;
            top: 56%;
            left: 50%;
            transform: translateX(-50%);
            z-index: 20;
            background: rgba(0, 0, 0, 0.82);
            border: 1px solid #ffd700;
            color: #ffd700;
            padding: 6px 14px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 13px;
            display: none;
            pointer-events: none;
            text-align: center;
        }

        #btnFullscreen {
            position: absolute;
            top: 14px;
            right: 52px;
            z-index: 30;
            background: rgba(10, 18, 30, 0.85);
            border: 1px solid #00f0ff;
            color: #00f0ff;
            padding: 6px 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            cursor: pointer;
        }

        #startOverlay3D {
            position: absolute;
            inset: 0;
            z-index: 25;
            background: rgba(5, 7, 12, 0.82);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 20px;
            cursor: pointer;
        }

        /* CONTROLES TÁCTILES MÓVIL */
        #mobileControls {
            position: absolute;
            inset: 0;
            z-index: 22;
            pointer-events: none;
            display: none;
        }

        .touch-dpad {
            position: absolute;
            bottom: 20px;
            left: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
            pointer-events: auto;
        }

        .touch-row { display: flex; gap: 6px; }

        .touch-btn {
            width: 52px;
            height: 52px;
            border-radius: 12px;
            background: rgba(15, 25, 40, 0.75);
            border: 1px solid #00f0ff;
            color: #fff;
            font-size: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .touch-actions {
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            pointer-events: auto;
        }

        .slide-down-exit {
            transition: transform 0.8s ease, opacity 0.8s ease !important;
            transform: translateY(120vh) !important;
            opacity: 0 !important;
            pointer-events: none;
        }
    </style>
</head>
<body>

    <!-- ETIQUETA FIJA DE VERSIÓN -->
    <div class="version-badge">{{ version }}</div>

    <div id="loaderOverlay">
        <div class="door-frame">
            <div class="loader-title">ACCESSO CASSETTA DI SICUREZZA</div>
            <div class="progress-bar-container">
                <div id="progressBar" class="progress-bar-fill"></div>
            </div>
            <div id="statusLabel" class="status-text">Avvio sistema... (0%)</div>
        </div>
    </div>

    <div id="loginScreen">
        <div class="login-card">
            <h2>ACCESSO PRIVATO</h2>
            <p>Inserisci la chiave per accedere</p>
            <div class="input-group">
                <input type="password" id="passInput" placeholder="••••••••" autocomplete="off">
            </div>
            <button class="btn-submit" onclick="validarAcceso()">ENTRA</button>
            <div id="errorLabel" class="error-label"></div>
        </div>
    </div>

    <div id="catalogSection">
        <div class="elaborate-header">
            <h1 class="cinema-title">CINEMA & <em>DOORS 3D</em></h1>
            <p class="sub-description">Streaming Privato & Esperienza Horror 3D in Prima Persona</p>
        </div>

        <div class="catalog-grid">
            <div class="movie-card" onclick="reproducir('/stream-video')">
                <img src="{{ portada }}" alt="Deadpool & Wolverine">
                <div class="info">
                    <h3>Deadpool & Wolverine</h3>
                    <div class="badges">
                        <span class="badge-pill">4K ULTRA HD</span>
                        <span class="badge-pill">SUB (SOLO VOCE)</span>
                    </div>
                </div>
            </div>

            <div class="movie-card game-card" onclick="abrirJuego()">
                <div style="height: 380px; background: radial-gradient(circle, #142238 0%, #05070d 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px;">
                    <span style="font-size: 80px; filter: drop-shadow(0 0 20px #00f0ff);">🚪</span>
                    <span style="font-family: monospace; font-size: 14px; letter-spacing: 3px; color: #00f0ff;">DOORS 3D</span>
                </div>
                <div class="info">
                    <h3>DOORS 3D: L'HOTEL</h3>
                    <div class="badges">
                        <span class="badge-pill" style="border: 1px solid #00f0ff; color: #00f0ff;">1ª PERSONA</span>
                        <span class="badge-pill">PC & MOBILE</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Video -->
    <div id="videoModal" class="modal">
        <div class="modal-box">
            <span class="modal-close" onclick="cerrarVideo()">&times;</span>
            <video id="player" controls playsinline></video>
        </div>
    </div>

    <!-- Modal Juego Doors 3D -->
    <div id="gameModal" class="modal">
        <div class="modal-box" id="gameModalBox">
            <button id="btnFullscreen" onclick="toggleFullscreen()">[F11] SCHERMO INTERO</button>
            <span class="modal-close" onclick="cerrarJuego()">&times;</span>

            <div id="doors3DContainer">
                <div id="doorsHUD">
                    <div class="hud-pill" id="hudRoom">STANZA: LOBBY (0000)</div>
                    <div class="hud-pill" id="hudInv">🔑 Grimaldelli: 0 | 🔦 Torcia: ON</div>
                    <div class="hud-pill" id="hudStatus" style="color: #00f0ff;">Esplora l'hotel</div>
                </div>

                <div id="crosshair"></div>
                <div id="promptText">Premi [E] o Clic per interagire</div>

                <div id="startOverlay3D" onclick="iniciarControl3D()">
                    <h2 style="color: #00f0ff; font-family: monospace; font-size: 26px; margin-bottom: 10px;">DOORS 3D - FIRST PERSON</h2>
                    <p style="color: #ccc; max-width: 480px; font-size: 14px; line-height: 1.5; margin-bottom: 20px;">
                        PC: [WASD] Muovi • [Mouse] Guarda • [E / Clic] Apri porte e cassetti • [F] Torcia • [F11] Schermo intero<br>
                        MOBILE: Usa i tasti su schermo e trascina il dito per guardarti intorno.
                    </p>
                    <div style="padding: 12px 26px; background: #00f0ff; color: #000; font-weight: bold; border-radius: 8px; font-family: monospace;">
                        CLICCA PER ENTRARE NELL'ASCENSORE
                    </div>
                </div>

                <div id="mobileControls">
                    <div class="touch-dpad">
                        <button class="touch-btn" id="btnUp">▲</button>
                        <div class="touch-row">
                            <button class="touch-btn" id="btnLeft">◀</button>
                            <button class="touch-btn" id="btnDown">▼</button>
                            <button class="touch-btn" id="btnRight">▶</button>
                        </div>
                    </div>
                    <div class="touch-actions">
                        <button class="touch-btn" id="btnFlash">🔦</button>
                        <button class="touch-btn" id="btnInteract">✋</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script id="embeddedSubtitles" type="text/vtt">{{ subtitulos_raw | safe }}</script>

    <script>
        // --- AUDIO PROCEDURAL (CHIRRIDOS, PASOS, TIMBRE, TERROR) ---
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        function playSound(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const now = audioCtx.currentTime;

            if (type === 'creak') {
                // Chirrido realista de puerta abriéndose
                const osc = audioCtx.createOscillator();
                const osc2 = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc2.type = 'triangle';
                osc.frequency.setValueAtTime(190, now);
                osc.frequency.linearRampToValueAtTime(340, now + 0.25);
                osc.frequency.linearRampToValueAtTime(150, now + 0.65);

                osc2.frequency.setValueAtTime(196, now);
                osc2.frequency.linearRampToValueAtTime(352, now + 0.25);
                osc2.frequency.linearRampToValueAtTime(145, now + 0.65);

                gain.gain.setValueAtTime(0.08, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
                osc.connect(gain);
                osc2.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc2.start(now);
                osc.stop(now + 0.7);
                osc2.stop(now + 0.7);

            } else if (type === 'drawer') {
                // Deslizamiento de cajón de madera
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(120, now);
                osc.frequency.linearRampToValueAtTime(85, now + 0.22);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.24);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.24);

            } else if (type === 'step') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(95, now);
                osc.frequency.exponentialRampToValueAtTime(42, now + 0.08);
                gain.gain.setValueAtTime(0.09, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.09);

            } else if (type === 'ding') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, now);
                gain.gain.setValueAtTime(0.15, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.9);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.9);

            } else if (type === 'pickup') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(520, now);
                osc.frequency.exponentialRampToValueAtTime(980, now + 0.14);
                gain.gain.setValueAtTime(0.12, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.15);
            }
        }

        // Música real descargada en /static/Corredor_Horror.mp3
        const musicaHotelReal = new Audio('/static/Corredor_Horror.mp3');
        musicaHotelReal.loop = true;
        musicaHotelReal.volume = 0.42;

        // --- LOADER & LOGIN ---
        window.addEventListener("DOMContentLoaded", () => {
            const bar = document.getElementById("progressBar");
            const label = document.getElementById("statusLabel");
            const loader = document.getElementById("loaderOverlay");
            const login = document.getElementById("loginScreen");

            let progress = 0;
            const interval = setInterval(() => {
                progress += 12;
                if (progress > 100) progress = 100;
                bar.style.width = progress + "%";
                label.innerText = `Caricamento... (${progress}%)`;
                if (progress === 100) {
                    clearInterval(interval);
                    loader.style.opacity = "0";
                    setTimeout(() => {
                        loader.style.visibility = "hidden";
                        login.style.visibility = "visible";
                        login.style.opacity = "1";
                    }, 400);
                }
            }, 45);
        });

        function validarAcceso() {
            const input = document.getElementById("passInput");
            const error = document.getElementById("errorLabel");
            const loginScreen = document.getElementById("loginScreen");
            if (input.value === "{{ clave }}") {
                error.innerText = "";
                loginScreen.classList.add("slide-down-exit");
            } else {
                error.innerText = "Password errata.";
                input.value = "";
            }
        }

        document.getElementById("passInput").addEventListener("keypress", (e) => {
            if (e.key === "Enter") validarAcceso();
        });

        // --- VIDEO STREAMING ---
        function reproducir(endpoint) {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");
            modal.style.display = "flex";
            player.src = endpoint;
            player.play().catch(() => {});
        }

        function cerrarVideo() {
            const modal = document.getElementById("videoModal");
            const player = document.getElementById("player");
            modal.style.display = "none";
            player.pause();
            player.removeAttribute("src");
        }

        // =========================================================================
        // MOTOR DOORS 3D EN PRIMERA PERSONA (THREE.JS)
        // =========================================================================
        let scene3D, camera3D, renderer3D, flashlight;
        let doorsActive = false;
        let animFrameId = null;

        // Jugador y cámara
        let playerPos = new THREE.Vector3(0, 1.65, 3.2);
        let yaw = 0, pitch = 0;
        let keys = {};
        let walkTimer = 0;
        let stepSoundTimer = 0;
        let flashlightOn = true;
        let lockpicks = 0;

        // Cinemática ascensor
        let elevatorPhase = true;
        let elevatorTimer = 0;
        let elevatorGroup = null;
        let elevatorDoorLeft = null;
        let elevatorDoorRight = null;

        // Brazos 1ª persona
        let leftArmGroup, rightArmGroup;

        // Habitaciones, colisiones, puertas y cajones
        const ROOM_LENGTH = 12;
        const ROOM_WIDTH = 8;
        const ROOM_HEIGHT = 4.2;
        const MAX_ACTIVE_ROOMS = 5; // Rango de producción: máximo 5 puertas/salas en memoria

        let roomsData = [];          // Lista de salas activas { index, group, doorPivot, doorTargetRot, doorOpen, doorBox, locked, wallBoxes, drawers, lights }
        let highestRoomGenerated = -1;
        let currentRoomIndex = 0;

        // Texturas procedurales realistas
        function crearTexturaMadera() {
            const c = document.createElement('canvas');
            c.width = 256; c.height = 256;
            const ctx = c.getContext('2d');
            ctx.fillStyle = '#472212';
            ctx.fillRect(0, 0, 256, 256);
            for (let y = 0; y < 256; y += 3) {
                ctx.strokeStyle = y % 9 === 0 ? 'rgba(15, 5, 1, 0.7)' : 'rgba(28, 10, 3, 0.4)';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.bezierCurveTo(85, y + Math.sin(y * 0.1) * 8, 170, y - Math.sin(y * 0.1) * 8, 256, y);
                ctx.stroke();
            }
            ctx.fillStyle = 'rgba(10, 3, 0, 0.85)';
            for (let x = 0; x < 256; x += 64) ctx.fillRect(x, 0, 2, 256);
            const tex = new THREE.CanvasTexture(c);
            tex.wrapS = THREE.RepeatWrapping;
            tex.wrapT = THREE.RepeatWrapping;
            return tex;
        }

        function crearTexturaAlfombra() {
            const c = document.createElement('canvas');
            c.width = 256; c.height = 256;
            const ctx = c.getContext('2d');
            ctx.fillStyle = '#4a1219';
            ctx.fillRect(0, 0, 256, 256);
            ctx.strokeStyle = 'rgba(212, 175, 55, 0.25)';
            ctx.lineWidth = 4;
            ctx.strokeRect(12, 12, 232, 232);
            const tex = new THREE.CanvasTexture(c);
            tex.wrapS = THREE.RepeatWrapping;
            tex.wrapT = THREE.RepeatWrapping;
            tex.repeat.set(2, 3);
            return tex;
        }

        function crearCartelNumero(numero) {
            const c = document.createElement('canvas');
            c.width = 256; c.height = 96;
            const ctx = c.getContext('2d');
            ctx.fillStyle = '#1c1208';
            ctx.fillRect(0, 0, 256, 96);
            ctx.strokeStyle = '#d4af37';
            ctx.lineWidth = 6;
            ctx.strokeRect(6, 6, 244, 84);
            ctx.fillStyle = '#ffd700';
            ctx.font = 'bold 46px monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(String(numero).padStart(4, '0'), 128, 50);
            return new THREE.CanvasTexture(c);
        }

        let matMadera, matAlfombra, matPared;

        function initDoors3D() {
            const container = document.getElementById("doors3DContainer");
            scene3D = new THREE.Scene();
            scene3D.background = new THREE.Color(0x050508);
            scene3D.fog = new THREE.FogExp2(0x050508, 0.032);

            camera3D = new THREE.PerspectiveCamera(72, container.clientWidth / container.clientHeight, 0.1, 80);
            scene3D.add(camera3D);

            renderer3D = new THREE.WebGLRenderer({ antialias: true });
            renderer3D.setSize(container.clientWidth, container.clientHeight);
            renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            container.appendChild(renderer3D.domElement);

            // Materiales realistas
            const texMadera = crearTexturaMadera();
            const texAlfombra = crearTexturaAlfombra();
            matMadera = new THREE.MeshStandardMaterial({ map: texMadera, bumpMap: texMadera, bumpScale: 0.03, roughness: 0.6 });
            matAlfombra = new THREE.MeshStandardMaterial({ map: texAlfombra, roughness: 0.9 });
            matPared = new THREE.MeshStandardMaterial({ color: 0x2a2421, roughness: 0.85 });

            // Luz ambiental base
            const ambLight = new THREE.AmbientLight(0x404050, 0.65);
            scene3D.add(ambLight);

            // Linterna en 1ª persona
            flashlight = new THREE.SpotLight(0xfff5e0, 2.6, 28, Math.PI / 3.3, 0.45, 1.0);
            flashlight.position.set(0.25, -0.15, -0.2);
            flashlight.target.position.set(0, -0.15, -5);
            camera3D.add(flashlight);
            camera3D.add(flashlight.target);

            // Brazos y manos en 1ª persona
            crearBrazosPrimeraPersona();

            // Ascensor inicial
            crearAscensorInicial();

            // Generar primeras 5 habitaciones (0 = Vestíbulo hasta 4)
            roomsData = [];
            highestRoomGenerated = -1;
            for (let i = 0; i < MAX_ACTIVE_ROOMS; i++) {
                generarHabitacion(i);
            }

            // Posición inicial dentro del ascensor
            playerPos.set(0, 1.65, 3.5);
            yaw = 0;
            pitch = 0;
            elevatorPhase = true;
            elevatorTimer = 0;
            lockpicks = 0;
            actualizarHUD();

            // Detectar móvil
            if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
                document.getElementById("mobileControls").style.display = "block";
            }
        }

        function crearBrazosPrimeraPersona() {
            const matManga = new THREE.MeshStandardMaterial({ color: 0x1b2028, roughness: 0.8 });
            const matPiel = new THREE.MeshStandardMaterial({ color: 0xd8a888, roughness: 0.6 });
            const matMetal = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.8, roughness: 0.2 });

            leftArmGroup = new THREE.Group();
            const brazoIzq = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.11, 0.48), matManga);
            const manoIzq = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.09, 0.12), matPiel);
            manoIzq.position.z = -0.28;
            leftArmGroup.add(brazoIzq, manoIzq);
            leftArmGroup.position.set(-0.34, -0.32, -0.42);
            camera3D.add(leftArmGroup);

            rightArmGroup = new THREE.Group();
            const brazoDer = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.11, 0.48), matManga);
            const manoDer = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.09, 0.12), matPiel);
            manoDer.position.z = -0.28;
            const linternaMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.032, 0.038, 0.24, 12), matMetal);
            linternaMesh.rotation.x = Math.PI / 2;
            linternaMesh.position.set(0, 0.03, -0.36);
            rightArmGroup.add(brazoDer, manoDer, linternaMesh);
            rightArmGroup.position.set(0.34, -0.32, -0.42);
            camera3D.add(rightArmGroup);
        }

        function crearAscensorInicial() {
            elevatorGroup = new THREE.Group();
            const matReja = new THREE.MeshStandardMaterial({ color: 0x333840, metalness: 0.7, roughness: 0.4 });
            const cabina = new THREE.Mesh(new THREE.BoxGeometry(2.6, 3.2, 2.4), new THREE.MeshStandardMaterial({ color: 0x24160e, side: THREE.BackSide }));
            cabina.position.set(0, 1.6, 3.5);
            elevatorGroup.add(cabina);

            // Puertas corredizas del ascensor
            elevatorDoorLeft = new THREE.Mesh(new THREE.BoxGeometry(1.1, 2.8, 0.1), matReja);
            elevatorDoorLeft.position.set(-0.55, 1.4, 2.3);
            elevatorDoorRight = new THREE.Mesh(new THREE.BoxGeometry(1.1, 2.8, 0.1), matReja);
            elevatorDoorRight.position.set(0.55, 1.4, 2.3);
            elevatorGroup.add(elevatorDoorLeft, elevatorDoorRight);

            const luzAscensor = new THREE.PointLight(0xffaa55, 1.6, 6);
            luzAscensor.position.set(0, 2.8, 3.5);
            elevatorGroup.add(luzAscensor);

            scene3D.add(elevatorGroup);
        }

        function generarHabitacion(index) {
            const zCenter = -index * ROOM_LENGTH;
            const zFrontWall = zCenter - ROOM_LENGTH / 2; // Pared norte con la puerta al siguiente cuarto
            const zBackWall = zCenter + ROOM_LENGTH / 2;

            const roomGroup = new THREE.Group();
            const wallBoxes = [];
            const drawers = [];
            const lights = [];

            // Suelo y Techo
            const floor = new THREE.Mesh(new THREE.PlaneGeometry(ROOM_WIDTH, ROOM_LENGTH), matAlfombra);
            floor.rotation.x = -Math.PI / 2;
            floor.position.set(0, 0, zCenter);
            roomGroup.add(floor);

            const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(ROOM_WIDTH, ROOM_LENGTH), matPared);
            ceiling.rotation.x = Math.PI / 2;
            ceiling.position.set(0, ROOM_HEIGHT, zCenter);
            roomGroup.add(ceiling);

            // Paredes laterales (Izquierda y Derecha) con colisión física
            const leftWall = new THREE.Mesh(new THREE.BoxGeometry(0.4, ROOM_HEIGHT, ROOM_LENGTH), matPared);
            leftWall.position.set(-ROOM_WIDTH / 2, ROOM_HEIGHT / 2, zCenter);
            roomGroup.add(leftWall);
            wallBoxes.push(new THREE.Box3().setFromObject(leftWall));

            const rightWall = new THREE.Mesh(new THREE.BoxGeometry(0.4, ROOM_HEIGHT, ROOM_LENGTH), matPared);
            rightWall.position.set(ROOM_WIDTH / 2, ROOM_HEIGHT / 2, zCenter);
            roomGroup.add(rightWall);
            wallBoxes.push(new THREE.Box3().setFromObject(rightWall));

            // Pared trasera en el vestíbulo (index === 0)
            if (index === 0) {
                const backWall = new THREE.Mesh(new THREE.BoxGeometry(ROOM_WIDTH, ROOM_HEIGHT, 0.4), matPared);
                backWall.position.set(0, ROOM_HEIGHT / 2, zBackWall);
                roomGroup.add(backWall);
                wallBoxes.push(new THREE.Box3().setFromObject(backWall));
            }

            // Pared frontal dividida para dejar el hueco de la puerta (ancho puerta = 1.6m, alto = 2.7m)
            const sideWallW = (ROOM_WIDTH - 1.6) / 2;
            const frontLeft = new THREE.Mesh(new THREE.BoxGeometry(sideWallW, ROOM_HEIGHT, 0.4), matPared);
            frontLeft.position.set(-(1.6 / 2 + sideWallW / 2), ROOM_HEIGHT / 2, zFrontWall);
            roomGroup.add(frontLeft);
            wallBoxes.push(new THREE.Box3().setFromObject(frontLeft));

            const frontRight = new THREE.Mesh(new THREE.BoxGeometry(sideWallW, ROOM_HEIGHT, 0.4), matPared);
            frontRight.position.set(1.6 / 2 + sideWallW / 2, ROOM_HEIGHT / 2, zFrontWall);
            roomGroup.add(frontRight);
            wallBoxes.push(new THREE.Box3().setFromObject(frontRight));

            const frontTop = new THREE.Mesh(new THREE.BoxGeometry(1.6, ROOM_HEIGHT - 2.7, 0.4), matPared);
            frontTop.position.set(0, 2.7 + (ROOM_HEIGHT - 2.7) / 2, zFrontWall);
            roomGroup.add(frontTop);

            // --- PUERTA CON BISAGRA REAL, ANIMACIÓN Y COLISIÓN ---
            const doorPivot = new THREE.Group();
            // Pivote en el borde izquierdo del marco de la puerta
            doorPivot.position.set(-0.8, 0, zFrontWall);

            const doorMesh = new THREE.Mesh(new THREE.BoxGeometry(1.6, 2.7, 0.14), matMadera);
            doorMesh.position.set(0.8, 1.35, 0); // Desplazada 0.8m para girar desde la bisagra izquierda
            doorPivot.add(doorMesh);

            // Perilla de la puerta
            const matDorado = new THREE.MeshStandardMaterial({ color: 0xffd700, metalness: 0.85, roughness: 0.2 });
            const doorKnob = new THREE.Mesh(new THREE.SphereGeometry(0.07, 12, 12), matDorado);
            doorKnob.position.set(1.4, 1.25, 0.1);
            doorPivot.add(doorKnob);

            // Cartel numerado encima de la puerta
            const signMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(0.9, 0.34),
                new THREE.MeshBasicMaterial({ map: crearCartelNumero(index + 1) })
            );
            signMesh.position.set(0, 3.05, zFrontWall + 0.22);
            roomGroup.add(signMesh);

            roomGroup.add(doorPivot);

            // Caja de colisión sólida de la puerta mientras está cerrada
            const doorBox = new THREE.Box3(
                new THREE.Vector3(-0.85, 0, zFrontWall - 0.25),
                new THREE.Vector3(0.85, 2.7, zFrontWall + 0.25)
            );

            // Algunas puertas (a partir de la 3) pueden estar cerradas con llave
            const isLocked = index >= 2 && Math.random() < 0.25;

            // --- ILUMINACIÓN DE LA HABITACIÓN ---
            // Vestíbulo (0) y primeras 5 salas siempre iluminadas; luego aleatorio
            let lit = true;
            if (index > 5) {
                lit = (index % 15 === 0) ? (Math.random() < 0.25) : (Math.random() < 0.65);
            }
            if (lit) {
                const intensity = index === 0 ? 2.2 : 1.7;
                const roomLight = new THREE.PointLight(0xffdfa8, intensity, 16);
                roomLight.position.set(0, ROOM_HEIGHT - 0.3, zCenter);
                roomGroup.add(roomLight);
                lights.push(roomLight);
            }

            // --- MUEBLES CON CAJONES BIEN ORIENTADOS Y COLISIÓN ---
            // Alternamos lado izquierdo (-1) o derecho (+1) de la habitación
            const side = (index % 2 === 0) ? -1 : 1;
            const tableX = side * (ROOM_WIDTH / 2 - 0.75);
            const tableZ = zCenter - 1.2;

            // Cuerpo de la mesa/cómoda pegada a la pared
            const deskGroup = new THREE.Group();
            deskGroup.position.set(tableX, 0, tableZ);

            // Si está a la izquierda (side = -1), mira hacia la derecha (+X, rotY = Math.PI/2)
            // Si está a la derecha (side = +1), mira hacia la izquierda (-X, rotY = -Math.PI/2)
            deskGroup.rotation.y = (side === -1) ? (Math.PI / 2) : (-Math.PI / 2);

            const tableBody = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.95, 0.8), matMadera);
            tableBody.position.y = 0.475;
            deskGroup.add(tableBody);

            // Cajón deslizable orientado hacia el frente local (+Z del mueble, hacia el pasillo)
            const drawerGroup = new THREE.Group();
            drawerGroup.position.set(0, 0.72, 0.05);

            const drawerBoxMesh = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.24, 0.72), matMadera);
            drawerGroup.add(drawerBoxMesh);

            // Perilla del cajón mirando exactamente hacia el pasillo (+Z local)
            const drawerKnob = new THREE.Mesh(new THREE.SphereGeometry(0.055, 10, 10), matDorado);
            drawerKnob.position.set(0, 0, 0.39);
            drawerGroup.add(drawerKnob);

            // Contenido dentro del cajón (ej. Ganzúa dorada)
            const hasLoot = Math.random() < 0.65;
            let lootMesh = null;
            if (hasLoot) {
                lootMesh = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.04, 0.08), matDorado);
                lootMesh.position.set(0, 0.05, 0.12);
                drawerGroup.add(lootMesh);
            }

            deskGroup.add(drawerGroup);
            roomGroup.add(deskGroup);

            // Colisión sólida del mueble
            const deskCollider = new THREE.Box3().setFromCenterAndSize(
                new THREE.Vector3(tableX, 0.5, tableZ),
                new THREE.Vector3(0.95, 1.0, 1.7)
            );
            wallBoxes.push(deskCollider);

            drawers.push({
                group: drawerGroup,
                worldPos: new THREE.Vector3(tableX, 0.72, tableZ),
                open: false,
                targetZ: 0.05,
                hasLoot: hasLoot,
                lootTaken: false,
                lootMesh: lootMesh
            });

            // Armario para esconderse en el lado opuesto
            const closetX = -side * (ROOM_WIDTH / 2 - 0.7);
            const closetZ = zCenter + 1.5;
            const closetMesh = new THREE.Mesh(new THREE.BoxGeometry(1.0, 2.5, 1.4), matMadera);
            closetMesh.position.set(closetX, 1.25, closetZ);
            roomGroup.add(closetMesh);
            wallBoxes.push(new THREE.Box3().setFromObject(closetMesh));

            scene3D.add(roomGroup);

            roomsData.push({
                index: index,
                zFrontWall: zFrontWall,
                group: roomGroup,
                doorPivot: doorPivot,
                doorOpen: false,
                doorTargetRot: 0,
                doorBox: doorBox,
                locked: isLocked,
                wallBoxes: wallBoxes,
                drawers: drawers,
                lights: lights
            });

            if (index > highestRoomGenerated) highestRoomGenerated = index;
        }

        // RANGO DE PRODUCCIÓN Y LIMPIEZA DE MEMORIA (SI AVANZA 5 PUERTAS, ELIMINA LAS ANTERIORES)
        function gestionarRangoProduccion() {
            // Determinar en qué habitación está el jugador según su coordenada Z
            const calcRoom = Math.max(0, Math.floor((-playerPos.z + ROOM_LENGTH / 2) / ROOM_LENGTH));
            if (calcRoom !== currentRoomIndex) {
                currentRoomIndex = calcRoom;
                actualizarHUD();
            }

            // Generar habitaciones por delante hasta mantener un rango de 5 puertas adelante
            while (highestRoomGenerated < currentRoomIndex + MAX_ACTIVE_ROOMS) {
                generarHabitacion(highestRoomGenerated + 1);
            }

            // Eliminar habitaciones que quedaron 5 puertas atrás para liberar memoria
            while (roomsData.length > 0 && roomsData[0].index <= currentRoomIndex - MAX_ACTIVE_ROOMS) {
                const oldRoom = roomsData.shift();
                scene3D.remove(oldRoom.group);
                // Liberar geometrías de memoria
                oldRoom.group.traverse((obj) => {
                    if (obj.geometry) obj.geometry.dispose();
                });
            }
        }

        function checkCollision(nextPos) {
            const playerRadius = 0.38;
            const playerSphere = new THREE.Sphere(new THREE.Vector3(nextPos.x, 1.0, nextPos.z), playerRadius);

            for (const room of roomsData) {
                // Colisión con paredes y muebles
                for (const box of room.wallBoxes) {
                    if (box.intersectsSphere(playerSphere)) return true;
                }
                // Colisión con puertas cerradas (no se pueden atravesar)
                if (!room.doorOpen && room.doorBox.intersectsSphere(playerSphere)) {
                    return true;
                }
            }
            return false;
        }

        function interactuar() {
            if (elevatorPhase) return;

            // 1. Revisar cercanía a puertas
            for (const room of roomsData) {
                const doorCenter = new THREE.Vector3(0, 1.35, room.zFrontWall);
                if (!room.doorOpen && playerPos.distanceTo(doorCenter) < 2.6) {
                    if (room.locked) {
                        if (lockpicks > 0) {
                            lockpicks--;
                            room.locked = false;
                            actualizarHUD("Cerradura forzada con ganzúa");
                        } else {
                            actualizarHUD("Puerta cerrada con llave (Busca una ganzúa en los cajones)");
                            return;
                        }
                    }
                    // Abrir puerta con animación y sonido de chirrido
                    room.doorOpen = true;
                    room.doorTargetRot = -Math.PI * 0.48; // Abre hacia adentro
                    playSound('creak');
                    actualizarHUD(`Puerta ${String(room.index + 1).padStart(4, '0')} abierta`);
                    return;
                }

                // 2. Revisar cercanía a cajones
                for (const d of room.drawers) {
                    if (playerPos.distanceTo(d.worldPos) < 2.4) {
                        if (!d.open) {
                            d.open = true;
                            d.targetZ = 0.45; // Se desliza hacia afuera mostrando su contenido
                            playSound('drawer');
                        } else if (d.hasLoot && !d.lootTaken) {
                            d.lootTaken = true;
                            if (d.lootMesh) d.lootMesh.visible = false;
                            lockpicks++;
                            playSound('pickup');
                            actualizarHUD("¡Recogiste una Ganzúa!");
                        } else {
                            d.open = false;
                            d.targetZ = 0.05;
                            playSound('drawer');
                        }
                        return;
                    }
                }
            }
        }

        function actualizarHUD(statusMsg) {
            document.getElementById("hudRoom").innerText = `STANZA: ${String(currentRoomIndex).padStart(4, '0')}`;
            document.getElementById("hudInv").innerText = `🔑 Grimaldelli: ${lockpicks} | 🔦 Torcia: ${flashlightOn ? 'ON' : 'OFF'}`;
            if (statusMsg) {
                document.getElementById("hudStatus").innerText = statusMsg;
            }
        }

        function updateDoors3D(dt) {
            // 1. Cinemática inicial del ascensor
            if (elevatorPhase) {
                elevatorTimer += dt;
                // Vibración sutil subiendo
                camera3D.position.set(
                    playerPos.x + (Math.random() - 0.5) * 0.02,
                    playerPos.y + (Math.random() - 0.5) * 0.02,
                    playerPos.z
                );
                if (elevatorTimer > 2.2) {
                    if (elevatorDoorLeft.position.x > -1.45) {
                        if (elevatorDoorLeft.position.x === -0.55) playSound('ding');
                        elevatorDoorLeft.position.x -= 1.2 * dt;
                        elevatorDoorRight.position.x += 1.2 * dt;
                    } else {
                        elevatorPhase = false;
                        actualizarHUD("Benvenuto nella Lobby");
                    }
                }
                return;
            }

            // 2. Movimiento del jugador con colisión física
            const speed = 4.6 * dt;
            const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
            const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
            let moveVec = new THREE.Vector3();

            if (keys['KeyW'] || keys['ArrowUp']) moveVec.add(forward);
            if (keys['KeyS'] || keys['ArrowDown']) moveVec.sub(forward);
            if (keys['KeyD'] || keys['ArrowRight']) moveVec.add(right);
            if (keys['KeyA'] || keys['ArrowLeft']) moveVec.sub(right);

            const isMoving = moveVec.lengthSq() > 0;
            if (isMoving) {
                moveVec.normalize().multiplyScalar(speed);
                // Deslizamiento suave por ejes para no quedarse pegado a paredes
                const tryX = playerPos.clone().add(new THREE.Vector3(moveVec.x, 0, 0));
                if (!checkCollision(tryX)) playerPos.x = tryX.x;

                const tryZ = playerPos.clone().add(new THREE.Vector3(0, 0, moveVec.z));
                if (!checkCollision(tryZ)) playerPos.z = tryZ.z;

                walkTimer += dt * 9;
                stepSoundTimer += dt;
                if (stepSoundTimer > 0.45) {
                    stepSoundTimer = 0;
                    playSound('step');
                }
            } else {
                walkTimer = 0;
            }

            // Efecto de caminar en cámara y brazos
            const bobY = isMoving ? Math.sin(walkTimer * 2) * 0.045 : 0;
            camera3D.position.set(playerPos.x, playerPos.y + bobY, playerPos.z);
            camera3D.rotation.order = 'YXZ';
            camera3D.rotation.y = yaw;
            camera3D.rotation.x = pitch;

            if (leftArmGroup && rightArmGroup) {
                leftArmGroup.position.y = -0.32 + (isMoving ? Math.sin(walkTimer) * 0.025 : 0);
                rightArmGroup.position.y = -0.32 + (isMoving ? -Math.sin(walkTimer) * 0.025 : 0);
            }

            // 3. Animación suave de apertura de puertas y cajones
            let promptVisible = false;
            const promptEl = document.getElementById("promptText");

            for (const room of roomsData) {
                // Animación rotación de puerta sobre bisagra
                if (Math.abs(room.doorPivot.rotation.y - room.doorTargetRot) > 0.005) {
                    room.doorPivot.rotation.y += (room.doorTargetRot - room.doorPivot.rotation.y) * 6 * dt;
                }

                const doorCenter = new THREE.Vector3(0, 1.35, room.zFrontWall);
                if (!room.doorOpen && playerPos.distanceTo(doorCenter) < 2.6) {
                    promptVisible = true;
                    promptEl.innerText = room.locked
                        ? `[E / Clic] Forzare Porta ${String(room.index + 1).padStart(4, '0')} (Serve 1 Grimaldello)`
                        : `[E / Clic] Apri Porta ${String(room.index + 1).padStart(4, '0')}`;
                }

                for (const d of room.drawers) {
                    // Animación suave de deslizamiento del cajón
                    d.group.position.z += (d.targetZ - d.group.position.z) * 10 * dt;

                    if (playerPos.distanceTo(d.worldPos) < 2.4) {
                        promptVisible = true;
                        if (!d.open) {
                            promptEl.innerText = "[E / Clic] Apri cassetto";
                        } else if (d.hasLoot && !d.lootTaken) {
                            promptEl.innerText = "[E / Clic] Prendi Grimaldello 🔑";
                        } else {
                            promptEl.innerText = "[E / Clic] Chiudi cassetto";
                        }
                    }
                }
            }

            promptEl.style.display = promptVisible ? "block" : "none";

            // 4. Rango de producción y limpieza cada 5 puertas
            gestionarRangoProduccion();
        }

        let lastTime = performance.now();
        function bucleDoors3D(now) {
            if (!doorsActive) return;
            const dt = Math.min((now - lastTime) / 1000, 0.05);
            lastTime = now;

            updateDoors3D(dt);
            renderer3D.render(scene3D, camera3D);
            animFrameId = requestAnimationFrame(bucleDoors3D);
        }

        function abrirJuego() {
            const modal = document.getElementById("gameModal");
            modal.style.display = "flex";
            document.getElementById("startOverlay3D").style.display = "flex";

            if (!renderer3D) {
                initDoors3D();
            }
            doorsActive = true;
            lastTime = performance.now();
            bucleDoors3D(lastTime);
            musicaHotelReal.currentTime = 0;
            musicaHotelReal.play().catch(() => {});
        }

        function cerrarJuego() {
            doorsActive = false;
            if (animFrameId) cancelAnimationFrame(animFrameId);
            musicaHotelReal.pause();
            if (document.pointerLockElement) document.exitPointerLock();
            document.getElementById("gameModal").style.display = "none";
        }

        function iniciarControl3D() {
            document.getElementById("startOverlay3D").style.display = "none";
            const container = document.getElementById("doors3DContainer");
            if (container.requestPointerLock) {
                container.requestPointerLock();
            }
            musicaHotelReal.play().catch(() => {});
        }

        function toggleFullscreen() {
            const box = document.getElementById("gameModalBox");
            if (!document.fullscreenElement) {
                box.requestFullscreen().catch(() => {});
            } else {
                document.exitFullscreen().catch(() => {});
            }
        }

        // Eventos PC (Teclado, Ratón y F11)
        window.addEventListener("keydown", (e) => {
            keys[e.code] = true;
            if (!doorsActive) return;

            if (e.code === "KeyF") {
                flashlightOn = !flashlightOn;
                flashlight.visible = flashlightOn;
                actualizarHUD();
            }
            if (e.code === "KeyE") {
                interactuar();
            }
            if (e.key === "F11") {
                e.preventDefault();
                toggleFullscreen();
            }
        });

        window.addEventListener("keyup", (e) => {
            keys[e.code] = false;
        });

        window.addEventListener("mousemove", (e) => {
            if (!doorsActive) return;
            if (document.pointerLockElement === document.getElementById("doors3DContainer")) {
                yaw -= e.movementX * 0.0022;
                pitch -= e.movementY * 0.0022;
                pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
            }
        });

        document.getElementById("doors3DContainer").addEventListener("mousedown", () => {
            if (!doorsActive) return;
            if (document.getElementById("startOverlay3D").style.display !== "none") return;
            if (document.pointerLockElement !== document.getElementById("doors3DContainer") && !('ontouchstart' in window)) {
                document.getElementById("doors3DContainer").requestPointerLock();
            } else {
                interactuar();
            }
        });

        // Controles Táctiles (Móvil / Tablet)
        let lastTouchX = 0, lastTouchY = 0;
        const container3D = document.getElementById("doors3DContainer");
        container3D.addEventListener("touchstart", (e) => {
            lastTouchX = e.touches[0].clientX;
            lastTouchY = e.touches[0].clientY;
        }, { passive: true });

        container3D.addEventListener("touchmove", (e) => {
            const dx = e.touches[0].clientX - lastTouchX;
            const dy = e.touches[0].clientY - lastTouchY;
            lastTouchX = e.touches[0].clientX;
            lastTouchY = e.touches[0].clientY;
            yaw -= dx * 0.005;
            pitch -= dy * 0.005;
            pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
        }, { passive: true });

        function bindTouchBtn(id, keyCode) {
            const btn = document.getElementById(id);
            btn.addEventListener("touchstart", (e) => { e.preventDefault(); keys[keyCode] = true; });
            btn.addEventListener("touchend", (e) => { e.preventDefault(); keys[keyCode] = false; });
        }
        bindTouchBtn("btnUp", "KeyW");
        bindTouchBtn("btnDown", "KeyS");
        bindTouchBtn("btnLeft", "KeyA");
        bindTouchBtn("btnRight", "KeyD");

        document.getElementById("btnFlash").addEventListener("touchstart", (e) => {
            e.preventDefault();
            flashlightOn = !flashlightOn;
            flashlight.visible = flashlightOn;
            actualizarHUD();
        });
        document.getElementById("btnInteract").addEventListener("touchstart", (e) => {
            e.preventDefault();
            interactuar();
        });

        window.addEventListener("resize", () => {
            if (!renderer3D || !camera3D) return;
            const c = document.getElementById("doors3DContainer");
            camera3D.aspect = c.clientWidth / c.clientHeight;
            camera3D.updateProjectionMatrix();
            renderer3D.setSize(c.clientWidth, c.clientHeight);
        });
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return render_template_string(
        PAGINA_WEB,
        version=APP_VERSION,
        clave=CONTRASEÑA_CORRECTA,
        subtitulos_raw=SUBTITULOS_VTT_BASE,
        portada=PORTADA_DEADPOOL
    )

@app.route('/stream-video')
def stream_video():
    range_header = request.headers.get('Range', None)
    headers = {'User-Agent': 'Mozilla/5.0'}
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
