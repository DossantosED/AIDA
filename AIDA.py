import subprocess
import re
from time import sleep
import model
from flask import Flask, jsonify, request
from flask_cors import CORS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

preguntas = model.cargar_preguntas_respuestas()

# Reemplaza los valores con los de tu aplicación de Spotify Developer
client_id = "your_client_id_here"
client_secret = "your_client_secret_here"
redirect_uri = "your_redirect_uri_here"

# Configura la autenticación y la instancia de Spotipy
auth_manager = SpotifyOAuth(
    client_id="idclient",
    client_secret="secret",
    redirect_uri="http://127.0.0.1:5500/sp.htm",
    scope="app-remote-control,user-modify-playback-state,user-read-playback-state",
)
sp = spotipy.Spotify(auth_manager=auth_manager)

def actions(aida_response):
    palabras_clave_chrome = ['Abriendo Chrome!']
    palabras_clave_musica = ['Poniendo Música!', 'Abriendo Spotify!']
    regex_Chrome = re.compile('|'.join(re.escape(palabra) for palabra in palabras_clave_chrome))
    regex_Musica = re.compile('|'.join(re.escape(palabra) for palabra in palabras_clave_musica))
    if regex_Chrome.findall(aida_response):
        app_name = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
        subprocess.Popen(app_name)
    elif regex_Musica.findall(aida_response):
        subprocess.Popen('explorer.exe shell:appsFolder\SpotifyAB.SpotifyMusic_zpdnekdrzrea0!Spotify')
        # Reemplaza 'your_spotify_playlist_uri' con el URI de la lista de reproducción que deseas reproducir
        playlist_uri = "https://open.spotify.com/playlist/7xMr6V00WmTLRzQUFVCx0B"

        # Obtiene el ID de la lista de reproducción y comienza a reproducirla
        devices = sp.devices()
        device_id = None
        for device in devices["devices"]:
            if device["is_active"]:
                device_id = device["id"]
                break
        sp.start_playback(device_id=device_id, context_uri=playlist_uri)


app = Flask(__name__)
CORS(app)
# Ruta para obtener la respuesta de AIDA
@app.route('/get_response', methods=['POST'])
def get_response():
    # Obtener el mensaje del usuario desde el cuerpo de la solicitud
    user_input = request.json.get('peticion', '')

    # Obtener la respuesta de AIDA
    aida_response = model.encontrar_respuesta_mas_probable(preguntas, user_input)

    actions(aida_response)
    # Construir la respuesta
    message = {
        "message": aida_response.encode('utf-8')
    }
    response = jsonify(message)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    app.run(debug=True)
