import requests
from flask import Blueprint, Response, request
from config import CATALOGO_PELICULAS

streaming_bp = Blueprint('streaming', __name__)

@streaming_bp.route('/stream-video/<pelicula_id>')
def stream_video(pelicula_id):
    pelicula = CATALOGO_PELICULAS.get(pelicula_id)
    if not pelicula:
        return Response("Película no encontrada", status=404)

    range_header = request.headers.get('Range', None)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    if range_header:
        headers['Range'] = range_header

    try:
        req = requests.get(pelicula["url_video"], headers=headers, stream=True, timeout=15)
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
