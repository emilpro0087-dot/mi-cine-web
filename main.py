import os
from flask import Flask, render_template
from config import APP_VERSION, CONTRASEÑA_CORRECTA, CATALOGO_PELICULAS
from streaming import streaming_bp
from subtitulos import subtitulos_bp

app = Flask(__name__)
app.register_blueprint(streaming_bp)
app.register_blueprint(subtitulos_bp)

@app.route('/')
def home():
    return render_template(
        'index.html',
        version=APP_VERSION,
        clave=CONTRASEÑA_CORRECTA,
        peliculas=CATALOGO_PELICULAS
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
