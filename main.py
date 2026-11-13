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
            max-width: 1020px;
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

        /* Estilos del Juego 3D Doors Realista (PC + Teléfono) */
        #doors3DContainer {
            position: relative;
            width: 100%;
            height: 74vh;
            max-height: 620px;
            min-height: 380px;
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
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #ff9900;
            color: #ffbb33;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: clamp(12px, 2.5vw, 15px);
            font-weight: bold;
            letter-spacing: 1.5px;
        }

        .doors-inventory-hud {
            position: absolute;
            top: 50px;
            left: 14px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            background: rgba(8, 10, 15, 0.82);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            color: #eee;
        }

        .battery-bar-bg {
            width: 120px;
            height: 8px;
            background: #222;
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid #555;
        }

        #batteryBarFill {
            width: 100%;
            height: 100%;
            background: #00f0ff;
            transition: width 0.2s, background 0.2s;
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
            background: rgba(0, 0, 0, 0.88);
            border: 1px solid #ff9900;
            color: #ffbb33;
            padding: 7px 15px;
            border-radius: 5px;
            font-size: 13px;
            display: none;
            white-space: nowrap;
        }

        #doorsLootNotification {
            position: absolute;
            top: 63%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(10, 25, 15, 0.92);
            border: 1px solid #00ff88;
            color: #00ff88;
            padding: 6px 14px;
            border-radius: 5px;
            font-size: 13px;
            font-weight: bold;
            display: none;
            white-space: nowrap;
        }

        #doorsCinematicBanner {
            position: absolute;
            top: 14px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.85);
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

        #closetVignette {
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at center, transparent 22%, rgba(0, 0, 0, 0.96) 65%);
            pointer-events: none;
            display: none;
            z-index: 18;
        }

        #doorsGameOver {
            position: absolute;
            inset: 0;
            background: rgba(40, 0, 0, 0.92);
            display: none;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 45;
            text-align: center;
            padding: 20px;
            font-family: monospace;
        }

        #doorsGameOver h2 {
            font-size: 32px;
            color: #ff2233;
            letter-spacing: 4px;
            margin-bottom: 12px;
            text-shadow: 0 0 20px #ff0000;
        }

        #doorsGameOver button {
            margin-top: 20px;
            padding: 12px 26px;
            background: #ff2233;
            color: #fff;
            border: none;
            border-radius: 6px;
            font-family: monospace;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }

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
            gap: 10px;
        }

        .touch-action-btn {
            width: 54px;
            height: 54px;
            border-radius: 50%;
            background: rgba(15, 20, 32, 0.78);
            border: 2px solid #00f0ff;
            color: #fff;
            font-size: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
        }

        .touch-action-btn.interact-btn {
            border-color: #00ff88;
            box-shadow: 0 0 12px rgba(0, 255, 136, 0.35);
        }

        .touch-action-btn.door-btn {
            border-color: #ff9900;
            box-shadow: 0 0 12px rgba(255, 153, 0, 0.35);
        }

        #doorsStartOverlay {
            position: absolute;
            inset: 0;
            background: rgba(5, 5, 8, 0.9);
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
            max-width: 480px;
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

                <!-- Tarjeta 2: DOORS 3D REALISTA -->
                <div class="movie-card game-card" onclick="playAudio('open'); abrirJuego3D()">
                    <div style="height: 380px; background: radial-gradient(circle, #301808 0%, #050507 100%); display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px;">
                        <span style="font-size: 80px; filter: drop-shadow(0 0 20px #ff9900);">🚪</span>
                        <span style="font-family: monospace; font-size: 13px; letter-spacing: 3px; color: #ffbb33;">HORROR 3D • REALISTIC</span>
                    </div>
                    <div class="info">
                        <h3>JUEGO: DOORS 3D</h3>
                        <div class="badges">
                            <span class="badge-pill" style="border-color: #ff9900; color: #ffbb33;">1ª PERSONA + MANOS</span>
                            <span class="badge-pill">CAOS & LOOT</span>
                            <span>PC & Móvil</span>
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

    <!-- Modal del Juego 3D Terror Realista -->
    <div id="gameModal" class="modal">
        <div class="modal-box" style="border-color: #ff9900; max-width: 1020px;">
            <span class="modal-close" onclick="cerrarJuego3D()">&times;</span>
            <div id="doors3DContainer">
                <div id="closetVignette"></div>
                <div id="doorsHUD">
                    <div class="doors-room-counter" id="roomCounter">ASCENSOR • B2</div>
                    <div class="doors-inventory-hud">
                        <div id="flashlightLabel">🔦 LINTERNA: POTENTE</div>
                        <div class="battery-bar-bg"><div id="batteryBarFill"></div></div>
                        <div id="lockpickLabel">🗝️ GANZÚAS: 0</div>
                    </div>
                    <button class="btn-fullscreen-doors" onclick="togglePantallaCompletaDoors()">[F11] FULLSCREEN</button>
                    <div class="doors-crosshair"></div>
                    <div class="doors-prompt" id="doorPrompt">[CLIC / 🚪] INTERACTUAR</div>
                    <div id="doorsLootNotification"></div>
                </div>

                <div id="doorsCinematicBanner">SUBIENDO AL VESTÍBULO DEL HOTEL...</div>

                <div id="doorsGameOver">
                    <h2>TE ATRAPÓ LA ENTIDAD DEL CAOS</h2>
                    <p style="color:#ffaaaa;">Cuando los focos parpadeen y tiemble el suelo, escóndete en un armario.</p>
                    <button onclick="abrirJuego3D()">REINTENTAR</button>
                </div>

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
                        <button class="touch-action-btn interact-btn" id="btnTouchInteract" onclick="interactuarCercano()">✋</button>
                        <button class="touch-action-btn door-btn" id="btnTouchDoor" onclick="intentarAbrirPuerta()">🚪</button>
                    </div>
                </div>

                <div id="doorsStartOverlay" onclick="iniciarExperienciaDoors()">
                    <h2>DOORS 3D // EL HOTEL</h2>
                    <p>Abre cajones (<b>[E]</b> o <b>✋</b>) para ver qué hay dentro y decidir si recogerlo.<br>
                    A partir de la habitación 5 las luces serán aleatorias, y cada 15 habrá caos total.<br><br>
                    Cuando venga el monstruo, escóndete en un <b>armario</b>.</p>
                </div>
            </div>
            <div class="game-controls-bar">
                [WASD] Caminar • [E / ✋] Abrir Cajón / Recoger / Armario • [CLIC / 🚪] Puerta • [F] Linterna • [F11] Pantalla Completa
            </div>
        </div>
    </div>

    <script id="embeddedSubtitles" type="text/vtt">{{ subtitulos_raw | safe }}</script>

    <script>
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        let ambientMusicTimer = null;

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
                osc.frequency.setValueAtTime(92, now);
                osc.frequency.linearRampToValueAtTime(58, now + 0.6);
                gain.gain.setValueAtTime(0.2, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.6);

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

            } else if (type === 'drawer_open') {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(185, now);
                osc.frequency.linearRampToValueAtTime(120, now + 0.25);
                gain.gain.setValueAtTime(0.18, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.25);

            } else if (type === 'loot_pickup') {
                [523.25, 659.25, 783.99].forEach((f, i) => {
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(f, now + i * 0.06);
                    gain.gain.setValueAtTime(0.14, now + i * 0.06);
                    gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.06 + 0.2);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start(now + i * 0.06);
                    osc.stop(now + i * 0.06 + 0.2);
                });

            } else if (type === 'monster_roar') {
                // Rugido siniestro de la entidad Rush causando caos
                const osc1 = audioCtx.createOscillator();
                const osc2 = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc1.type = 'sawtooth';
                osc2.type = 'square';
                osc1.frequency.setValueAtTime(52, now);
                osc1.frequency.exponentialRampToValueAtTime(155, now + 1.4);
                osc1.frequency.exponentialRampToValueAtTime(34, now + 3.4);
                osc2.frequency.setValueAtTime(55, now);
                osc2.frequency.exponentialRampToValueAtTime(148, now + 1.4);
                gain.gain.setValueAtTime(0.01, now);
                gain.gain.linearRampToValueAtTime(0.36, now + 1.4);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 3.6);
                osc1.connect(gain);
                osc2.connect(gain);
                gain.connect(audioCtx.destination);
                osc1.start(now);
                osc2.start(now);
                osc1.stop(now + 3.6);
                osc2.stop(now + 3.6);

            } else if (type === 'chaos_crash') {
                // Estruendo de muebles volcándose al pasar el monstruo
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(120, now);
                osc.frequency.exponentialRampToValueAtTime(28, now + 0.35);
                gain.gain.setValueAtTime(0.26, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.35);

            } else if (type === 'footstep') {
                // Sonido de pisada realista en madera/alfombra
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(105, now);
                osc.frequency.exponentialRampToValueAtTime(36, now + 0.085);
                gain.gain.setValueAtTime(0.13, now);
                gain.gain.exponentialRampToValueAtTime(0.001, now + 0.085);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 0.085);
            }
        }

        // Música real descargada en /static/Corredor_Horror.mp3
        const musicaHotelReal = new Audio('/static/Corredor_Horror.mp3');
        musicaHotelReal.loop = true;
        musicaHotelReal.volume = 0.45;

        function iniciarMusicaTerror() {
            musicaHotelReal.currentTime = 0;
            musicaHotelReal.play().catch(err => console.warn("Audio esperando clic:", err));
        }

        function detenerMusicaTerror() {
            musicaHotelReal.pause();
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
        // MOTOR 3D REALISTA: CAJONES INTERACTIVOS, CAOS Y CÁMARA VIVA
        // ============================================================
        let scene3D, camera3D, renderer3D, flashlight, handsGroup, animFrame3D;
        let doorsActive = false;
        let currentRoomNum = 1;
        let activeDoorPivot = null;
        let activeDoorOpen = false;
        let activeDoorLocked = false;
        let roomZOffset = 0;

        let texMaderaReal, texAlfombraReal, texParedHotel;

        // Linterna potente como antes
        let flashlightRange = 28;
        let flashlightType = "POTENTE (28m)";
        let flashlightBattery = 100;
        let lockpicksCount = 0;

        // Objetos interactivos (cajones que muestran contenido y armarios)
        let interactables = [];
        let furnitureGroups = []; // Mesas que el monstruo volcará al causar caos
        let isHidingInCloset = false;
        let savedPosBeforeCloset = { x: 0, z: 0 };

        // Focos del techo y Monstruo del Caos
        let roomLights = []; // { light, baseIntensity, chaoticFlicker }
        let monsterMesh = null;
        let monsterActive = false;
        let monsterWarningTimer = 0;
        let monsterZ = 0;
        let cameraShakeIntensity = 0;

        // Cinemática de Ascensor
        let elevatorGroup, elevDoorLeft, elevDoorRight, elevLight;
        let cinematicState = "WAITING";
        let cinematicTimer = 0;
        let elevatorStartY = -14;

        // Controles en 1ª persona y balanceo natural de cámara/brazos
        let yaw = 0;
        let pitch = 0;
        let walkBobTimer = 0;
        let stepSoundTimer = 0;
        const moveKeys = { w: false, a: false, s: false, d: false };
        let flashlightOn = true;

        const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);
        let lookTouchId = null;
        let lastTouchX = 0;
        let lastTouchY = 0;

        function generarTexturasRealistas() {
            // 1. Madera realista con vetas oscuras marcadas
            const cMadera = document.createElement('canvas');
            cMadera.width = 512;
            cMadera.height = 512;
            const ctxM = cMadera.getContext('2d');
            ctxM.fillStyle = '#472210';
            ctxM.fillRect(0, 0, 512, 512);

            for (let y = 0; y < 512; y += 2) {
                const onda = Math.sin(y * 0.07) * 14;
                ctxM.strokeStyle = y % 6 === 0 ? 'rgba(14, 5, 1, 0.72)' : 'rgba(25, 10, 3, 0.38)';
                ctxM.lineWidth = 1 + Math.random() * 1.6;
                ctxM.beginPath();
                ctxM.moveTo(0, y);
                ctxM.bezierCurveTo(170, y + onda, 340, y - onda, 512, y);
                ctxM.stroke();
            }
            ctxM.fillStyle = 'rgba(10, 3, 0, 0.85)';
            for (let x = 0; x < 512; x += 64) {
                ctxM.fillRect(x, 0, 3, 512);
            }
            texMaderaReal = new THREE.CanvasTexture(cMadera);
            texMaderaReal.wrapS = THREE.RepeatWrapping;
            texMaderaReal.wrapT = THREE.RepeatWrapping;

            // 2. Alfombra roja de hotel
            const cAlf = document.createElement('canvas');
            cAlf.width = 256;
            cAlf.height = 256;
            const ctxA = cAlf.getContext('2d');
            ctxA.fillStyle = '#4a1014';
            ctxA.fillRect(0, 0, 256, 256);
            ctxA.strokeStyle = 'rgba(20, 4, 6, 0.45)';
            for (let i = 0; i < 256; i += 8) {
                ctxA.beginPath(); ctxA.moveTo(i, 0); ctxA.lineTo(i, 256); ctxA.stroke();
                ctxA.beginPath(); ctxA.moveTo(0, i); ctxA.lineTo(256, i); ctxA.stroke();
            }
            texAlfombraReal = new THREE.CanvasTexture(cAlf);
            texAlfombraReal.wrapS = THREE.RepeatWrapping;
            texAlfombraReal.wrapT = THREE.RepeatWrapping;
            texAlfombraReal.repeat.set(4, 8);

            // 3. Pared de hotel con molduras oscuras
            const cPar = document.createElement('canvas');
            cPar.width = 256;
            cPar.height = 256;
            const ctxP = cPar.getContext('2d');
            ctxP.fillStyle = '#331c14';
            ctxP.fillRect(0, 0, 256, 256);
            ctxP.fillStyle = 'rgba(18, 8, 4, 0.4)';
            for (let x = 0; x < 256; x += 32) {
                ctxP.fillRect(x, 0, 12, 256);
            }
            ctxP.fillStyle = '#1c0c05';
            ctxP.fillRect(0, 200, 256, 56);
            texParedHotel = new THREE.CanvasTexture(cPar);
            texParedHotel.wrapS = THREE.RepeatWrapping;
            texParedHotel.wrapT = THREE.RepeatWrapping;
            texParedHotel.repeat.set(4, 1);
        }

        function crearTexturaPlaca(texto, bloqueada = false) {
            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 128;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = bloqueada ? '#3a0a0a' : '#2b1d0e';
            ctx.fillRect(0, 0, 256, 128);
            ctx.strokeStyle = bloqueada ? '#ff3344' : '#d4af37';
            ctx.lineWidth = 8;
            ctx.strokeRect(8, 8, 240, 112);
            ctx.fillStyle = bloqueada ? '#ff5566' : '#ffd700';
            ctx.font = 'bold 46px monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(texto, 128, 66);
            return new THREE.CanvasTexture(canvas);
        }

        function construirManosPrimeraPersona() {
            handsGroup = new THREE.Group();

            const matManga = new THREE.MeshStandardMaterial({ color: 0x1e2229, roughness: 0.8 });
            const matPiel = new THREE.MeshStandardMaterial({ color: 0xd9a78b, roughness: 0.6 });
            const matLinterna = new THREE.MeshStandardMaterial({ color: 0x151518, metalness: 0.85, roughness: 0.25 });

            // Brazo izquierdo
            const brazoIzqGroup = new THREE.Group();
            const brazoIzq = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.11, 0.45), matManga);
            brazoIzq.position.set(-0.34, -0.32, -0.35);
            brazoIzq.rotation.y = -0.15;
            brazoIzqGroup.add(brazoIzq);

            const manoIzq = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.09, 0.14), matPiel);
            manoIzq.position.set(-0.30, -0.31, -0.60);
            brazoIzqGroup.add(manoIzq);
            handsGroup.add(brazoIzqGroup);

            // Brazo derecho sosteniendo la linterna
            const brazoDerGroup = new THREE.Group();
            const brazoDer = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.11, 0.45), matManga);
            brazoDer.position.set(0.34, -0.30, -0.35);
            brazoDer.rotation.y = 0.15;
            brazoDerGroup.add(brazoDer);

            const manoDer = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.09, 0.14), matPiel);
            manoDer.position.set(0.30, -0.29, -0.60);
            brazoDerGroup.add(manoDer);

            const cuerpoLinterna = new THREE.Mesh(new THREE.CylinderGeometry(0.032, 0.038, 0.24, 14), matLinterna);
            cuerpoLinterna.rotation.x = Math.PI / 2;
            cuerpoLinterna.position.set(0.30, -0.26, -0.68);
            brazoDerGroup.add(cuerpoLinterna);

            const lenteLinterna = new THREE.Mesh(
                new THREE.CircleGeometry(0.03, 14),
                new THREE.MeshBasicMaterial({ color: 0xfff8dc })
            );
            lenteLinterna.position.set(0.30, -0.26, -0.805);
            lenteLinterna.rotation.y = Math.PI;
            brazoDerGroup.add(lenteLinterna);

            handsGroup.add(brazoDerGroup);
            handsGroup.userData = { leftArm: brazoIzqGroup, rightArm: brazoDerGroup };

            camera3D.add(handsGroup);
        }

        function crearMuebleConCajon(x, z, rotY, lootTipo, desordenado = false) {
            const matMadera = new THREE.MeshStandardMaterial({
                map: texMaderaReal,
                bumpMap: texMaderaReal,
                bumpScale: 0.04,
                roughness: 0.55
            });
            const matTirador = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.85, roughness: 0.2 });

            const grupoMesa = new THREE.Group();
            grupoMesa.position.set(x, 0, z);
            grupoMesa.rotation.y = rotY + (desordenado ? (Math.random() - 0.5) * 0.7 : 0);
            if (desordenado && Math.random() > 0.5) {
                grupoMesa.rotation.z = 0.25;
            }

            const cuerpo = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.95, 0.8), matMadera);
            cuerpo.position.set(0, 0.475, 0);
            grupoMesa.add(cuerpo);

            // Cajón deslizable con fondo hueco para mostrar el objeto dentro
            const cajon = new THREE.Group();
            cajon.position.set(0, 0.65, 0.22);

            const baseCajon = new THREE.Mesh(new THREE.BoxGeometry(0.92, 0.05, 0.52), matMadera);
            baseCajon.position.set(0, -0.1, 0);
            cajon.add(baseCajon);

            const frenteCajon = new THREE.Mesh(new THREE.BoxGeometry(0.96, 0.28, 0.08), matMadera);
            frenteCajon.position.set(0, 0, 0.24);
            cajon.add(frenteCajon);

            const tirador = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 10), matTirador);
            tirador.position.set(0, 0, 0.30);
            cajon.add(tirador);

            // Crear el objeto 3D visible dentro del cajón (si lootTipo !== 'empty')
            let itemMesh = null;
            if (lootTipo === 'battery') {
                itemMesh = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.05, 0.05, 0.16, 12),
                    new THREE.MeshStandardMaterial({ color: 0x00d8ff, emissive: 0x004466, metalness: 0.6 })
                );
                itemMesh.rotation.z = Math.PI / 2;
                itemMesh.position.set(0, -0.02, 0.05);
                cajon.add(itemMesh);
            } else if (lootTipo === 'lockpick') {
                itemMesh = new THREE.Mesh(
                    new THREE.BoxGeometry(0.04, 0.02, 0.22),
                    new THREE.MeshStandardMaterial({ color: 0xffd700, emissive: 0x554400, metalness: 0.9 })
                );
                itemMesh.rotation.y = 0.4;
                itemMesh.position.set(0, -0.04, 0.05);
                cajon.add(itemMesh);
            } else if (lootTipo === 'super_flashlight') {
                itemMesh = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.045, 0.055, 0.26, 12),
                    new THREE.MeshStandardMaterial({ color: 0xff9900, emissive: 0x552200, metalness: 0.8 })
                );
                itemMesh.rotation.z = Math.PI / 2;
                itemMesh.position.set(0, -0.02, 0.05);
                cajon.add(itemMesh);
            }

            grupoMesa.add(cajon);
            scene3D.add(grupoMesa);
            furnitureGroups.push(grupoMesa);

            interactables.push({
                type: 'drawer',
                mesh: cajon,
                itemMesh: itemMesh,
                x: x,
                z: z,
                opened: false,
                targetZ: 0.22,
                lootTaken: (lootTipo === 'empty'),
                lootType: lootTipo
            });
        }

        function crearArmarioEscondite(x, z, rotY) {
            const matMadera = new THREE.MeshStandardMaterial({
                map: texMaderaReal,
                bumpMap: texMaderaReal,
                bumpScale: 0.05,
                roughness: 0.5
            });

            const armario = new THREE.Group();
            armario.position.set(x, 0, z);
            armario.rotation.y = rotY;

            const trasera = new THREE.Mesh(new THREE.BoxGeometry(1.6, 2.7, 0.15), matMadera);
            trasera.position.set(0, 1.35, -0.5);
            armario.add(trasera);

            const latIzq = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2.7, 1.1), matMadera);
            latIzq.position.set(-0.75, 1.35, 0);
            armario.add(latIzq);

            const latDer = new THREE.Mesh(new THREE.BoxGeometry(0.15, 2.7, 1.1), matMadera);
            latDer.position.set(0.75, 1.35, 0);
            armario.add(latDer);

            const techoArm = new THREE.Mesh(new THREE.BoxGeometry(1.65, 0.15, 1.15), matMadera);
            techoArm.position.set(0, 2.7, 0);
            armario.add(techoArm);

            const puertaIzq = new THREE.Mesh(new THREE.BoxGeometry(0.72, 2.55, 0.1), matMadera);
            puertaIzq.position.set(-0.38, 1.3, 0.52);
            puertaIzq.rotation.y = 0.25;
            armario.add(puertaIzq);

            const puertaDer = new THREE.Mesh(new THREE.BoxGeometry(0.72, 2.55, 0.1), matMadera);
            puertaDer.position.set(0.38, 1.3, 0.52);
            puertaDer.rotation.y = -0.25;
            armario.add(puertaDer);

            scene3D.add(armario);

            interactables.push({
                type: 'closet',
                mesh: armario,
                x: x,
                z: z,
                rotY: rotY
            });
        }

        function construirAscensorYVestibulo() {
            // 1. CABINA DEL ASCENSOR
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

            elevLight = new THREE.PointLight(0xffaa33, 1.5, 8);
            elevLight.position.set(0, 2.7, 0);
            elevatorGroup.add(elevLight);

            scene3D.add(elevatorGroup);

            // 2. VESTÍBULO DEL HOTEL BIEN ILUMINADO
            const anchoLobby = 14;
            const largoLobby = 18;
            const altoLobby = 4.8;

            const matParedLobby = new THREE.MeshStandardMaterial({ map: texParedHotel, bumpMap: texParedHotel, bumpScale: 0.03, roughness: 0.75 });
            const matAlfombra = new THREE.MeshStandardMaterial({ map: texAlfombraReal, bumpMap: texAlfombraReal, bumpScale: 0.02, roughness: 0.85 });
            const matMadera = new THREE.MeshStandardMaterial({ map: texMaderaReal, bumpMap: texMaderaReal, bumpScale: 0.04, roughness: 0.5 });

            const sueloLobby = new THREE.Mesh(new THREE.BoxGeometry(anchoLobby, 0.2, largoLobby), matAlfombra);
            sueloLobby.position.set(0, -0.1, -7.4);
            scene3D.add(sueloLobby);

            const techoLobby = new THREE.Mesh(new THREE.BoxGeometry(anchoLobby, 0.2, largoLobby), matMadera);
            techoLobby.position.set(0, altoLobby + 0.1, -7.4);
            scene3D.add(techoLobby);

            const paredLobbyIzq = new THREE.Mesh(new THREE.BoxGeometry(0.3, altoLobby, largoLobby), matParedLobby);
            paredLobbyIzq.position.set(-anchoLobby / 2, altoLobby / 2, -7.4);
            scene3D.add(paredLobbyIzq);

            const paredLobbyDer = new THREE.Mesh(new THREE.BoxGeometry(0.3, altoLobby, largoLobby), matParedLobby);
            paredLobbyDer.position.set(anchoLobby / 2, altoLobby / 2, -7.4);
            scene3D.add(paredLobbyDer);

            const muroAtrasIzq = new THREE.Mesh(new THREE.BoxGeometry(5.4, altoLobby, 0.3), matParedLobby);
            muroAtrasIzq.position.set(-4.3, altoLobby / 2, 1.6);
            scene3D.add(muroAtrasIzq);

            const muroAtrasDer = new THREE.Mesh(new THREE.BoxGeometry(5.4, altoLobby, 0.3), matParedLobby);
            muroAtrasDer.position.set(4.3, altoLobby / 2, 1.6);
            scene3D.add(muroAtrasDer);

            const dintelAscensor = new THREE.Mesh(new THREE.BoxGeometry(3.2, 1.7, 0.3), matParedLobby);
            dintelAscensor.position.set(0, 3.95, 1.6);
            scene3D.add(dintelAscensor);

            const mostrador = new THREE.Mesh(new THREE.BoxGeometry(1.6, 1.2, 5.2), matMadera);
            mostrador.position.set(5.2, 0.6, -6.5);
            scene3D.add(mostrador);

            const cartelRecep = new THREE.Mesh(
                new THREE.PlaneGeometry(2.6, 0.6),
                new THREE.MeshBasicMaterial({ map: crearTexturaPlaca("RECEPTION") })
            );
            cartelRecep.position.set(6.8, 2.8, -6.5);
            cartelRecep.rotation.y = -Math.PI / 2;
            scene3D.add(cartelRecep);

            crearMuebleConCajon(-5.5, -5.0, Math.PI / 2, "battery", false);
            crearMuebleConCajon(-5.5, -10.0, Math.PI / 2, "lockpick", false);
            crearArmarioEscondite(-6.1, -7.5, Math.PI / 2);

            // Iluminación abundante en el vestíbulo (araña central + dos apliques cálidos)
            const luzLobbyCentro = new THREE.PointLight(0xffcc77, 2.2, 26);
            luzLobbyCentro.position.set(0, altoLobby - 0.5, -7.4);
            scene3D.add(luzLobbyCentro);
            roomLights.push({ light: luzLobbyCentro, baseIntensity: 2.2, chaoticFlicker: false });

            const luzLobbyFrente = new THREE.PointLight(0xffbb66, 1.6, 20);
            luzLobbyFrente.position.set(0, altoLobby - 0.6, -13.5);
            scene3D.add(luzLobbyFrente);
            roomLights.push({ light: luzLobbyFrente, baseIntensity: 1.6, chaoticFlicker: false });

            const luzLobbyRecep = new THREE.PointLight(0xffaa55, 1.5, 18);
            luzLobbyRecep.position.set(4.5, 2.8, -6.5);
            scene3D.add(luzLobbyRecep);
            roomLights.push({ light: luzLobbyRecep, baseIntensity: 1.5, chaoticFlicker: false });

            const zPuerta1 = -16.4;
            const muroFrenteIzq = new THREE.Mesh(new THREE.BoxGeometry(6.15, altoLobby, 0.3), matParedLobby);
            muroFrenteIzq.position.set(-3.92, altoLobby / 2, zPuerta1);
            scene3D.add(muroFrenteIzq);

            const muroFrenteDer = new THREE.Mesh(new THREE.BoxGeometry(6.15, altoLobby, 0.3), matParedLobby);
            muroFrenteDer.position.set(3.92, altoLobby / 2, zPuerta1);
            scene3D.add(muroFrenteDer);

            const dintelFrente = new THREE.Mesh(new THREE.BoxGeometry(1.7, 2.0, 0.3), matParedLobby);
            dintelFrente.position.set(0, altoLobby - 1.0, zPuerta1);
            scene3D.add(dintelFrente);

            crearPuertaInteractiva(1, zPuerta1, false);
        }

        function crearPuertaInteractiva(numHabitacion, zPos, cerradaConLlave) {
            const pivot = new THREE.Group();
            pivot.position.set(-0.85, 0, zPos);

            const matPuerta = new THREE.MeshStandardMaterial({
                map: texMaderaReal,
                bumpMap: texMaderaReal,
                bumpScale: 0.05,
                roughness: 0.5
            });
            const hojaPuerta = new THREE.Mesh(new THREE.BoxGeometry(1.7, 2.8, 0.15), matPuerta);
            hojaPuerta.position.set(0.85, 1.4, 0);
            pivot.add(hojaPuerta);

            const textoPlaca = cerradaConLlave ? "🔒 " + String(numHabitacion).padStart(4, '0') : String(numHabitacion).padStart(4, '0');
            const placaMat = new THREE.MeshBasicMaterial({ map: crearTexturaPlaca(textoPlaca, cerradaConLlave) });
            const placa = new THREE.Mesh(new THREE.PlaneGeometry(0.75, 0.35), placaMat);
            placa.position.set(0.85, 2.15, 0.085);
            pivot.add(placa);

            const pomo = new THREE.Mesh(
                new THREE.SphereGeometry(0.08, 12, 12),
                new THREE.MeshStandardMaterial({ color: 0xffd700, metalness: 0.85, roughness: 0.2 })
            );
            pomo.position.set(1.48, 1.3, 0.1);
            pivot.add(pomo);

            scene3D.add(pivot);
            activeDoorPivot = pivot;
            activeDoorOpen = false;
            activeDoorLocked = cerradaConLlave;
            roomZOffset = zPos;
        }

        function construirHabitacionSiguiente(numHabitacion, zStart) {
            const largo = 20;
            const ancho = 9;
            const alto = 4.4;

            const matPared = new THREE.MeshStandardMaterial({ map: texParedHotel, bumpMap: texParedHotel, bumpScale: 0.03, roughness: 0.8 });
            const matSuelo = new THREE.MeshStandardMaterial({ map: texAlfombraReal, bumpMap: texAlfombraReal, bumpScale: 0.02, roughness: 0.9 });
            const matTecho = new THREE.MeshStandardMaterial({ map: texMaderaReal, roughness: 0.85 });

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

            // --- LÓGICA DE ILUMINACIÓN PROGRESIVA Y CAOS CADA 15 HABITACIONES ---
            const esZonaCaos15 = (numHabitacion >= 15 && (numHabitacion % 15 === 0 || numHabitacion % 15 <= 2));
            let probLuz = 1.0; // Primeras 5 habitaciones siempre encendidas
            if (esZonaCaos15) {
                probLuz = 0.25; // Caos extremo cada 15 habitaciones
            } else if (numHabitacion > 5) {
                probLuz = 0.58; // Después de la 5 habitación es aleatorio
            }

            const luzEncendida = Math.random() < probLuz;
            const intensidadFoco = luzEncendida ? (esZonaCaos15 ? 1.1 : 1.65) : 0.0;

            const focoLuz = new THREE.PointLight(0xffbb66, intensidadFoco, 22);
            focoLuz.position.set(0, alto - 0.5, zStart - largo / 2);
            scene3D.add(focoLuz);
            roomLights.push({
                light: focoLuz,
                baseIntensity: intensidadFoco,
                chaoticFlicker: esZonaCaos15 && luzEncendida
            });

            if (esZonaCaos15) {
                mostrarNotificacionLoot("⚡ ZONA DE CAOS — LUCES INESTABLES", "#ff6600");
            }

            // Armarios para esconderse
            crearArmarioEscondite(-3.6, zStart - 8, Math.PI / 2);
            crearArmarioEscondite(3.6, zStart - 13, -Math.PI / 2);

            // Muebles con cajones y objetos aleatorios
            const opcionesLoot = ["battery", "lockpick", "super_flashlight", "empty"];
            const loot1 = opcionesLoot[Math.floor(Math.random() * opcionesLoot.length)];
            const loot2 = opcionesLoot[Math.floor(Math.random() * opcionesLoot.length)];

            crearMuebleConCajon(-3.6, zStart - 14, Math.PI / 2, loot1, esZonaCaos15);
            crearMuebleConCajon(3.6, zStart - 6, -Math.PI / 2, loot2, esZonaCaos15);

            const siguienteCerrada = (numHabitacion % 4 === 0);

            const zPuerta = zStart - largo;
            const muroIzqPuerta = new THREE.Mesh(new THREE.BoxGeometry(3.65, alto, 0.3), matPared);
            muroIzqPuerta.position.set(-2.67, alto / 2, zPuerta);
            scene3D.add(muroIzqPuerta);

            const muroDerPuerta = new THREE.Mesh(new THREE.BoxGeometry(3.65, alto, 0.3), matPared);
            muroDerPuerta.position.set(2.67, alto / 2, zPuerta);
            scene3D.add(muroDerPuerta);

            const dintel = new THREE.Mesh(new THREE.BoxGeometry(1.7, 1.6, 0.3), matPared);
            dintel.position.set(0, alto - 0.8, zPuerta);
            scene3D.add(dintel);

            crearPuertaInteractiva(numHabitacion, zPuerta, siguienteCerrada);

            // Aparición del Monstruo del Caos (más frecuente en zonas de 15 habitaciones)
            const probMonstruo = esZonaCaos15 ? 0.65 : (numHabitacion > 5 ? 0.35 : 0.2);
            if (numHabitacion >= 3 && Math.random() < probMonstruo && !monsterActive) {
                activarEventoMonstruo(zStart + 20);
            }
        }

        function activarEventoMonstruo(zSpawn) {
            monsterActive = true;
            monsterWarningTimer = 3.2;
            monsterZ = zSpawn;
            playAudio('monster_roar');
            mostrarNotificacionLoot("⚠️ ¡LOS FOCOS PARPADEAN! ¡ESCÓNDETE EN UN ARMARIO!", "#ff3344");

            if (!monsterMesh) {
                const grupoMonstruo = new THREE.Group();
                const sombra = new THREE.Mesh(
                    new THREE.SphereGeometry(1.4, 16, 16),
                    new THREE.MeshBasicMaterial({ color: 0x050505 })
                );
                grupoMonstruo.add(sombra);

                const ojoIzq = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), new THREE.MeshBasicMaterial({ color: 0xff0022 }));
                ojoIzq.position.set(-0.42, 0.2, -1.25);
                grupoMonstruo.add(ojoIzq);

                const ojoDer = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 10), new THREE.MeshBasicMaterial({ color: 0xff0022 }));
                ojoDer.position.set(0.42, 0.2, -1.25);
                grupoMonstruo.add(ojoDer);

                const luzMonstruo = new THREE.PointLight(0xff0022, 4, 15);
                grupoMonstruo.add(luzMonstruo);

                monsterMesh = grupoMonstruo;
                scene3D.add(monsterMesh);
            }
            monsterMesh.position.set(0, 1.8, monsterZ);
            monsterMesh.visible = true;
        }

        function mostrarNotificacionLoot(texto, color = "#00ff88") {
            const el = document.getElementById("doorsLootNotification");
            if (!el) return;
            el.innerText = texto;
            el.style.color = color;
            el.style.borderColor = color;
            el.style.display = "block";
            setTimeout(() => {
                el.style.display = "none";
            }, 2600);
        }

        function actualizarHUDInventario() {
            document.getElementById("flashlightLabel").innerText = `🔦 LINTERNA: ${flashlightType}`;
            document.getElementById("lockpickLabel").innerText = `🗝️ GANZÚAS: ${lockpicksCount}`;
            const bar = document.getElementById("batteryBarFill");
            bar.style.width = Math.max(0, flashlightBattery) + "%";
            bar.style.background = flashlightBattery > 30 ? "#00f0ff" : "#ff3344";
        }

        function alternarLinterna() {
            if (!flashlight) return;
            if (flashlightBattery <= 0) {
                playAudio('error');
                mostrarNotificacionLoot("¡SIN BATERÍA! BUSCA PILAS EN LOS CAJONES", "#ff5566");
                return;
            }
            flashlightOn = !flashlightOn;
            flashlight.intensity = flashlightOn ? 3.0 : 0;
            playAudio('type');
        }

        function interactuarCercano() {
            if (!doorsActive || cinematicState !== "PLAYABLE") return;

            if (isHidingInCloset) {
                isHidingInCloset = false;
                camera3D.position.set(savedPosBeforeCloset.x, 1.65, savedPosBeforeCloset.z);
                document.getElementById("closetVignette").style.display = "none";
                playAudio('drawer_open');
                return;
            }

            let masCercano = null;
            let minDist = 2.7;

            for (const item of interactables) {
                if (item.type === 'drawer' && item.opened && item.lootTaken) continue;
                const dx = camera3D.position.x - item.x;
                const dz = camera3D.position.z - item.z;
                const d = Math.sqrt(dx * dx + dz * dz);
                if (d < minDist) {
                    minDist = d;
                    masCercano = item;
                }
            }

            if (!masCercano) return;

            if (masCercano.type === 'closet') {
                isHidingInCloset = true;
                savedPosBeforeCloset = { x: camera3D.position.x, z: camera3D.position.z };
                camera3D.position.set(masCercano.x, 1.65, masCercano.z);
                document.getElementById("closetVignette").style.display = "block";
                playAudio('drawer_open');
                mostrarNotificacionLoot("ESCONDIDO EN EL ARMARIO (PULSA E / ✋ PARA SALIR)", "#ffbb33");

            } else if (masCercano.type === 'drawer') {
                // Paso 1: Si el cajón está cerrado, deslizarlo suavemente para ver qué tiene
                if (!masCercano.opened) {
                    masCercano.opened = true;
                    masCercano.targetZ = 0.56; // Se desliza suavemente en bucleDoors3D
                    playAudio('drawer_open');
                    if (masCercano.lootType === 'empty') {
                        mostrarNotificacionLoot("EL CAJÓN ESTÁ VACÍO", "#aaaaaa");
                    }
                // Paso 2: Si ya está abierto y tiene un objeto, decidir recogerlo
                } else if (!masCercano.lootTaken && masCercano.itemMesh) {
                    masCercano.lootTaken = true;
                    masCercano.itemMesh.visible = false;
                    playAudio('loot_pickup');

                    if (masCercano.lootType === 'super_flashlight') {
                        flashlightRange = 36;
                        flashlightType = "ULTRA (36m)";
                        flashlightBattery = 100;
                        flashlight.distance = flashlightRange;
                        flashlight.intensity = 3.4;
                        flashlightOn = true;
                        mostrarNotificacionLoot("RECOGIENDO LINTERNA ULTRA POTENTE (36m)");
                    } else if (masCercano.lootType === 'lockpick') {
                        lockpicksCount++;
                        mostrarNotificacionLoot("RECOGIENDO GANZÚA (+1)");
                    } else if (masCercano.lootType === 'battery') {
                        flashlightBattery = Math.min(100, flashlightBattery + 55);
                        mostrarNotificacionLoot("RECOGIENDO PILAS (+55% BATERÍA)");
                    }
                    actualizarHUDInventario();
                }
            }
        }

        function intentarAbrirPuerta() {
            if (!doorsActive || cinematicState !== "PLAYABLE" || isHidingInCloset) return;
            if (activeDoorPivot && !activeDoorOpen) {
                const dist = Math.abs(camera3D.position.z - roomZOffset);
                if (dist < 3.8) {
                    if (activeDoorLocked) {
                        if (lockpicksCount > 0) {
                            lockpicksCount--;
                            activeDoorLocked = false;
                            actualizarHUDInventario();
                            mostrarNotificacionLoot("¡CERRADURA FORZADA CON GANZÚA!", "#00f0ff");
                        } else {
                            playAudio('error');
                            mostrarNotificacionLoot("🔒 PUERTA CERRADA — BUSCA UNA GANZÚA EN LOS CAJONES", "#ff4455");
                            return;
                        }
                    }

                    activeDoorOpen = true;
                    playAudio('door_creak');
                    currentRoomNum++;
                    document.getElementById("roomCounter").innerText = "PUERTA " + String(currentRoomNum).padStart(4, '0');
                    construirHabitacionSiguiente(currentRoomNum, roomZOffset);
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
            interactables = [];
            furnitureGroups = [];
            roomLights = [];
            isHidingInCloset = false;
            monsterActive = false;
            monsterMesh = null;
            cameraShakeIntensity = 0;

            flashlightRange = 28;
            flashlightType = "POTENTE (28m)";
            flashlightBattery = 100;
            lockpicksCount = 0;
            actualizarHUDInventario();

            document.getElementById("roomCounter").innerText = "ASCENSOR • B2";
            document.getElementById("doorsStartOverlay").style.display = "flex";
            document.getElementById("doorsCinematicBanner").style.display = "none";
            document.getElementById("doorsGameOver").style.display = "none";
            document.getElementById("closetVignette").style.display = "none";
            document.getElementById("mobileTouchControls").style.display = isTouchDevice ? "block" : "none";

            yaw = 0;
            pitch = 0;
            flashlightOn = true;

            const oldCanvas = container.querySelector("canvas");
            if (oldCanvas) oldCanvas.remove();

            generarTexturasRealistas();

            scene3D = new THREE.Scene();
            scene3D.background = new THREE.Color(0x020204);
            scene3D.fog = new THREE.FogExp2(0x020204, 0.045);

            camera3D = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 80);
            camera3D.position.set(0, elevatorStartY + 1.65, 3.2);

            renderer3D = new THREE.WebGLRenderer({ antialias: true });
            renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer3D.setSize(container.clientWidth, container.clientHeight);
            container.appendChild(renderer3D.domElement);

            const amb = new THREE.AmbientLight(0x2e2822, 0.55);
            scene3D.add(amb);

            // Linterna potente y ancha desde el comienzo
            flashlight = new THREE.SpotLight(0xfff5e0, 3.0, flashlightRange, Math.PI / 3.3, 0.5, 1.0);
            flashlight.position.set(0, 0, 0);
            flashlight.target.position.set(0, 0, -1);
            camera3D.add(flashlight);
            camera3D.add(flashlight.target);
            scene3D.add(camera3D);

            construirManosPrimeraPersona();
            construirAscensorYVestibulo();
            iniciarMusicaTerror();

            if (!animFrame3D) {
                bucleDoors3D();
            }
        }

        function iniciarExperienciaDoors() {
            const container = document.getElementById("doors3DContainer");
            document.getElementById("doorsStartOverlay").style.display = "none";

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
            detenerMusicaTerror();
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
            } else if (doorsActive && cinematicState !== "WAITING" && document.getElementById("doorsGameOver").style.display !== "flex") {
                overlay.style.display = "flex";
            }
        });

        document.addEventListener("mousemove", (e) => {
            const container = document.getElementById("doors3DContainer");
            if (document.pointerLockElement === container && doorsActive) {
                yaw -= e.movementX * 0.0022;
                pitch -= e.movementY * 0.0022;
                pitch = Math.max(-Math.PI / 2.5, Math.min(Math.PI / 2.5, pitch));
            }
        });

        document.addEventListener("mousedown", (e) => {
            const container = document.getElementById("doors3DContainer");
            if (document.pointerLockElement === container && doorsActive && e.button === 0) {
                intentarAbrirPuerta();
            }
        });

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
            if (k === 'f') alternarLinterna();
            if (k === 'e') interactuarCercano();
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

                elevLight.intensity = 1.2 + Math.sin(cinematicTimer * 30) * 0.25;

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
                    elevLight.intensity = 1.5;
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

            // Rotación en 1ª persona + temblor si pasa el monstruo del caos
            let camShakeX = 0;
            let camShakeY = 0;
            if (cameraShakeIntensity > 0.001) {
                camShakeX = (Math.random() - 0.5) * cameraShakeIntensity;
                camShakeY = (Math.random() - 0.5) * cameraShakeIntensity;
                cameraShakeIntensity *= 0.94;
            }

            camera3D.rotation.order = 'YXZ';
            camera3D.rotation.y = yaw + camShakeX;
            camera3D.rotation.x = pitch + camShakeY;

            // --- FASE 3: JUGABILIDAD EN 1ª PERSONA ---
            if (cinematicState === "PLAYABLE") {
                if (flashlightOn && flashlightBattery > 0) {
                    flashlightBattery -= 0.012;
                    if (flashlightBattery <= 0) {
                        flashlightBattery = 0;
                        flashlightOn = false;
                        flashlight.intensity = 0;
                    }
                    if (Math.random() < 0.08) actualizarHUDInventario();
                }

                let isMoving = false;
                if (!isHidingInCloset) {
                    const speed = 0.095;
                    const forwardX = -Math.sin(yaw);
                    const forwardZ = -Math.cos(yaw);
                    const rightX = Math.cos(yaw);
                    const rightZ = -Math.sin(yaw);

                    if (moveKeys.w) { camera3D.position.x += forwardX * speed; camera3D.position.z += forwardZ * speed; isMoving = true; }
                    if (moveKeys.s) { camera3D.position.x -= forwardX * speed; camera3D.position.z -= forwardZ * speed; isMoving = true; }
                    if (moveKeys.a) { camera3D.position.x -= rightX * speed; camera3D.position.z -= rightZ * speed; isMoving = true; }
                    if (moveKeys.d) { camera3D.position.x += rightX * speed; camera3D.position.z += rightZ * speed; isMoving = true; }

                    if (camera3D.position.z > -16.4) {
                        camera3D.position.x = Math.max(-6.1, Math.min(6.1, camera3D.position.x));
                        camera3D.position.z = Math.min(4.3, camera3D.position.z);
                    } else {
                        camera3D.position.x = Math.max(-3.7, Math.min(3.7, camera3D.position.x));
                    }
                }

                // Efecto natural de cámara y brazos al caminar + pasos sincronizados
                if (isMoving && handsGroup) {
                    walkBobTimer += 0.16;
                    stepSoundTimer += 0.16;

                    // La cámara sube y baja levemente al dar cada paso (Camera Bobbing)
                    camera3D.position.y = 1.65 + Math.abs(Math.sin(walkBobTimer)) * 0.045;

                    // Balanceo alternado de brazo izquierdo y derecho
                    handsGroup.position.y = Math.sin(walkBobTimer * 2) * 0.015;
                    handsGroup.position.x = Math.cos(walkBobTimer) * 0.018;
                    if (handsGroup.userData.leftArm && handsGroup.userData.rightArm) {
                        handsGroup.userData.leftArm.rotation.x = Math.sin(walkBobTimer) * 0.06;
                        handsGroup.userData.rightArm.rotation.x = -Math.sin(walkBobTimer) * 0.04;
                    }

                    if (stepSoundTimer >= Math.PI) {
                        stepSoundTimer = 0;
                        playAudio('footstep');
                    }
                } else {
                    camera3D.position.y += (1.65 - camera3D.position.y) * 0.15;
                    if (handsGroup) {
                        handsGroup.position.y *= 0.85;
                        handsGroup.position.x *= 0.85;
                    }
                }

                // Animación suave de deslizamiento de cajones al abrirse
                for (const item of interactables) {
                    if (item.type === 'drawer' && item.opened) {
                        item.mesh.position.z += (item.targetZ - item.mesh.position.z) * 0.16;
                    }
                }

                // Parpadeo caótico en habitaciones de zona 15
                for (const rl of roomLights) {
                    if (rl.chaoticFlicker && !monsterActive) {
                        rl.light.intensity = Math.random() > 0.25 ? rl.baseIntensity : 0.05;
                    }
                }

                // --- LÓGICA DEL MONSTRUO DEL CAOS ---
                if (monsterActive) {
                    for (const rl of roomLights) {
                        rl.light.intensity = Math.random() > 0.45 ? 1.8 : 0.0;
                    }

                    if (monsterWarningTimer > 0) {
                        monsterWarningTimer -= 0.016;
                        cameraShakeIntensity = 0.015;
                    } else {
                        monsterMesh.position.z -= 0.72;
                        cameraShakeIntensity = 0.065; // Temblor fuerte al pasar

                        // Volcar mesas cercanas a su paso para causar caos real
                        for (const mesa of furnitureGroups) {
                            if (Math.abs(mesa.position.z - monsterMesh.position.z) < 2.2 && !mesa.userData.knocked) {
                                mesa.userData.knocked = true;
                                mesa.rotation.z = (mesa.position.x > 0 ? -1 : 1) * 0.55;
                                mesa.rotation.y += (Math.random() - 0.5) * 0.8;
                                playAudio('chaos_crash');
                            }
                        }

                        if (Math.abs(monsterMesh.position.z - camera3D.position.z) < 1.8) {
                            if (!isHidingInCloset) {
                                doorsActive = false;
                                detenerMusicaTerror();
                                playAudio('error');
                                if (document.pointerLockElement) document.exitPointerLock();
                                document.getElementById("doorsGameOver").style.display = "flex";
                                return;
                            }
                        }

                        if (monsterMesh.position.z < roomZOffset - 25) {
                            monsterActive = false;
                            monsterMesh.visible = false;
                            for (const rl of roomLights) rl.light.intensity = rl.baseIntensity;
                            mostrarNotificacionLoot("EL MONSTRUO SE HA IDO. PUEDES SALIR.", "#00f0ff");
                        }
                    }
                }
            }

            // Prompts contextuales según lo que mires o tengas cerca
            const promptEl = document.getElementById("doorPrompt");
            if (cinematicState === "PLAYABLE") {
                if (isHidingInCloset) {
                    promptEl.innerText = "[E / ✋] SALIR DEL ARMARIO";
                    promptEl.style.display = "block";
                } else {
                    let nearObj = null;
                    for (const item of interactables) {
                        if (item.type === 'drawer' && item.opened && item.lootTaken) continue;
                        const dx = camera3D.position.x - item.x;
                        const dz = camera3D.position.z - item.z;
                        if (Math.sqrt(dx * dx + dz * dz) < 2.7) {
                            nearObj = item;
                            break;
                        }
                    }

                    if (nearObj) {
                        if (nearObj.type === 'closet') {
                            promptEl.innerText = "[E / ✋] ESCONDERSE EN ARMARIO";
                        } else if (!nearObj.opened) {
                            promptEl.innerText = "[E / ✋] ABRIR CAJÓN";
                        } else if (!nearObj.lootTaken) {
                            const nombresLoot = {
                                'battery': 'PILAS',
                                'lockpick': 'GANZÚA',
                                'super_flashlight': 'LINTERNA ULTRA'
                            };
                            promptEl.innerText = `[E / ✋] TOMAR ${nombresLoot[nearObj.lootType] || 'OBJETO'}`;
                        }
                        promptEl.style.display = "block";
                    } else if (activeDoorPivot && !activeDoorOpen && Math.abs(camera3D.position.z - roomZOffset) < 3.8) {
                        promptEl.innerText = activeDoorLocked ? "[CLIC / 🚪] USAR GANZÚA" : "[CLIC / 🚪] ABRIR PUERTA";
                        promptEl.style.display = "block";
                    } else {
                        promptEl.style.display = "none";
                    }
                }
            } else {
                promptEl.style.display = "none";
            }

            // Animación suave de apertura de puertas
            scene3D.traverse((obj) => {
                if (obj.type === "Group" && obj !== activeDoorPivot && obj !== elevatorGroup) {
                    if (obj.rotation.y > -Math.PI / 2.1 && obj.children.length === 4) {
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
