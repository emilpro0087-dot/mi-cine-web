import os
import requests
from flask import Flask, render_template_string, Response, request

app = Flask(__name__)

# CONTROL DE VERSIÓN DE LA WEB (Sube +0.1 en cada actualización)
APP_VERSION = "v0.4"

CONTRASEÑA_CORRECTA = "perrofeoxd"

# Enlace directo al archivo .mp4 de Archive.org
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
    <title>Cinema Privato // Cinema & Arcade Vault ({{ version }})</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍿</text></svg>">
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

        /* INSIGNIA FIJA DE VERSIÓN EN ESQUINA SUPERIOR IZQUIERDA */
        .version-badge {
            position: fixed;
            top: 14px;
            left: 14px;
            z-index: 9999;
            background: rgba(10, 16, 26, 0.85);
            border: 1px solid rgba(0, 240, 255, 0.45);
            border-radius: 6px;
            padding: 5px 12px;
            font-family: monospace;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            color: #00f0ff;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
            backdrop-filter: blur(8px);
            pointer-events: none;
        }

        /* ENTRADA ORIGINAL DE LA WEB (LOADER CON ENGRANAJES) */
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

        /* LOGIN ORIGINAL DE SIEMPRE */
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
            user-select: text;
            -webkit-user-select: text;
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

        /* CATÁLOGO ORIGINAL DE SIEMPRE */
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
            z-index: 50;
            text-shadow: 0 0 8px #000;
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

        /* CONTENEDOR DOORS 3D */
        #gameModalBox {
            width: 95vw;
            max-width: 1120px;
            height: 84vh;
            border: 2px solid #00f0ff;
            position: relative;
            background: #050508;
            box-shadow: 0 0 50px rgba(0, 240, 255, 0.3);
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

    <!-- ETIQUETA FIJA DE VERSIÓN -->
    <div class="version-badge">{{ version }}</div>

    <!-- PANTALLA DE CARGA ORIGINAL -->
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

    <!-- LOGIN ORIGINAL DE SIEMPRE -->
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

    <!-- CATÁLOGO ORIGINAL DE SIEMPRE -->
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

                <!-- Tarjeta 2: Juego DOORS 3D -->
                <div class="movie-card game-card" onclick="playAudio('open'); abrirJuego()">
                    <div style="height: 390px; background: radial-gradient(circle, #0e1e38 0%, #060911 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px;">
                        <span style="font-size: 80px; filter: drop-shadow(0 0 20px #00f0ff);">🚪</span>
                        <span style="font-family: monospace; font-size: 13px; letter-spacing: 3px; color: #00f0ff;">DOORS 3D</span>
                    </div>
                    <div class="info">
                        <h3>DOORS 3D: L'HOTEL</h3>
                        <div class="badges">
                            <span class="badge-pill" style="border-color: #00f0ff; color: #00f0ff;">1ª PERSONA</span>
                            <span class="badge-pill">PC & MOBILE</span>
                            <span>Horror 3D</span>
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

    <!-- Modal Juego Doors 3D -->
    <div id="gameModal" class="modal">
        <div class="modal-box" id="gameModalBox">
            <button id="btnFullscreen" onclick="toggleFullscreen()">[F11] SCHERMO INTERO</button>
            <span class="modal-close" onclick="cerrarJuego()">&times;</span>

            <div id="doors3DContainer">
                <div id="doorsHUD">
                    <div class="hud-pill" id="hudRoom">STANZA: LOBBY (0000)</div>
                    <div class="hud-pill" id="hudInv">🔑 Grimaldelli: 0 | 🔋 Batteria: 100% | 🔦 Torcia: ON</div>
                    <div class="hud-pill" id="hudStatus" style="color: #00f0ff;">Ascensore in salita...</div>
                </div>

                <div id="crosshair"></div>
                <div id="promptText">Premi [E] o Clic per interagire</div>

                <div id="startOverlay3D" onclick="iniciarControl3D()">
                    <h2 style="color: #00f0ff; font-family: monospace; font-size: 26px; margin-bottom: 10px;">DOORS 3D - L'HOTEL</h2>
                    <p style="color: #ccc; max-width: 500px; font-size: 14px; line-height: 1.5; margin-bottom: 20px;">
                        PC: [WASD] Muovi • [Mouse] Guarda • [E / Clic] Apri porte, cassetti e armadi • [F] Torcia • [F11] Schermo intero<br>
                        ATTENZIONE: Se le luci sfarfallano, nasconditi subito in un ARMADIO!
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
        // --- AUDIO PROCEDURAL (INTERFAZ + PUERTAS + PASOS + CAJONES + MONSTRUO IA) ---
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        function playAudio(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
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

            } else if (type === 'creak') {
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

            } else if (type === 'unlock') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'square';
                osc.frequency.setValueAtTime(300, now);
                osc.frequency.setValueAtTime(520, now + 0.08);
                gain.gain.setValueAtTime(0.14, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.22);

            } else if (type === 'monster') {
                // Rugido aterrador de Rush acercándose
                const osc = audioCtx.createOscillator();
                const osc2 = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc2.type = 'square';
                osc.frequency.setValueAtTime(55, now);
                osc.frequency.linearRampToValueAtTime(135, now + 1.4);
                osc.frequency.linearRampToValueAtTime(42, now + 2.6);

                osc2.frequency.setValueAtTime(61, now);
                osc2.frequency.linearRampToValueAtTime(148, now + 1.4);
                osc2.frequency.linearRampToValueAtTime(38, now + 2.6);

                gain.gain.setValueAtTime(0.02, now);
                gain.gain.linearRampToValueAtTime(0.24, now + 1.3);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 2.7);
                osc.connect(gain);
                osc2.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc2.start(now);
                osc.stop(now + 2.7);
                osc2.stop(now + 2.7);
            }
        }

        // Música real descargada en /static/Corredor_Horror.mp3
        const musicaHotelReal = new Audio('/static/Corredor_Horror.mp3');
        musicaHotelReal.loop = true;
        musicaHotelReal.volume = 0.42;

        // --- ENTRADA ORIGINAL DE LA WEB (LOADER & LOGIN) ---
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

        // --- SUBTÍTULOS Y REPRODUCTOR DE VIDEO ---
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
                playPromise.catch(() => {});
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

        // =========================================================================
        // MOTOR DOORS 3D EN PRIMERA PERSONA (THREE.JS)
        // =========================================================================
        let scene3D, camera3D, renderer3D, flashlight;
        let doorsActive = false;
        let animFrameId = null;

        // Jugador, inventario y estados
        let playerPos = new THREE.Vector3(0, 1.75, 6.2);
        let yaw = 0, pitch = 0;
        let keys = {};
        let walkTimer = 0;
        let stepSoundTimer = 0;
        let flashlightOn = true;
        let battery = 100;
        let lockpicks = 0;
        let isHiding = false;
        let savedPosBeforeHide = new THREE.Vector3();

        // Cinemática ascensor
        let elevatorPhase = true;
        let elevatorTimer = 0;
        let elevatorDingPlayed = false;
        let elevatorGroup = null;
        let elevatorDoorLeft = null;
        let elevatorDoorRight = null;
        let elevatorFloorCanvas = null;
        let elevatorFloorTex = null;
        let lastFloorText = "";

        // Brazos y manos orgánicas 1ª persona
        let leftArmGroup, rightArmGroup;

        // Dimensiones amplias de salas, puertas y rango de memoria (5 puertas)
        const ROOM_LENGTH = 18;
        const ROOM_WIDTH = 14;
        const ROOM_HEIGHT = 5.2;
        const DOOR_WIDTH = 2.2;
        const DOOR_HEIGHT = 3.3;
        const MAX_ACTIVE_ROOMS = 5;

        let roomsData = [];
        let highestRoomGenerated = -1;
        let currentRoomIndex = 0;
        let rainSystems = []; // Gotas de lluvia animadas en las ventanas

        // IA DEL MONSTRUO (RUSH)
        let monsterMesh = null;
        let monsterActive = false;
        let monsterWarningTimer = 0;
        let monsterZ = 0;
        let monsterCooldown = 14;

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
            tex.repeat.set(3, 4);
            return tex;
        }

        // PLACA DE NÚMERO ESTILO DOORS (MADERA TALLADA CON LETRAS BLANCAS/CREMA, NO AMARILLA)
        function crearCartelMaderaDoors(numero) {
            const c = document.createElement('canvas');
            c.width = 256; c.height = 96;
            const ctx = c.getContext('2d');

            // Fondo de madera oscura envejecida
            ctx.fillStyle = '#2d160b';
            ctx.fillRect(0, 0, 256, 96);

            // Vetas de madera en el cartel
            for (let y = 0; y < 96; y += 3) {
                ctx.strokeStyle = 'rgba(15, 6, 2, 0.45)';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(256, y + Math.sin(y * 0.2) * 3);
                ctx.stroke();
            }

            // Marco tallado en madera clara/bronce envejecido
            ctx.strokeStyle = '#7c5332';
            ctx.lineWidth = 8;
            ctx.strokeRect(4, 4, 248, 88);
            ctx.strokeStyle = '#180a04';
            ctx.lineWidth = 2;
            ctx.strokeRect(10, 10, 236, 76);

            // Número tallado en color marfil/blanco hueso (como en DOORS original)
            ctx.fillStyle = '#efe6d5';
            ctx.shadowColor = '#000000';
            ctx.shadowBlur = 4;
            ctx.shadowOffsetX = 2;
            ctx.shadowOffsetY = 2;
            ctx.font = 'bold 46px Georgia, serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(String(numero).padStart(4, '0'), 128, 50);

            return new THREE.CanvasTexture(c);
        }

        // TEXTURA DE CUADROS ARTÍSTICOS PARA EL VESTÍBULO
        function crearTexturaCuadro(tipo) {
            const c = document.createElement('canvas');
            c.width = 256; c.height = 320;
            const ctx = c.getContext('2d');
            if (tipo === 0) {
                // Paisaje nocturno del hotel
                const grad = ctx.createLinearGradient(0, 0, 0, 320);
                grad.addColorStop(0, '#0a1428');
                grad.addColorStop(1, '#1e2d42');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 256, 320);
                ctx.fillStyle = '#e8eef5';
                ctx.beginPath();
                ctx.arc(185, 70, 26, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#090d14';
                ctx.beginPath();
                ctx.moveTo(0, 250);
                ctx.lineTo(90, 140);
                ctx.lineTo(170, 220);
                ctx.lineTo(256, 150);
                ctx.lineTo(256, 320);
                ctx.lineTo(0, 320);
                ctx.fill();
            } else {
                // Retrato clásico victoriano oscuro
                ctx.fillStyle = '#24140e';
                ctx.fillRect(0, 0, 256, 320);
                ctx.fillStyle = '#111116';
                ctx.beginPath();
                ctx.ellipse(128, 255, 65, 85, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#c8a688';
                ctx.beginPath();
                ctx.ellipse(128, 135, 34, 44, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#181412';
                ctx.fillRect(92, 85, 72, 22);
            }
            return new THREE.CanvasTexture(c);
        }

        let matMadera, matAlfombra, matPared, matHierroViejo, matOro;

        function initDoors3D() {
            const container = document.getElementById("doors3DContainer");
            scene3D = new THREE.Scene();
            scene3D.background = new THREE.Color(0x050508);
            scene3D.fog = new THREE.FogExp2(0x050508, 0.022);

            camera3D = new THREE.PerspectiveCamera(72, container.clientWidth / container.clientHeight, 0.1, 100);
            scene3D.add(camera3D);

            renderer3D = new THREE.WebGLRenderer({ antialias: true });
            renderer3D.setSize(container.clientWidth, container.clientHeight);
            renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            container.appendChild(renderer3D.domElement);

            const texMadera = crearTexturaMadera();
            const texAlfombra = crearTexturaAlfombra();
            matMadera = new THREE.MeshStandardMaterial({ map: texMadera, bumpMap: texMadera, bumpScale: 0.03, roughness: 0.6 });
            matAlfombra = new THREE.MeshStandardMaterial({ map: texAlfombra, roughness: 0.9 });
            matPared = new THREE.MeshStandardMaterial({ color: 0x332924, roughness: 0.85 });
            matHierroViejo = new THREE.MeshStandardMaterial({ color: 0x2c2825, metalness: 0.8, roughness: 0.65 });
            matOro = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.85, roughness: 0.25 });

            const ambLight = new THREE.AmbientLight(0x4a4a5a, 0.75);
            scene3D.add(ambLight);

            flashlight = new THREE.SpotLight(0xfff5e0, 2.7, 34, Math.PI / 3.2, 0.45, 1.0);
            flashlight.position.set(0.25, -0.15, -0.2);
            flashlight.target.position.set(0, -0.15, -6);
            camera3D.add(flashlight);
            camera3D.add(flashlight.target);

            crearBrazosOrganicos();
            crearAscensorRealista();
            crearMonstruoIA();

            roomsData = [];
            rainSystems = [];
            highestRoomGenerated = -1;
            for (let i = 0; i < MAX_ACTIVE_ROOMS; i++) {
                generarHabitacion(i);
            }

            playerPos.set(0, 1.75, 6.2);
            yaw = 0;
            pitch = 0;
            elevatorPhase = true;
            elevatorTimer = 0;
            elevatorDingPlayed = false;
            lockpicks = 0;
            battery = 100;
            isHiding = false;
            monsterActive = false;
            monsterWarningTimer = 0;
            monsterCooldown = 14;
            actualizarHUD();

            if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
                document.getElementById("mobileControls").style.display = "block";
            }
        }

        function crearBrazosOrganicos() {
            const matManga = new THREE.MeshStandardMaterial({ color: 0x1e242d, roughness: 0.75 });
            const matPiel = new THREE.MeshStandardMaterial({ color: 0xdca98a, roughness: 0.55 });
            const matMetal = new THREE.MeshStandardMaterial({ color: 0x15181e, metalness: 0.85, roughness: 0.2 });

            function buildArm(conLinterna) {
                const armGroup = new THREE.Group();
                const forearm = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.058, 0.42, 16), matManga);
                forearm.rotation.x = Math.PI / 2.15;
                armGroup.add(forearm);

                const palm = new THREE.Mesh(new THREE.SphereGeometry(0.048, 16, 16), matPiel);
                palm.scale.set(0.95, 0.75, 1.25);
                palm.position.set(0, 0.015, -0.23);
                armGroup.add(palm);

                for (let f = -1.5; f <= 1.5; f += 1) {
                    const finger = new THREE.Mesh(new THREE.CylinderGeometry(0.009, 0.011, 0.075, 10), matPiel);
                    finger.rotation.x = Math.PI / 2.6;
                    finger.position.set(f * 0.018, 0.01, -0.29);
                    armGroup.add(finger);
                }

                if (conLinterna) {
                    const body = new THREE.Mesh(new THREE.CylinderGeometry(0.026, 0.024, 0.22, 16), matMetal);
                    body.rotation.x = Math.PI / 2.1;
                    body.position.set(0, 0.032, -0.26);
                    const head = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.026, 0.06, 16), matMetal);
                    head.rotation.x = Math.PI / 2.1;
                    head.position.set(0, 0.038, -0.38);
                    armGroup.add(body, head);
                }
                return armGroup;
            }

            leftArmGroup = buildArm(false);
            leftArmGroup.position.set(-0.32, -0.29, -0.36);
            camera3D.add(leftArmGroup);

            rightArmGroup = buildArm(true);
            rightArmGroup.position.set(0.32, -0.29, -0.36);
            camera3D.add(rightArmGroup);
        }

        // ASCENSOR REALISTA DE HOTEL CON PANELES DE MADERA, PASAMANOS Y REJAS CON BARROTES
        function actualizarDisplayAscensor(texto) {
            if (!elevatorFloorCanvas || lastFloorText === texto) return;
            lastFloorText = texto;
            const ctx = elevatorFloorCanvas.getContext('2d');
            ctx.fillStyle = '#090d14';
            ctx.fillRect(0, 0, 256, 80);
            ctx.strokeStyle = '#d4af37';
            ctx.lineWidth = 4;
            ctx.strokeRect(4, 4, 248, 72);
            ctx.fillStyle = '#ffaa22';
            ctx.font = 'bold 34px monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(texto, 128, 42);
            if (elevatorFloorTex) elevatorFloorTex.needsUpdate = true;
        }

        function crearAscensorRealista() {
            elevatorGroup = new THREE.Group();
            const matCabinaMadera = new THREE.MeshStandardMaterial({ map: crearTexturaMadera(), roughness: 0.5, side: THREE.BackSide });
            const matRejaMetal = new THREE.MeshStandardMaterial({ color: 0x2b3038, metalness: 0.85, roughness: 0.3 });

            // Cabina de madera elegante
            const cabina = new THREE.Mesh(new THREE.BoxGeometry(3.4, 3.8, 3.2), matCabinaMadera);
            cabina.position.set(0, 1.9, 6.2);
            elevatorGroup.add(cabina);

            // Pasamanos de latón dorado dentro del ascensor
            const railBack = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 3.0, 12), matOro);
            railBack.rotation.z = Math.PI / 2;
            railBack.position.set(0, 1.05, 7.72);
            const railLeft = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.8, 12), matOro);
            railLeft.rotation.x = Math.PI / 2;
            railLeft.position.set(-1.62, 1.05, 6.2);
            const railRight = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 2.8, 12), matOro);
            railRight.rotation.x = Math.PI / 2;
            railRight.position.set(1.62, 1.05, 6.2);
            elevatorGroup.add(railBack, railLeft, railRight);

            // Plafón luminoso en el techo
            const plafon = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 1.4), new THREE.MeshBasicMaterial({ color: 0xffe8b5 }));
            plafon.position.set(0, 3.74, 6.2);
            elevatorGroup.add(plafon);

            // Visor de pisos
            elevatorFloorCanvas = document.createElement('canvas');
            elevatorFloorCanvas.width = 256;
            elevatorFloorCanvas.height = 80;
            elevatorFloorTex = new THREE.CanvasTexture(elevatorFloorCanvas);
            actualizarDisplayAscensor("▲ B2");

            const displayMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(1.2, 0.36),
                new THREE.MeshBasicMaterial({ map: elevatorFloorTex })
            );
            displayMesh.position.set(0, 3.3, 4.62);
            elevatorGroup.add(displayMesh);

            // Puertas de reja metálica con barrotes reales
            function crearHojaReja() {
                const hoja = new THREE.Group();
                const marco = new THREE.Mesh(new THREE.BoxGeometry(1.45, 3.1, 0.08), matRejaMetal);
                hoja.add(marco);
                for (let bx = -0.55; bx <= 0.55; bx += 0.22) {
                    const barrote = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 2.9, 8), matOro);
                    barrote.position.set(bx, 0, 0.05);
                    hoja.add(barrote);
                }
                return hoja;
            }

            elevatorDoorLeft = crearHojaReja();
            elevatorDoorLeft.position.set(-0.72, 1.55, 4.6);
            elevatorDoorRight = crearHojaReja();
            elevatorDoorRight.position.set(0.72, 1.55, 4.6);
            elevatorGroup.add(elevatorDoorLeft, elevatorDoorRight);

            const luzAscensor = new THREE.PointLight(0xffc978, 2.0, 9);
            luzAscensor.position.set(0, 3.4, 6.2);
            elevatorGroup.add(luzAscensor);

            scene3D.add(elevatorGroup);
        }

        // CONSTRUIR CANDADO VIEJO DE HIERRO FORJADO PARA PUERTAS CERRADAS
        function crearCandadoViejo() {
            const lockGroup = new THREE.Group();
            // Cuerpo pesado del candado
            const body = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.28, 0.09), matHierroViejo);
            lockGroup.add(body);

            // Arco superior de acero oxidado
            const shackle = new THREE.Mesh(new THREE.TorusGeometry(0.085, 0.022, 8, 16, Math.PI), matHierroViejo);
            shackle.position.set(0, 0.14, 0);
            lockGroup.add(shackle);

            // Bocallave oscura en el centro
            const keyhole = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.08, 0.1), new THREE.MeshBasicMaterial({ color: 0x050505 }));
            keyhole.position.set(0, -0.02, 0.01);
            lockGroup.add(keyhole);

            return lockGroup;
        }

        // CREAR VENTANA NOCTURNA CON LUNA LLENA Y LLUVIA ANIMADA
        function crearVentanaNocheLluvia(x, y, z, rotY) {
            const winGroup = new THREE.Group();
            winGroup.position.set(x, y, z);
            winGroup.rotation.y = rotY;

            // Fondo cielo nocturno profundo
            const sky = new THREE.Mesh(
                new THREE.PlaneGeometry(3.2, 2.8),
                new THREE.MeshBasicMaterial({ color: 0x070d1c })
            );
            sky.position.z = -0.04;
            winGroup.add(sky);

            // Luna llena brillante con halo
            const moon = new THREE.Mesh(
                new THREE.CircleGeometry(0.36, 24),
                new THREE.MeshBasicMaterial({ color: 0xf4f7ff })
            );
            moon.position.set(0.75, 0.72, -0.03);
            winGroup.add(moon);

            // Marco de madera de la ventana (4 bordes + cruz central)
            const topBar = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.18, 0.14), matMadera);
            topBar.position.y = 1.4;
            const botBar = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.22, 0.18), matMadera);
            botBar.position.y = -1.4;
            const leftBar = new THREE.Mesh(new THREE.BoxGeometry(0.18, 2.9, 0.14), matMadera);
            leftBar.position.x = -1.6;
            const rightBar = new THREE.Mesh(new THREE.BoxGeometry(0.18, 2.9, 0.14), matMadera);
            rightBar.position.x = 1.6;
            const midV = new THREE.Mesh(new THREE.BoxGeometry(0.09, 2.8, 0.1), matMadera);
            const midH = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.09, 0.1), matMadera);
            winGroup.add(topBar, botBar, leftBar, rightBar, midV, midH);

            // Gotas de lluvia cayendo detrás del cristal
            const rainDrops = [];
            const matGota = new THREE.MeshBasicMaterial({ color: 0x7aa4d4, transparent: true, opacity: 0.65 });
            for (let r = 0; r < 28; r++) {
                const drop = new THREE.Mesh(new THREE.BoxGeometry(0.015, 0.22, 0.01), matGota);
                drop.position.set((Math.random() - 0.5) * 3.0, (Math.random() - 0.5) * 2.5, -0.015);
                winGroup.add(drop);
                rainDrops.push(drop);
            }
            rainSystems.push(rainDrops);

            return winGroup;
        }

        // DECORACIÓN ULTRA REALISTA EXCLUSIVA PARA EL VESTÍBULO (LOBBY)
        function decorarVestibulo(roomGroup, wallBoxes, zCenter) {
            // 1. Mostrador de Recepción de madera tallada a la izquierda
            const deskGroup = new THREE.Group();
            deskGroup.position.set(-4.8, 0, zCenter - 1.5);

            const counterBase = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.15, 5.2), matMadera);
            counterBase.position.y = 0.575;
            const counterTop = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.1, 5.4), matOro);
            counterTop.position.y = 1.18;
            deskGroup.add(counterBase, counterTop);

            // Campana dorada de recepción
            const bell = new THREE.Mesh(new THREE.SphereGeometry(0.1, 14, 14), matOro);
            bell.position.set(0.4, 1.28, 0.6);
            deskGroup.add(bell);

            // Lámpara de escritorio cálida
            const lampStand = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.12, 0.45, 12), matOro);
            lampStand.position.set(0.3, 1.42, -1.2);
            const lampShade = new THREE.Mesh(new THREE.ConeGeometry(0.24, 0.22, 16), new THREE.MeshStandardMaterial({ color: 0x165b33, emissive: 0x0b331b }));
            lampShade.position.set(0.3, 1.65, -1.2);
            deskGroup.add(lampStand, lampShade);

            roomGroup.add(deskGroup);
            wallBoxes.push(new THREE.Box3().setFromCenterAndSize(
                new THREE.Vector3(-4.8, 0.6, zCenter - 1.5),
                new THREE.Vector3(1.8, 1.3, 5.4)
            ));

            // 2. Sofás de terciopelo rojo a la derecha
            const matSofa = new THREE.MeshStandardMaterial({ color: 0x5c1118, roughness: 0.7 });
            [-2.5, 2.2].forEach((offsetZ) => {
                const sofa = new THREE.Group();
                sofa.position.set(4.8, 0, zCenter + offsetZ);
                const seat = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.45, 2.6), matSofa);
                seat.position.y = 0.25;
                const back = new THREE.Mesh(new THREE.BoxGeometry(0.35, 1.05, 2.6), matSofa);
                back.position.set(0.55, 0.55, 0);
                sofa.add(seat, back);
                roomGroup.add(sofa);
                wallBoxes.push(new THREE.Box3().setFromCenterAndSize(
                    new THREE.Vector3(4.8, 0.5, zCenter + offsetZ),
                    new THREE.Vector3(1.5, 1.1, 2.7)
                ));
            });

            // 3. Cuadros con marcos dorados en las paredes del vestíbulo
            const texCuadro0 = crearTexturaCuadro(0);
            const texCuadro1 = crearTexturaCuadro(1);
            const cuadrosConfig = [
                { x: -ROOM_WIDTH / 2 + 0.24, y: 2.7, z: zCenter - 2.0, rotY: Math.PI / 2, tex: texCuadro0 },
                { x: -ROOM_WIDTH / 2 + 0.24, y: 2.7, z: zCenter + 2.5, rotY: Math.PI / 2, tex: texCuadro1 },
                { x: ROOM_WIDTH / 2 - 0.24, y: 2.7, z: zCenter - 2.5, rotY: -Math.PI / 2, tex: texCuadro1 },
                { x: ROOM_WIDTH / 2 - 0.24, y: 2.7, z: zCenter + 2.2, rotY: -Math.PI / 2, tex: texCuadro0 }
            ];

            cuadrosConfig.forEach((c) => {
                const frameGroup = new THREE.Group();
                frameGroup.position.set(c.x, c.y, c.z);
                frameGroup.rotation.y = c.rotY;
                const border = new THREE.Mesh(new THREE.BoxGeometry(1.7, 2.1, 0.08), matOro);
                const canvasMesh = new THREE.Mesh(new THREE.PlaneGeometry(1.48, 1.88), new THREE.MeshBasicMaterial({ map: c.tex }));
                canvasMesh.position.z = 0.045;
                frameGroup.add(border, canvasMesh);
                roomGroup.add(frameGroup);
            });

            // 4. Columnas arquitectónicas en las esquinas
            [[-6.3, -8.2], [6.3, -8.2], [-6.3, 8.2], [6.3, 8.2]].forEach(([cx, cz]) => {
                const col = new THREE.Mesh(new THREE.BoxGeometry(0.65, ROOM_HEIGHT, 0.65), matMadera);
                col.position.set(cx, ROOM_HEIGHT / 2, zCenter + cz);
                roomGroup.add(col);
            });
        }

        function generarHabitacion(index) {
            const zCenter = -index * ROOM_LENGTH;
            const zFrontWall = zCenter - ROOM_LENGTH / 2;
            const zBackWall = zCenter + ROOM_LENGTH / 2;

            const roomGroup = new THREE.Group();
            const wallBoxes = [];
            const drawers = [];
            const closets = [];
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

            // Paredes laterales
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
                decorarVestibulo(roomGroup, wallBoxes, zCenter);
            } else {
                // En habitaciones normales: Ventanas nocturnas con luna llena y lluvia
                const winSide = (index % 2 === 0) ? 1 : -1;
                const winX = winSide * (ROOM_WIDTH / 2 - 0.22);
                const winRot = (winSide === 1) ? (-Math.PI / 2) : (Math.PI / 2);
                roomGroup.add(crearVentanaNocheLluvia(winX, 2.7, zCenter + 1.2, winRot));
            }

            // Pared frontal con hueco de puerta
            const sideWallW = (ROOM_WIDTH - DOOR_WIDTH) / 2;
            const frontLeft = new THREE.Mesh(new THREE.BoxGeometry(sideWallW, ROOM_HEIGHT, 0.4), matPared);
            frontLeft.position.set(-(DOOR_WIDTH / 2 + sideWallW / 2), ROOM_HEIGHT / 2, zFrontWall);
            roomGroup.add(frontLeft);
            wallBoxes.push(new THREE.Box3().setFromObject(frontLeft));

            const frontRight = new THREE.Mesh(new THREE.BoxGeometry(sideWallW, ROOM_HEIGHT, 0.4), matPared);
            frontRight.position.set(DOOR_WIDTH / 2 + sideWallW / 2, ROOM_HEIGHT / 2, zFrontWall);
            roomGroup.add(frontRight);
            wallBoxes.push(new THREE.Box3().setFromObject(frontRight));

            const frontTop = new THREE.Mesh(new THREE.BoxGeometry(DOOR_WIDTH, ROOM_HEIGHT - DOOR_HEIGHT, 0.4), matPared);
            frontTop.position.set(0, DOOR_HEIGHT + (ROOM_HEIGHT - DOOR_HEIGHT) / 2, zFrontWall);
            roomGroup.add(frontTop);

            // --- PUERTA CON BISAGRA REAL, CARTEL DE MADERA DOORS Y CANDADO VIEJO ---
            const doorPivot = new THREE.Group();
            doorPivot.position.set(-DOOR_WIDTH / 2, 0, zFrontWall);

            const doorMesh = new THREE.Mesh(new THREE.BoxGeometry(DOOR_WIDTH, DOOR_HEIGHT, 0.16), matMadera);
            doorMesh.position.set(DOOR_WIDTH / 2, DOOR_HEIGHT / 2, 0);
            doorPivot.add(doorMesh);

            const doorKnob = new THREE.Mesh(new THREE.SphereGeometry(0.08, 12, 12), matOro);
            doorKnob.position.set(DOOR_WIDTH - 0.25, 1.45, 0.12);
            doorPivot.add(doorKnob);

            // Placa numerada de MADERA estilo DOORS (no amarilla)
            const signMesh = new THREE.Mesh(
                new THREE.PlaneGeometry(1.15, 0.42),
                new THREE.MeshBasicMaterial({ map: crearCartelMaderaDoors(index + 1) })
            );
            signMesh.position.set(0, DOOR_HEIGHT + 0.42, zFrontWall + 0.22);
            roomGroup.add(signMesh);

            // Algunas puertas tienen candado viejo real
            const isLocked = index >= 2 && Math.random() < 0.28;
            let padlockMesh = null;
            if (isLocked) {
                padlockMesh = crearCandadoViejo();
                padlockMesh.position.set(DOOR_WIDTH - 0.25, 1.24, 0.15);
                doorPivot.add(padlockMesh);
            }

            roomGroup.add(doorPivot);

            const doorBox = new THREE.Box3(
                new THREE.Vector3(-DOOR_WIDTH / 2 - 0.1, 0, zFrontWall - 0.3),
                new THREE.Vector3(DOOR_WIDTH / 2 + 0.1, DOOR_HEIGHT, zFrontWall + 0.3)
            );

            // --- ILUMINACIÓN DE LA HABITACIÓN ---
            let lit = true;
            if (index > 5) {
                lit = (index % 15 === 0) ? (Math.random() < 0.25) : (Math.random() < 0.65);
            }
            if (lit) {
                const intensity = index === 0 ? 2.5 : 1.9;
                const roomLight = new THREE.PointLight(0xffdfa8, intensity, 25);
                roomLight.position.set(0, ROOM_HEIGHT - 0.4, zCenter);
                roomGroup.add(roomLight);
                lights.push(roomLight);
            }

            // --- CÓMODA CON CAJÓN HUECO REAL Y OBJETO ULTRA DETALLADO DENTRO ---
            const side = (index % 2 === 0) ? -1 : 1;
            const tableX = side * (ROOM_WIDTH / 2 - 0.85);
            const tableZ = zCenter - 2.2;

            const deskGroup = new THREE.Group();
            deskGroup.position.set(tableX, 0, tableZ);
            deskGroup.rotation.y = (side === -1) ? (Math.PI / 2) : (-Math.PI / 2);

            // Estructura de la cómoda con hueco superior para el cajón
            const baseBody = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.58, 0.85), matMadera);
            baseBody.position.y = 0.29;
            const topBoard = new THREE.Mesh(new THREE.BoxGeometry(1.86, 0.08, 0.9), matMadera);
            topBoard.position.y = 0.96;
            const sideL = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.36, 0.85), matMadera);
            sideL.position.set(-0.83, 0.76, 0);
            const sideR = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.36, 0.85), matMadera);
            sideR.position.set(0.83, 0.76, 0);
            deskGroup.add(baseBody, topBoard, sideL, sideR);

            // Cajón hueco real (4 paredes + fondo oscuro + perilla)
            const drawerGroup = new THREE.Group();
            drawerGroup.position.set(0, 0.75, 0.04);

            const matInteriorOscuro = new THREE.MeshStandardMaterial({ color: 0x160903, roughness: 0.9 });
            const dBottom = new THREE.Mesh(new THREE.BoxGeometry(1.48, 0.04, 0.74), matInteriorOscuro);
            dBottom.position.y = -0.12;
            const dFront = new THREE.Mesh(new THREE.BoxGeometry(1.52, 0.28, 0.05), matMadera);
            dFront.position.z = 0.36;
            const dBack = new THREE.Mesh(new THREE.BoxGeometry(1.48, 0.24, 0.04), matInteriorOscuro);
            dBack.position.z = -0.35;
            const dWallL = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.24, 0.72), matInteriorOscuro);
            dWallL.position.x = -0.72;
            const dWallR = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.24, 0.72), matInteriorOscuro);
            dWallR.position.x = 0.72;
            drawerGroup.add(dBottom, dFront, dBack, dWallL, dWallR);

            const drawerKnob = new THREE.Mesh(new THREE.SphereGeometry(0.06, 12, 12), matOro);
            drawerKnob.position.set(0, 0, 0.41);
            drawerGroup.add(drawerKnob);

            // Objeto ultra detallado dentro del hueco del cajón (Ganzúa o Batería)
            const lootRoll = Math.random();
            let lootType = null;
            let lootMesh = null;
            if (lootRoll < 0.72) {
                lootMesh = new THREE.Group();
                lootMesh.position.set(0, -0.05, 0.08);
                if (lootRoll < 0.40) {
                    // Ganzúa ultra detallada (anillo + vástago + dientes de acero)
                    lootType = 'lockpick';
                    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.06, 0.014, 8, 16), matOro);
                    ring.rotation.x = Math.PI / 2;
                    ring.position.x = -0.12;
                    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.24, 10), matOro);
                    shaft.rotation.z = Math.PI / 2;
                    shaft.position.x = 0.04;
                    const tooth = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.015, 0.04), matOro);
                    tooth.position.set(0.14, 0, 0.025);
                    lootMesh.add(ring, shaft, tooth);
                } else {
                    // Batería/Pila ultra detallada (cuerpo azul/negro + polo cobrizo)
                    lootType = 'battery';
                    const batBody = new THREE.Mesh(
                        new THREE.CylinderGeometry(0.042, 0.042, 0.16, 16),
                        new THREE.MeshStandardMaterial({ color: 0x114488, metalness: 0.6, roughness: 0.3 })
                    );
                    batBody.rotation.z = Math.PI / 2;
                    const batCap = new THREE.Mesh(
                        new THREE.CylinderGeometry(0.042, 0.042, 0.04, 16),
                        new THREE.MeshStandardMaterial({ color: 0xd97724, metalness: 0.85, roughness: 0.2 })
                    );
                    batCap.rotation.z = Math.PI / 2;
                    batCap.position.x = 0.09;
                    lootMesh.add(batBody, batCap);
                }
                drawerGroup.add(lootMesh);
            }

            deskGroup.add(drawerGroup);
            roomGroup.add(deskGroup);

            const deskCollider = new THREE.Box3().setFromCenterAndSize(
                new THREE.Vector3(tableX, 0.5, tableZ),
                new THREE.Vector3(1.05, 1.1, 1.9)
            );
            wallBoxes.push(deskCollider);

            drawers.push({
                group: drawerGroup,
                worldPos: new THREE.Vector3(tableX, 0.75, tableZ),
                open: false,
                targetZ: 0.04,
                lootType: lootType,
                lootTaken: false,
                lootMesh: lootMesh
            });

            // --- ARMARIO PARA ESCONDERSE DE LA IA DEL MONSTRUO ---
            const closetX = -side * (ROOM_WIDTH / 2 - 0.85);
            const closetZ = zCenter + 2.8;
            const closetMesh = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.9, 1.8), matMadera);
            closetMesh.position.set(closetX, 1.45, closetZ);
            roomGroup.add(closetMesh);
            wallBoxes.push(new THREE.Box3().setFromObject(closetMesh));

            closets.push({
                worldPos: new THREE.Vector3(closetX, 1.5, closetZ),
                hidePos: new THREE.Vector3(closetX - side * 0.2, 1.75, closetZ),
                lookYaw: (side === 1) ? (-Math.PI / 2) : (Math.PI / 2)
            });

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
                padlockMesh: padlockMesh,
                wallBoxes: wallBoxes,
                drawers: drawers,
                closets: closets,
                lights: lights
            });

            if (index > highestRoomGenerated) highestRoomGenerated = index;
        }

        // --- IA DEL MONSTRUO (RUSH) ---
        function crearMonstruoIA() {
            monsterMesh = new THREE.Group();
            const core = new THREE.Mesh(
                new THREE.SphereGeometry(1.1, 16, 16),
                new THREE.MeshBasicMaterial({ color: 0x050508 })
            );
            const aura = new THREE.Mesh(
                new THREE.SphereGeometry(1.45, 16, 16),
                new THREE.MeshBasicMaterial({ color: 0x1a0508, transparent: true, opacity: 0.55 })
            );
            const eyeMat = new THREE.MeshBasicMaterial({ color: 0xff2244 });
            const eyeL = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 10), eyeMat);
            eyeL.position.set(-0.38, 0.25, 0.98);
            const eyeR = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 10), eyeMat);
            eyeR.position.set(0.38, 0.25, 0.98);

            const mLight = new THREE.PointLight(0xff1133, 3.5, 18);
            monsterMesh.add(core, aura, eyeL, eyeR, mLight);
            monsterMesh.visible = false;
            scene3D.add(monsterMesh);
        }

        function activarAtaqueMonstruo() {
            if (monsterActive || monsterWarningTimer > 0) return;
            monsterWarningTimer = 3.2; // 3.2 segundos de aviso parpadeando luces
            playAudio('monster');
            actualizarHUD("⚠️ ¡LAS LUCES PARPADEAN! ¡ESCÓNDETE EN UN ARMARIO!");
        }

        function actualizarIAMonstruo(dt) {
            if (elevatorPhase) return;

            // Temporizador para invocar al monstruo cuando ya pasaste la puerta 2
            if (!monsterActive && monsterWarningTimer <= 0 && currentRoomIndex >= 2) {
                monsterCooldown -= dt;
                if (monsterCooldown <= 0) {
                    monsterCooldown = 22 + Math.random() * 14;
                    activarAtaqueMonstruo();
                }
            }

            // Fase 1: Aviso con parpadeo violento de luces
            if (monsterWarningTimer > 0) {
                monsterWarningTimer -= dt;
                const flicker = Math.random() > 0.45;
                for (const r of roomsData) {
                    for (const l of r.lights) l.visible = flicker;
                }
                if (flashlightOn) flashlight.visible = flicker;

                if (monsterWarningTimer <= 0) {
                    // Lanza al monstruo desde atrás hacia adelante
                    for (const r of roomsData) {
                        for (const l of r.lights) l.visible = true;
                    }
                    if (flashlightOn) flashlight.visible = true;

                    monsterActive = true;
                    monsterZ = playerPos.z + 32;
                    monsterMesh.position.set(0, 1.8, monsterZ);
                    monsterMesh.visible = true;
                }
            }

            // Fase 2: El monstruo cruza las salas a toda velocidad
            if (monsterActive) {
                monsterZ -= 26 * dt;
                monsterMesh.position.z = monsterZ;
                monsterMesh.position.x = Math.sin(monsterZ * 0.8) * 1.2;

                // Comprobar si atrapa al jugador (si NO está escondido en un armario)
                if (!isHiding && Math.abs(monsterZ - playerPos.z) < 2.2) {
                    monsterActive = false;
                    monsterMesh.visible = false;
                    playAudio('error');
                    // Reinicio al vestíbulo
                    playerPos.set(0, 1.75, 2.0);
                    yaw = 0;
                    actualizarHUD("💀 Te atrapó el monstruo. Volviste a la Lobby.");
                    return;
                }

                // Cuando ya pasó lejos por delante, desaparece
                if (monsterZ < playerPos.z - 45) {
                    monsterActive = false;
                    monsterMesh.visible = false;
                    actualizarHUD("El monstruo se alejó... Puedes salir.");
                }
            }
        }

        // RANGO DE PRODUCCIÓN Y LIMPIEZA DE MEMORIA (5 PUERTAS)
        function gestionarRangoProduccion() {
            const calcRoom = Math.max(0, Math.floor((-playerPos.z + ROOM_LENGTH / 2) / ROOM_LENGTH));
            if (calcRoom !== currentRoomIndex) {
                currentRoomIndex = calcRoom;
                actualizarHUD();
            }

            while (highestRoomGenerated < currentRoomIndex + MAX_ACTIVE_ROOMS) {
                generarHabitacion(highestRoomGenerated + 1);
            }

            while (roomsData.length > 0 && roomsData[0].index <= currentRoomIndex - MAX_ACTIVE_ROOMS) {
                const oldRoom = roomsData.shift();
                scene3D.remove(oldRoom.group);
                oldRoom.group.traverse((obj) => {
                    if (obj.geometry) obj.geometry.dispose();
                });
            }
        }

        function checkCollision(nextPos) {
            const playerRadius = 0.42;
            const playerSphere = new THREE.Sphere(new THREE.Vector3(nextPos.x, 1.0, nextPos.z), playerRadius);

            for (const room of roomsData) {
                for (const box of room.wallBoxes) {
                    if (box.intersectsSphere(playerSphere)) return true;
                }
                if (!room.doorOpen && room.doorBox.intersectsSphere(playerSphere)) {
                    return true;
                }
            }
            return false;
        }

        function interactuar() {
            if (elevatorPhase) return;

            // Salir del armario si ya está escondido
            if (isHiding) {
                isHiding = false;
                playerPos.copy(savedPosBeforeHide);
                playAudio('creak');
                actualizarHUD("Saliste del armario");
                return;
            }

            for (const room of roomsData) {
                // 1. Esconderse en un armario
                for (const c of room.closets) {
                    if (playerPos.distanceTo(c.worldPos) < 2.8) {
                        isHiding = true;
                        savedPosBeforeHide.copy(playerPos);
                        playerPos.copy(c.hidePos);
                        yaw = c.lookYaw;
                        playAudio('creak');
                        actualizarHUD("Escondido en el armario ([E / Clic] para salir)");
                        return;
                    }
                }

                // 2. Abrir puerta (con candado viejo si está cerrada)
                const doorCenter = new THREE.Vector3(0, 1.6, room.zFrontWall);
                if (!room.doorOpen && playerPos.distanceTo(doorCenter) < 3.0) {
                    if (room.locked) {
                        if (lockpicks > 0) {
                            lockpicks--;
                            room.locked = false;
                            if (room.padlockMesh) room.padlockMesh.visible = false;
                            playAudio('unlock');
                            actualizarHUD("Candado abierto con ganzúa");
                        } else {
                            actualizarHUD("Puerta con candado viejo (Busca una ganzúa en los cajones)");
                            return;
                        }
                    }
                    room.doorOpen = true;
                    room.doorTargetRot = -Math.PI * 0.48;
                    playAudio('creak');
                    actualizarHUD(`Puerta ${String(room.index + 1).padStart(4, '0')} abierta`);
                    return;
                }

                // 3. Abrir cajón hueco y recoger objeto dentro
                for (const d of room.drawers) {
                    if (playerPos.distanceTo(d.worldPos) < 2.8) {
                        if (!d.open) {
                            d.open = true;
                            d.targetZ = 0.50;
                            playAudio('drawer');
                        } else if (d.lootType && !d.lootTaken) {
                            d.lootTaken = true;
                            if (d.lootMesh) d.lootMesh.visible = false;
                            playAudio('pickup');
                            if (d.lootType === 'lockpick') {
                                lockpicks++;
                                actualizarHUD("¡Recogiste una Ganzúa!");
                            } else if (d.lootType === 'battery') {
                                battery = Math.min(100, battery + 45);
                                actualizarHUD("¡Recogiste una Batería (+45%)!");
                            }
                        } else {
                            d.open = false;
                            d.targetZ = 0.04;
                            playAudio('drawer');
                        }
                        return;
                    }
                }
            }
        }

        function actualizarHUD(statusMsg) {
            document.getElementById("hudRoom").innerText = `STANZA: ${String(currentRoomIndex).padStart(4, '0')}`;
            document.getElementById("hudInv").innerText = `🔑 Grimaldelli: ${lockpicks} | 🔋 Batteria: ${Math.ceil(battery)}% | 🔦 Torcia: ${flashlightOn ? 'ON' : 'OFF'}`;
            if (statusMsg) {
                document.getElementById("hudStatus").innerText = statusMsg;
            }
        }

        function updateDoors3D(dt) {
            // Animar lluvia en las ventanas nocturnas
            for (const drops of rainSystems) {
                for (const drop of drops) {
                    drop.position.y -= 4.8 * dt;
                    if (drop.position.y < -1.3) drop.position.y = 1.3;
                }
            }

            // 1. Cinemática inicial del ascensor
            if (elevatorPhase) {
                elevatorTimer += dt;
                if (elevatorTimer < 0.9) {
                    actualizarDisplayAscensor("▲ B2");
                } else if (elevatorTimer < 1.8) {
                    actualizarDisplayAscensor("▲ B1");
                } else {
                    actualizarDisplayAscensor("LOBBY");
                }

                camera3D.position.set(
                    playerPos.x + (Math.random() - 0.5) * 0.018,
                    playerPos.y + (Math.random() - 0.5) * 0.018,
                    playerPos.z
                );

                if (elevatorTimer > 2.0) {
                    if (!elevatorDingPlayed) {
                        elevatorDingPlayed = true;
                        playAudio('ding');
                    }
                    if (elevatorDoorLeft.position.x > -1.85) {
                        elevatorDoorLeft.position.x -= 1.3 * dt;
                        elevatorDoorRight.position.x += 1.3 * dt;
                    } else {
                        elevatorPhase = false;
                        actualizarHUD("Benvenuto nella Lobby");
                    }
                }
                return;
            }

            // Consumo suave de batería de la linterna
            if (flashlightOn && battery > 0) {
                battery = Math.max(0, battery - 0.35 * dt);
                flashlight.intensity = 1.2 + (battery / 100) * 1.6;
                if (battery === 0) {
                    flashlightOn = false;
                    flashlight.visible = false;
                }
            }

            // 2. Movimiento con colisión (si no está escondido en armario)
            let isMoving = false;
            if (!isHiding) {
                const speed = 5.2 * dt;
                const forward = new THREE.Vector3(-Math.sin(yaw), 0, -Math.cos(yaw));
                const right = new THREE.Vector3(Math.cos(yaw), 0, -Math.sin(yaw));
                let moveVec = new THREE.Vector3();

                if (keys['KeyW'] || keys['ArrowUp']) moveVec.add(forward);
                if (keys['KeyS'] || keys['ArrowDown']) moveVec.sub(forward);
                if (keys['KeyD'] || keys['ArrowRight']) moveVec.add(right);
                if (keys['KeyA'] || keys['ArrowLeft']) moveVec.sub(right);

                isMoving = moveVec.lengthSq() > 0;
                if (isMoving) {
                    moveVec.normalize().multiplyScalar(speed);
                    const tryX = playerPos.clone().add(new THREE.Vector3(moveVec.x, 0, 0));
                    if (!checkCollision(tryX)) playerPos.x = tryX.x;

                    const tryZ = playerPos.clone().add(new THREE.Vector3(0, 0, moveVec.z));
                    if (!checkCollision(tryZ)) playerPos.z = tryZ.z;

                    walkTimer += dt * 9;
                    stepSoundTimer += dt;
                    if (stepSoundTimer > 0.44) {
                        stepSoundTimer = 0;
                        playAudio('step');
                    }
                } else {
                    walkTimer = 0;
                }
            }

            const bobY = isMoving ? Math.sin(walkTimer * 2) * 0.045 : 0;
            camera3D.position.set(playerPos.x, playerPos.y + bobY, playerPos.z);
            camera3D.rotation.order = 'YXZ';
            camera3D.rotation.y = yaw;
            camera3D.rotation.x = pitch;

            if (leftArmGroup && rightArmGroup) {
                leftArmGroup.visible = !isHiding;
                rightArmGroup.visible = !isHiding;
                leftArmGroup.position.y = -0.29 + (isMoving ? Math.sin(walkTimer) * 0.022 : 0);
                rightArmGroup.position.y = -0.29 + (isMoving ? -Math.sin(walkTimer) * 0.022 : 0);
            }

            // 3. Animación de apertura de puertas, cajones y avisos
            let promptVisible = false;
            const promptEl = document.getElementById("promptText");

            if (isHiding) {
                promptVisible = true;
                promptEl.innerText = "[E / Clic] Esci dall'armadio";
            } else {
                for (const room of roomsData) {
                    if (Math.abs(room.doorPivot.rotation.y - room.doorTargetRot) > 0.005) {
                        room.doorPivot.rotation.y += (room.doorTargetRot - room.doorPivot.rotation.y) * 6 * dt;
                    }

                    const doorCenter = new THREE.Vector3(0, 1.6, room.zFrontWall);
                    if (!room.doorOpen && playerPos.distanceTo(doorCenter) < 3.0) {
                        promptVisible = true;
                        promptEl.innerText = room.locked
                            ? `[E / Clic] Apri Lucchetto Porta ${String(room.index + 1).padStart(4, '0')} (Serve 1 Grimaldello)`
                            : `[E / Clic] Apri Porta ${String(room.index + 1).padStart(4, '0')}`;
                    }

                    for (const d of room.drawers) {
                        d.group.position.z += (d.targetZ - d.group.position.z) * 10 * dt;

                        if (playerPos.distanceTo(d.worldPos) < 2.8) {
                            promptVisible = true;
                            if (!d.open) {
                                promptEl.innerText = "[E / Clic] Apri cassetto";
                            } else if (d.lootType && !d.lootTaken) {
                                promptEl.innerText = d.lootType === 'lockpick'
                                    ? "[E / Clic] Prendi Grimaldello 🔑"
                                    : "[E / Clic] Prendi Batteria 🔋";
                            } else {
                                promptEl.innerText = "[E / Clic] Chiudi cassetto";
                            }
                        }
                    }

                    for (const c of room.closets) {
                        if (playerPos.distanceTo(c.worldPos) < 2.8) {
                            promptVisible = true;
                            promptEl.innerText = "[E / Clic] Nasconditi nell'armadio";
                        }
                    }
                }
            }

            promptEl.style.display = promptVisible ? "block" : "none";

            // 4. Actualizar IA del monstruo y rango de producción
            actualizarIAMonstruo(dt);
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

        window.addEventListener("keydown", (e) => {
            keys[e.code] = true;
            if (!doorsActive) return;

            if (e.code === "KeyF") {
                if (battery > 0) {
                    flashlightOn = !flashlightOn;
                    flashlight.visible = flashlightOn;
                    actualizarHUD();
                }
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
            if (battery > 0) {
                flashlightOn = !flashlightOn;
                flashlight.visible = flashlightOn;
                actualizarHUD();
            }
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
