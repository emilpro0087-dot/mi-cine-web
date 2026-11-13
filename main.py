import os
import requests
from flask import Flask, render_template_string, Response, request

app = Flask(__name__)

CONTRASEÑA_CORRECTA = "perrofeoxd"

# Enlace directo al archivo .mp4 en Archive.org
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
    <title>Cinema Privato // Cinema & Doors 3D</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🍿</text></svg>">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background-color: #0b0c10;
            color: #ffffff;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Insignia fija v0.0 en la esquina superior izquierda */
        .version-badge {
            position: fixed;
            top: 14px;
            left: 14px;
            z-index: 9999;
            background: rgba(10, 16, 26, 0.88);
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
            padding: 55px 15px 80px;
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
            margin-bottom: 40px;
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
            font-size: clamp(28px, 5vw, 54px);
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
            gap: 24px;
            justify-content: center;
            width: 100%;
        }

        .movie-card {
            background: rgba(20, 22, 30, 0.78);
            backdrop-filter: blur(12px);
            border-radius: 14px;
            overflow: hidden;
            width: 270px;
            max-width: 90vw;
            cursor: pointer;
            border: 1px solid rgba(255, 255, 255, 0.12);
            transition: transform 0.35s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.35s ease, border-color 0.35s ease;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.8);
        }

        .movie-card:hover {
            transform: translateY(-8px) scale(1.02);
            border-color: #e50914;
            box-shadow: 0 20px 45px rgba(229, 9, 20, 0.5);
        }

        .movie-card.game-card:hover {
            border-color: #ff9900;
            box-shadow: 0 20px 45px rgba(255, 153, 0, 0.45);
        }

        .movie-card img {
            width: 100%;
            height: 380px;
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
            flex-wrap: wrap;
            gap: 6px;
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
            font-size: 20px;
            font-weight: bold;
            text-shadow: 2px 2px 4px #000;
        }

        .modal {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 6000;
            background: rgba(0, 0, 0, 0.96);
            justify-content: center;
            align-items: center;
            padding: 10px;
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
            top: 8px;
            right: 14px;
            color: #fff;
            font-size: 32px;
            font-weight: bold;
            cursor: pointer;
            z-index: 60;
            text-shadow: 0 0 8px #000;
            line-height: 1;
        }

        .subtitle-controls {
            position: absolute;
            top: 12px;
            left: 16px;
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
            max-height: 85vh;
            display: block;
            outline: none;
            background: #000;
        }

        /* Estilos del Juego 3D Doors adaptable (PC + Teléfono) */
        #doors3DContainer {
            position: relative;
            width: 100%;
            height: 70vh;
            max-height: 580px;
            min-height: 360px;
            background: #030305;
            cursor: crosshair;
            overflow: hidden;
            touch-action: none;
            user-select: none;
        }

        #doors3DContainer:fullscreen {
            width: 100vw;
            height: 100vh;
            max-height: 100vh;
        }

        #doorsHUD {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 20;
            font-family: monospace;
        }

        .doors-room-counter {
            position: absolute;
            top: 12px;
            left: 14px;
            background: rgba(0, 0, 0, 0.78);
            border: 1px solid #ff9900;
            color: #ffbb33;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: clamp(12px, 2.5vw, 15px);
            font-weight: bold;
            letter-spacing: 1.5px;
        }

        .btn-fullscreen-doors {
            position: absolute;
            top: 12px;
            right: 48px;
            pointer-events: auto;
            background: rgba(0, 0, 0, 0.82);
            border: 1px solid #00f0ff;
            color: #00f0ff;
            padding: 6px 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: clamp(10px, 2vw, 12px);
            font-weight: bold;
            cursor: pointer;
            letter-spacing: 1px;
        }

        .btn-fullscreen-doors:hover {
            background: rgba(0, 240, 255, 0.22);
        }

        .doors-crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 8px;
            height: 8px;
            background: rgba(255, 255, 255, 0.85);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 0 0 6px #fff;
        }

        .doors-prompt {
            position: absolute;
            top: 56%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid #ff9900;
            color: #ffbb33;
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 13px;
            display: none;
            white-space: nowrap;
        }

        #doorsCinematicBanner {
            position: absolute;
            top: 55px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            border-left: 3px solid #ff9900;
            padding: 8px 16px;
            color: #ffdd99;
            font-family: monospace;
            font-size: clamp(11px, 2.3vw, 14px);
            letter-spacing: 1.5px;
            z-index: 25;
            display: none;
            text-transform: uppercase;
            white-space: nowrap;
        }

        /* Controles Táctiles en Pantalla para Móvil / Tablet */
        #mobileTouchControls {
            position: absolute;
            inset: 0;
            pointer-events: none;
            z-index: 28;
            display: none;
        }

        .touch-dpad {
            position: absolute;
            bottom: 18px;
            left: 18px;
            pointer-events: auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 6px;
        }

        .touch-row {
            display: flex;
            gap: 6px;
        }

        .touch-btn {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            background: rgba(20, 25, 38, 0.65);
            border: 1.5px solid rgba(255, 187, 51, 0.55);
            color: #ffdd99;
            font-size: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(4px);
            touch-action: manipulation;
        }

        .touch-btn:active {
            background: rgba(255, 153, 0, 0.45);
            transform: scale(0.94);
        }

        .touch-actions {
            position: absolute;
            bottom: 22px;
            right: 18px;
            pointer-events: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .touch-action-btn {
            width: 58px;
            height: 58px;
            border-radius: 50%;
            background: rgba(15, 20, 32, 0.72);
            border: 2px solid #00f0ff;
            color: #fff;
            font-size: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
        }

        .touch-action-btn.door-btn {
            border-color: #ff9900;
            box-shadow: 0 0 12px rgba(255, 153, 0, 0.35);
        }

        #doorsStartOverlay {
            position: absolute;
            inset: 0;
            background: rgba(5, 5, 8, 0.88);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 35;
            cursor: pointer;
            text-align: center;
            padding: 20px;
        }

        #doorsStartOverlay h2 {
            font-family: monospace;
            font-size: clamp(20px, 4vw, 28px);
            letter-spacing: 3px;
            color: #ff9900;
            margin-bottom: 12px;
            text-shadow: 0 0 15px rgba(255, 153, 0, 0.6);
        }

        #doorsStartOverlay p {
            color: #ccc;
            font-size: clamp(12px, 2.8vw, 14px);
            max-width: 460px;
            line-height: 1.6;
        }

        .game-controls-bar {
            text-align: center;
            padding: 10px;
            background: #0d111a;
            color: #ffbb33;
            font-family: monospace;
            font-size: clamp(11px, 2.2vw, 13px);
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

    <!-- Versión fija en la esquina superior izquierda -->
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
                <h1 class="cinema-title">CINEMA & <em>DOORS 3D</em></h1>
                <div class="title-divider"></div>
                <p class="sub-description">Catalogo selezionato • Streaming Ultra HD & Horror 3D</p>
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

                <!-- Tarjeta 2: Apartado de JUEGO 3D TERROR (DOORS 1ª PERSONA PC + MÓVIL) -->
                <div class="movie-card game-card" onclick="playAudio('open'); abrirJuego3D()">
                    <div style="height: 380px; background: radial-gradient(circle, #2a1808 0%, #050507 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px;">
                        <span style="font-size: 80px; filter: drop-shadow(0 0 20px #ff9900);">🚪</span>
                        <span style="font-family: monospace; font-size: 13px; letter-spacing: 3px; color: #ffbb33;">HORROR 3D • 1ª PERSONA</span>
                    </div>
                    <div class="info">
                        <h3>JUEGO: DOORS 3D</h3>
                        <div class="badges">
                            <span class="badge-pill" style="border-color: #ff9900; color: #ffbb33;">PC & TELÉFONO</span>
                            <span class="badge-pill">ASCENSOR + LOBBY</span>
                            <span>F11 Full</span>
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

    <!-- Modal del Juego 3D Terror (PC + Teléfono Táctil + Cinemática Ascensor + F11) -->
    <div id="gameModal" class="modal">
        <div class="modal-box" style="border-color: #ff9900; max-width: 960px;">
            <span class="modal-close" onclick="cerrarJuego3D()">&times;</span>
            <div id="doors3DContainer">
                <div id="doorsHUD">
                    <div class="doors-room-counter" id="roomCounter">ASCENSOR • B2</div>
                    <button class="btn-fullscreen-doors" onclick="togglePantallaCompletaDoors()">[F11] FULLSCREEN</button>
                    <div class="doors-crosshair"></div>
                    <div class="doors-prompt" id="doorPrompt">[CLIC / 🚪] ABRIR PUERTA</div>
                </div>

                <div id="doorsCinematicBanner">SUBIENDO AL VESTÍBULO DEL HOTEL...</div>

                <!-- Controles táctiles para teléfonos y tablets -->
                <div id="mobileTouchControls">
                    <div class="touch-dpad">
                        <button class="touch-btn" id="btnTouchW">▲</button>
                        <div class="touch-row">
                            <button class="touch-btn" id="btnTouchA">◀</button>
                            <button class="touch-btn" id="btnTouchS">▼</button>
                            <button class="touch-btn" id="btnTouchD">▶</button>
                        </div>
                    </div>
                    <div class="touch-actions">
                        <button class="touch-action-btn" id="btnTouchFlash" onclick="alternarLinterna()">🔦</button>
                        <button class="touch-action-btn door-btn" id="btnTouchDoor" onclick="intentarAbrirPuerta()">🚪</button>
                    </div>
                </div>

                <div id="doorsStartOverlay" onclick="iniciarExperienciaDoors()">
                    <h2>DOORS 3D // EL ASCENSOR</h2>
                    <p>Toca aquí para iniciar la cinemática de subida en primera persona.<br><br>
                    <b>PC:</b> WASD + Ratón + F (Linterna) + F11.<br>
                    <b>Móvil:</b> Cruceta táctil + Deslizar dedo para mirar.</p>
                </div>
            </div>
            <div class="game-controls-bar">
                PC: [WASD] + [RATÓN] + [F] Linterna + [F11] • MÓVIL: Controles táctiles + Deslizar pantalla
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

            } else if (type === 'door_creak') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(95, now);
                osc.frequency.linearRampToValueAtTime(62, now + 0.55);
                gain.gain.setValueAtTime(0.18, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.55);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.55);

            } else if (type === 'elevator_ding') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, now);
                osc.frequency.setValueAtTime(1174.66, now + 0.12);
                gain.gain.setValueAtTime(0.22, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 1.1);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 1.1);
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
                    console.warn("Interazione richiesta dal browser:", err);
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

        // ============================================================
        // MOTOR 3D MULTIPLATAFORMA (PC + TELÉFONO): DOORS 1ª PERSONA
        // ============================================================
        let scene3D, camera3D, renderer3D, flashlight, animFrame3D;
        let doorsActive = false;
        let currentRoomNum = 1;
        let activeDoorPivot = null;
        let activeDoorOpen = false;
        let roomZOffset = 0;

        // Cinemática de Ascensor
        let elevatorGroup, elevDoorLeft, elevDoorRight, elevLight;
        let cinematicState = "WAITING"; // WAITING -> RISING -> OPENING_DOORS -> PLAYABLE
        let cinematicTimer = 0;
        let elevatorStartY = -14;

        // Controles en 1ª persona
        let yaw = 0;
        let pitch = 0;
        const moveKeys = { w: false, a: false, s: false, d: false };
        let flashlightOn = true;

        // Detección de dispositivo táctil
        const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
        let lookTouchId = null;
        let lastTouchX = 0;
        let lastTouchY = 0;

        function crearTexturaPlaca(texto) {
            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 128;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#2b1d0e';
            ctx.fillRect(0, 0, 256, 128);
            ctx.strokeStyle = '#d4af37';
            ctx.lineWidth = 8;
            ctx.strokeRect(8, 8, 240, 112);
            ctx.fillStyle = '#ffd700';
            ctx.font = 'bold 50px monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(texto, 128, 66);
            return new THREE.CanvasTexture(canvas);
        }

        function construirAscensorYVestibulo() {
            // 1. CABINA DEL ASCENSOR (Sube desde Y = -14 hasta Y = 0)
            elevatorGroup = new THREE.Group();
            elevatorGroup.position.set(0, elevatorStartY, 3.2);

            const matMetal = new THREE.MeshStandardMaterial({ color: 0x24262b, metalness: 0.7, roughness: 0.4 });
            const matReja = new THREE.MeshStandardMaterial({ color: 0x3b352a, metalness: 0.8, roughness: 0.3 });

            const elevFloor = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.2, 3.2), matMetal);
            elevFloor.position.set(0, -0.1, 0);
            elevatorGroup.add(elevFloor);

            const elevCeil = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.2, 3.2), matMetal);
            elevCeil.position.set(0, 3.1, 0);
            elevatorGroup.add(elevCeil);

            const elevBack = new THREE.Mesh(new THREE.BoxGeometry(3.2, 3.2, 0.15), matMetal);
            elevBack.position.set(0, 1.5, 1.55);
            elevatorGroup.add(elevBack);

            const elevLeft = new THREE.Mesh(new THREE.BoxGeometry(0.15, 3.2, 3.2), matMetal);
            elevLeft.position.set(-1.55, 1.5, 0);
            elevatorGroup.add(elevLeft);

            const elevRight = new THREE.Mesh(new THREE.BoxGeometry(0.15, 3.2, 3.2), matMetal);
            elevRight.position.set(1.55, 1.5, 0);
            elevatorGroup.add(elevRight);

            elevDoorLeft = new THREE.Mesh(new THREE.BoxGeometry(1.5, 2.9, 0.1), matReja);
            elevDoorLeft.position.set(-0.75, 1.45, -1.5);
            elevatorGroup.add(elevDoorLeft);

            elevDoorRight = new THREE.Mesh(new THREE.BoxGeometry(1.5, 2.9, 0.1), matReja);
            elevDoorRight.position.set(0.75, 1.45, -1.5);
            elevatorGroup.add(elevDoorRight);

            elevLight = new THREE.PointLight(0xffaa33, 1.3, 6);
            elevLight.position.set(0, 2.7, 0);
            elevatorGroup.add(elevLight);

            scene3D.add(elevatorGroup);

            // 2. VESTÍBULO DEL HOTEL (LOBBY)
            const anchoLobby = 12;
            const largoLobby = 16;
            const altoLobby = 4.6;

            const matParedLobby = new THREE.MeshStandardMaterial({ color: 0x361e16, roughness: 0.8 });
            const matAlfombra = new THREE.MeshStandardMaterial({ color: 0x4d1216, roughness: 0.9 });
            const matMadera = new THREE.MeshStandardMaterial({ color: 0x24130a, roughness: 0.6 });

            const sueloLobby = new THREE.Mesh(new THREE.BoxGeometry(anchoLobby, 0.2, largoLobby), matAlfombra);
            sueloLobby.position.set(0, -0.1, -6.4);
            scene3D.add(sueloLobby);

            const techoLobby = new THREE.Mesh(new THREE.BoxGeometry(anchoLobby, 0.2, largoLobby), matMadera);
            techoLobby.position.set(0, altoLobby + 0.1, -6.4);
            scene3D.add(techoLobby);

            const paredLobbyIzq = new THREE.Mesh(new THREE.BoxGeometry(0.3, altoLobby, largoLobby), matParedLobby);
            paredLobbyIzq.position.set(-anchoLobby / 2, altoLobby / 2, -6.4);
            scene3D.add(paredLobbyIzq);

            const paredLobbyDer = new THREE.Mesh(new THREE.BoxGeometry(0.3, altoLobby, largoLobby), matParedLobby);
            paredLobbyDer.position.set(anchoLobby / 2, altoLobby / 2, -6.4);
            scene3D.add(paredLobbyDer);

            const muroAtrasIzq = new THREE.Mesh(new THREE.BoxGeometry(4.4, altoLobby, 0.3), matParedLobby);
            muroAtrasIzq.position.set(-3.8, altoLobby / 2, 1.6);
            scene3D.add(muroAtrasIzq);

            const muroAtrasDer = new THREE.Mesh(new THREE.BoxGeometry(4.4, altoLobby, 0.3), matParedLobby);
            muroAtrasDer.position.set(3.8, altoLobby / 2, 1.6);
            scene3D.add(muroAtrasDer);

            const dintelAscensor = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.5, 0.3), matParedLobby);
            dintelAscensor.position.set(0, 3.85, 1.6);
            scene3D.add(dintelAscensor);

            const mostrador = new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.15, 4.5), matMadera);
            mostrador.position.set(4.2, 0.58, -5.5);
            scene3D.add(mostrador);

            const cartelRecep = new THREE.Mesh(
                new THREE.PlaneGeometry(2.4, 0.55),
                new THREE.MeshBasicMaterial({ map: crearTexturaPlaca("RECEPTION") })
            );
            cartelRecep.position.set(5.8, 2.7, -5.5);
            cartelRecep.rotation.y = -Math.PI / 2;
            scene3D.add(cartelRecep);

            const luzLobby = new THREE.PointLight(0xffbb66, 1.1, 18);
            luzLobby.position.set(0, altoLobby - 0.6, -6.4);
            scene3D.add(luzLobby);

            const zPuerta1 = -14.4;
            const muroFrenteIzq = new THREE.Mesh(new THREE.BoxGeometry(5.15, altoLobby, 0.3), matParedLobby);
            muroFrenteIzq.position.set(-3.42, altoLobby / 2, zPuerta1);
            scene3D.add(muroFrenteIzq);

            const muroFrenteDer = new THREE.Mesh(new THREE.BoxGeometry(5.15, altoLobby, 0.3), matParedLobby);
            muroFrenteDer.position.set(3.42, altoLobby / 2, zPuerta1);
            scene3D.add(muroFrenteDer);

            const dintelFrente = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.8, 0.3), matParedLobby);
            dintelFrente.position.set(0, altoLobby - 0.9, zPuerta1);
            scene3D.add(dintelFrente);

            crearPuertaInteractiva(1, zPuerta1);
        }

        function crearPuertaInteractiva(numHabitacion, zPos) {
            const pivot = new THREE.Group();
            pivot.position.set(-0.85, 0, zPos);

            const matPuerta = new THREE.MeshStandardMaterial({ color: 0x4a2511, roughness: 0.6 });
            const hojaPuerta = new THREE.Mesh(new THREE.BoxGeometry(1.7, 2.8, 0.14), matPuerta);
            hojaPuerta.position.set(0.85, 1.4, 0);
            pivot.add(hojaPuerta);

            const placaMat = new THREE.MeshBasicMaterial({ map: crearTexturaPlaca(String(numHabitacion).padStart(4, '0')) });
            const placa = new THREE.Mesh(new THREE.PlaneGeometry(0.65, 0.32), placaMat);
            placa.position.set(0.85, 2.15, 0.08);
            pivot.add(placa);

            const pomo = new THREE.Mesh(
                new THREE.SphereGeometry(0.08, 12, 12),
                new THREE.MeshStandardMaterial({ color: 0xffd700, metalness: 0.8, roughness: 0.2 })
            );
            pomo.position.set(1.48, 1.3, 0.1);
            pivot.add(pomo);

            scene3D.add(pivot);
            activeDoorPivot = pivot;
            activeDoorOpen = false;
            roomZOffset = zPos;
        }

        function construirPasilloSiguiente(numHabitacion, zStart) {
            const largo = 16;
            const ancho = 6;
            const alto = 4;

            const matPared = new THREE.MeshStandardMaterial({ color: 0x2a1a14, roughness: 0.85 });
            const matSuelo = new THREE.MeshStandardMaterial({ color: 0x1a120d, roughness: 0.9 });
            const matTecho = new THREE.MeshStandardMaterial({ color: 0x120d0a, roughness: 0.95 });

            const suelo = new THREE.Mesh(new THREE.BoxGeometry(ancho, 0.2, largo), matSuelo);
            suelo.position.set(0, -0.1, zStart - largo / 2);
            scene3D.add(suelo);

            const techo = new THREE.Mesh(new THREE.BoxGeometry(ancho, 0.2, largo), matTecho);
            techo.position.set(0, alto + 0.1, zStart - largo / 2);
            scene3D.add(techo);

            const paredIzq = new THREE.Mesh(new THREE.BoxGeometry(0.3, alto, largo), matPared);
            paredIzq.position.set(-ancho / 2, alto / 2, zStart - largo / 2);
            scene3D.add(paredIzq);

            const paredDer = new THREE.Mesh(new THREE.BoxGeometry(0.3, alto, largo), matPared);
            paredDer.position.set(ancho / 2, alto / 2, zStart - largo / 2);
            scene3D.add(paredDer);

            const lamparaLuz = new THREE.PointLight(0xffaa44, 0.65, 12);
            lamparaLuz.position.set(0, alto - 0.5, zStart - largo / 2);
            scene3D.add(lamparaLuz);

            const zPuerta = zStart - largo;
            const muroIzqPuerta = new THREE.Mesh(new THREE.BoxGeometry(2.15, alto, 0.3), matPared);
            muroIzqPuerta.position.set(-1.92, alto / 2, zPuerta);
            scene3D.add(muroIzqPuerta);

            const muroDerPuerta = new THREE.Mesh(new THREE.BoxGeometry(2.15, alto, 0.3), matPared);
            muroDerPuerta.position.set(1.92, alto / 2, zPuerta);
            scene3D.add(muroDerPuerta);

            const dintel = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.2, 0.3), matPared);
            dintel.position.set(0, alto - 0.6, zPuerta);
            scene3D.add(dintel);

            crearPuertaInteractiva(numHabitacion, zPuerta);
        }

        function alternarLinterna() {
            if (!flashlight) return;
            flashlightOn = !flashlightOn;
            flashlight.intensity = flashlightOn ? 2.6 : 0;
            playAudio('type');
        }

        function intentarAbrirPuerta() {
            if (!doorsActive || cinematicState !== "PLAYABLE") return;
            if (activeDoorPivot && !activeDoorOpen) {
                const dist = Math.abs(camera3D.position.z - roomZOffset);
                if (dist < 3.9) {
                    activeDoorOpen = true;
                    playAudio('door_creak');
                    currentRoomNum++;
                    document.getElementById("roomCounter").innerText = "PUERTA " + String(currentRoomNum).padStart(4, '0');
                    construirPasilloSiguiente(currentRoomNum, roomZOffset);
                }
            }
        }

        function abrirJuego3D() {
            const modal = document.getElementById("gameModal");
            const container = document.getElementById("doors3DContainer");
            modal.style.display = "flex";
            doorsActive = true;

            currentRoomNum = 1;
            cinematicState = "WAITING";
            cinematicTimer = 0;
            document.getElementById("roomCounter").innerText = "ASCENSOR • B2";
            document.getElementById("doorsStartOverlay").style.display = "flex";
            document.getElementById("doorsCinematicBanner").style.display = "none";
            document.getElementById("mobileTouchControls").style.display = isTouchDevice ? "block" : "none";

            yaw = 0;
            pitch = 0;
            flashlightOn = true;

            const oldCanvas = container.querySelector("canvas");
            if (oldCanvas) oldCanvas.remove();

            scene3D = new THREE.Scene();
            scene3D.background = new THREE.Color(0x030305);
            scene3D.fog = new THREE.FogExp2(0x030305, 0.055);

            camera3D = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 75);
            camera3D.position.set(0, elevatorStartY + 1.65, 3.2);

            renderer3D = new THREE.WebGLRenderer({ antialias: true });
            renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer3D.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer3D.domElement);

            const amb = new THREE.AmbientLight(0x2a2520, 0.45);
            scene3D.add(amb);

            // LINTERNA MÁS ANCHA Y DE MAYOR ALCANCE (Math.PI / 3.4 de ángulo y 32m de distancia)
            flashlight = new THREE.SpotLight(0xfff5e0, 2.6, 32, Math.PI / 3.4, 0.55, 1.0);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera3D.add(flashlight);
            camera3D.add(flashlight.target);
            scene3D.add(camera3D);

            construirAscensorYVestibulo();

            if (!animFrame3D) {
                bucleDoors3D();
            }
        }

        function iniciarExperienciaDoors() {
            const container = document.getElementById("doors3DContainer");
            document.getElementById("doorsStartOverlay").style.display = "none";

            // En PC bloquea el ratón; en teléfono no es necesario
            if (!isTouchDevice && container.requestPointerLock) {
                container.requestPointerLock();
            }

            if (cinematicState === "WAITING") {
                cinematicState = "RISING";
                document.getElementById("doorsCinematicBanner").style.display = "block";
            }
        }

        function cerrarJuego3D() {
            doorsActive = false;
            document.getElementById("gameModal").style.display = "none";
            if (document.fullscreenElement) {
                document.exitFullscreen().catch(() => {});
            }
            if (document.pointerLockElement) {
                document.exitPointerLock();
            }
            if (animFrame3D) {
                cancelAnimationFrame(animFrame3D);
                animFrame3D = null;
            }
        }

        function togglePantallaCompletaDoors() {
            const container = document.getElementById("doors3DContainer");
            if (!document.fullscreenElement) {
                if (container.requestFullscreen) {
                    container.requestFullscreen().catch(() => {});
                } else if (container.webkitRequestFullscreen) {
                    container.webkitRequestFullscreen();
                }
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen().catch(() => {});
                }
            }
        }

        function ajustarTamano3D() {
            const container = document.getElementById("doors3DContainer");
            if (renderer3D && camera3D && container) {
                const w = container.clientWidth;
                const h = container.clientHeight;
                camera3D.aspect = w / h;
                camera3D.updateProjectionMatrix();
                renderer3D.setSize(w, h);
            }
        }

        document.addEventListener("fullscreenchange", ajustarTamano3D);
        window.addEventListener("resize", ajustarTamano3D);

        document.addEventListener("pointerlockchange", () => {
            if (isTouchDevice) return;
            const container = document.getElementById("doors3DContainer");
            const overlay = document.getElementById("doorsStartOverlay");
            if (document.pointerLockElement === container) {
                overlay.style.display = "none";
            } else if (doorsActive && cinematicState !== "WAITING") {
                overlay.style.display = "flex";
            }
        });

        // Mirada con Ratón en PC
        document.addEventListener("mousemove", (e) => {
            const container = document.getElementById("doors3DContainer");
            if (document.pointerLockElement === container && doorsActive) {
                yaw -= e.movementX * 0.0022;
                pitch -= e.movementY * 0.0022;
                pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
            }
        });

        // Clic izquierdo en PC para abrir puerta
        document.addEventListener("mousedown", (e) => {
            const container = document.getElementById("doors3DContainer");
            if (document.pointerLockElement === container && doorsActive && e.button === 0) {
                intentarAbrirPuerta();
            }
        });

        // Controles Táctiles en Teléfono / Tablet
        function configurarBotonTactil(id, tecla) {
            const btn = document.getElementById(id);
            if (!btn) return;
            btn.addEventListener("touchstart", (e) => {
                e.preventDefault();
                moveKeys[tecla] = true;
            }, { passive: false });
            btn.addEventListener("touchend", (e) => {
                e.preventDefault();
                moveKeys[tecla] = false;
            }, { passive: false });
        }

        window.addEventListener("DOMContentLoaded", () => {
            configurarBotonTactil("btnTouchW", "w");
            configurarBotonTactil("btnTouchA", "a");
            configurarBotonTactil("btnTouchS", "s");
            configurarBotonTactil("btnTouchD", "d");

            const container3D = document.getElementById("doors3DContainer");
            container3D.addEventListener("touchstart", (e) => {
                if (!doorsActive || e.target.closest("button") || e.target.closest("#doorsStartOverlay")) return;
                const touch = e.changedTouches[0];
                if (lookTouchId === null) {
                    lookTouchId = touch.identifier;
                    lastTouchX = touch.clientX;
                    lastTouchY = touch.clientY;
                }
            }, { passive: true });

            container3D.addEventListener("touchmove", (e) => {
                if (!doorsActive || lookTouchId === null) return;
                for (let i = 0; i < e.changedTouches.length; i++) {
                    const touch = e.changedTouches[i];
                    if (touch.identifier === lookTouchId) {
                        const dx = touch.clientX - lastTouchX;
                        const dy = touch.clientY - lastTouchY;
                        lastTouchX = touch.clientX;
                        lastTouchY = touch.clientY;

                        yaw -= dx * 0.0055;
                        pitch -= dy * 0.0055;
                        pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
                        break;
                    }
                }
            }, { passive: true });

            container3D.addEventListener("touchend", (e) => {
                for (let i = 0; i < e.changedTouches.length; i++) {
                    if (e.changedTouches[i].identifier === lookTouchId) {
                        lookTouchId = null;
                        break;
                    }
                }
            }, { passive: true });
        });

        window.addEventListener("keydown", (e) => {
            if (!doorsActive) return;

            if (e.key === "F11") {
                e.preventDefault();
                togglePantallaCompletaDoors();
                return;
            }

            const k = e.key.toLowerCase();
            if (k === 'w') moveKeys.w = true;
            if (k === 'a') moveKeys.a = true;
            if (k === 's') moveKeys.s = true;
            if (k === 'd') moveKeys.d = true;
            if (k === 'f') {
                alternarLinterna();
            }
        });

        window.addEventListener("keyup", (e) => {
            const k = e.key.toLowerCase();
            if (k === 'w') moveKeys.w = false;
            if (k === 'a') moveKeys.a = false;
            if (k === 's') moveKeys.s = false;
            if (k === 'd') moveKeys.d = false;
        });

        function bucleDoors3D() {
            if (!doorsActive) return;

            cinematicTimer += 0.016;

            // --- FASE 1: CINEMÁTICA DE ASCENSOR SUBIENDO ---
            if (cinematicState === "RISING") {
                elevatorGroup.position.y += 0.065;

                const shakeX = Math.sin(cinematicTimer * 45) * 0.012;
                const shakeY = Math.cos(cinematicTimer * 38) * 0.01;
                camera3D.position.set(shakeX, elevatorGroup.position.y + 1.65 + shakeY, 3.2);

                elevLight.intensity = 1.1 + Math.sin(cinematicTimer * 30) * 0.25;

                if (elevatorGroup.position.y < -8) {
                    document.getElementById("roomCounter").innerText = "ASCENSOR • B2";
                } else if (elevatorGroup.position.y < -3) {
                    document.getElementById("roomCounter").innerText = "ASCENSOR • B1";
                } else {
                    document.getElementById("roomCounter").innerText = "ASCENSOR • PB";
                }

                if (elevatorGroup.position.y >= 0) {
                    elevatorGroup.position.y = 0;
                    camera3D.position.set(0, 1.65, 3.2);
                    elevLight.intensity = 1.3;
                    playAudio('elevator_ding');
                    document.getElementById("roomCounter").innerText = "VESTÍBULO • 0001";
                    document.getElementById("doorsCinematicBanner").innerText = "HAS LLEGADO AL VESTÍBULO";
                    cinematicState = "OPENING_DOORS";
                }

            // --- FASE 2: APERTURA DE REJAS DEL ASCENSOR ---
            } else if (cinematicState === "OPENING_DOORS") {
                elevDoorLeft.position.x -= 0.03;
                elevDoorRight.position.x += 0.03;

                if (elevDoorLeft.position.x <= -2.1) {
                    cinematicState = "PLAYABLE";
                    setTimeout(() => {
                        const banner = document.getElementById("doorsCinematicBanner");
                        if (banner) banner.style.display = "none";
                    }, 1800);
                }
            }

            // Rotación en 1ª persona
            camera3D.rotation.order = 'YXZ';
            camera3D.rotation.y = yaw;
            camera3D.rotation.x = pitch;

            // --- FASE 3: MOVIMIENTO POR EL VESTÍBULO Y PASILLOS ---
            if (cinematicState === "PLAYABLE") {
                const speed = 0.09;
                const forwardX = -Math.sin(yaw);
                const forwardZ = -Math.cos(yaw);
                const rightX = Math.cos(yaw);
                const rightZ = -Math.sin(yaw);

                if (moveKeys.w) {
                    camera3D.position.x += forwardX * speed;
                    camera3D.position.z += forwardZ * speed;
                }
                if (moveKeys.s) {
                    camera3D.position.x -= forwardX * speed;
                    camera3D.position.z -= forwardZ * speed;
                }
                if (moveKeys.a) {
                    camera3D.position.x -= rightX * speed;
                    camera3D.position.z -= rightZ * speed;
                }
                if (moveKeys.d) {
                    camera3D.position.x += rightX * speed;
                    camera3D.position.z += rightZ * speed;
                }

                if (camera3D.position.z > -14.4) {
                    camera3D.position.x = Math.max(-5.2, Math.min(5.2, camera3D.position.x));
                    camera3D.position.z = Math.min(4.3, camera3D.position.z);
                } else {
                    camera3D.position.x = Math.max(-2.3, Math.min(2.3, camera3D.position.x));
                }
            }

            // Aviso para abrir puerta
            const promptEl = document.getElementById("doorPrompt");
            if (activeDoorPivot && cinematicState === "PLAYABLE") {
                const dist = Math.abs(camera3D.position.z - roomZOffset);
                if (!activeDoorOpen && dist < 3.9) {
                    promptEl.style.display = "block";
                } else {
                    promptEl.style.display = "none";
                }
            } else {
                promptEl.style.display = "none";
            }

            // Animación suave de apertura de puertas
            scene3D.traverse((obj) => {
                if (obj.type === "Group" && obj !== activeDoorPivot && obj !== elevatorGroup) {
                    if (obj.rotation.y > -Math.PI / 2.1) {
                        obj.rotation.y -= 0.06;
                    }
                }
            });

            renderer3D.render(scene3D, camera3D);
            animFrame3D = requestAnimationFrame(bucleDoors3D);
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
