import os
from flask import Flask, render_template_string

app = Flask(__name__)

CONTRASEÑA_CORRECTA = "perrofeoxd"

# Reemplaza con el enlace .mp4 directo de tu subida en Archive.org
VIDEO_URL = "https://archive.org/download/deadpool-and-wolverine_202611/Deadpool_and_Wolverine.mp4"

# URL directa y estable del póster oficial
PORTADA_DEADPOOL = "https://image.tmdb.org/t/p/w500/8cdWjvZQUExUUTzyp4t6EDMubfO.jpg"

PAGINA_WEB = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Clasificado // Zona Privada</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Courier New', Courier, monospace; 
            background: radial-gradient(circle at center, #1a0204 0%, #080808 100%); 
            color: #ff3344; 
            text-align: center; 
            padding: 20px; 
            margin: 0; 
            min-height: 100vh;
        }
        .random-box { 
            background: rgba(10, 10, 10, 0.95); 
            border: 2px solid #ff1a2d;
            box-shadow: 0 0 25px rgba(255, 26, 45, 0.35);
            padding: 30px; 
            border-radius: 8px; 
            display: inline-block; 
            max-width: 460px;
            width: 90%;
