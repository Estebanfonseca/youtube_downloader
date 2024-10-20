from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import os
from models.clases import Request_mp3_downloader
import urllib.parse
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

router = APIRouter()

TEMP_FOLDER = "./descargas"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Configuración de OAuth2
client_id = "tu_client_id"
client_secret = "tu_client_secret"
redirect_uri = "http://localhost:8000/callback"

def obtener_token():
    # Obtener token de acceso
    creds = None
    if creds is None or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = Credentials(
                token="tu_token",
                refresh_token="tu_refresh_token",
                scopes=["https://www.googleapis.com/auth/youtube.force-ssl"],
            )
    return creds.token

def descargar_mp3(url: str, nombre_archivo: str = None):
    """
    Descarga un archivo MP3 desde YouTube.

    Args:
        url (str): URL del video.
        nombre_archivo (str, optional): Nombre del archivo. Defaults to None.

    Returns:
        str: Ruta del archivo MP3 descargado.
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.netloc != 'www.youtube.com':
            raise HTTPException(status_code=400, detail="URL inválida")

        titulo = ''
        if nombre_archivo is None:
            titulo = f'{TEMP_FOLDER}/%(title)s.%(ext)s'
        else:
            titulo = f'{TEMP_FOLDER}/{nombre_archivo}.%(ext)s'

        token = obtener_token()
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{titulo}',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3',
                'Authorization': f'Bearer {token}',
            },
            'cookies': './cookies.txt',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            mp3_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')

        return mp3_file

    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(status_code=500, detail=f"Error al descargar el audio: {e}")

@router.post('/download_mp3')
def download_audio(request: Request_mp3_downloader):
    """
    Descarga un archivo MP3 desde YouTube.

    Args:
        request (Request_mp3_downloader): Objeto con la URL y nombre del archivo.

    Returns:
        FileResponse: Archivo MP3 descargado.
    """
    url = request.url
    nombre_archivo = request.nombre_archivo

    if not url:
        raise HTTPException(status_code=400, detail="No se proporcionó la URL")

    mp3_file = descargar_mp3(url, nombre_archivo)

    if not mp3_file:
        raise HTTPException(status_code=500, detail="Error al descargar el audio")

    return FileResponse(mp3_file, media_type="audio/mpeg", filename=os.path.basename(mp3_file))

@router.on_event("shutdown")
def cleanup_files():
    """
    Elimina los archivos temporales después de cada ejecución.
    """
    for file in os.listdir(TEMP_FOLDER):
        os.remove(os.path.join(TEMP_FOLDER, file))