import os
from flask import Blueprint, Response

subtitulos_bp = Blueprint('subtitulos', __name__)

SUBTITULOS_DEFECTO = """WEBVTT

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

@subtitulos_bp.route('/subtitulos/<pelicula_id>.vtt')
def obtener_subtitulos(pelicula_id):
    # Si subes un archivo como deadpool.vtt, greenland.vtt o dragonball.vtt, lo lee entero
    ruta_archivo = f"{pelicula_id}.vtt"
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
    else:
        contenido = SUBTITULOS_DEFECTO

    return Response(contenido, mimetype="text/vtt")
