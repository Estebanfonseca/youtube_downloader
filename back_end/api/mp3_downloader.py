from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import yt_dlp
import os
import shutil
from models.clases import Request_mp3_downloader

router = APIRouter()


TEMP_FOLDER = "./descargas"
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

def descargar_mp3(url:str,nombre_archivo:str = None):
    try:
        titulo = ''
        if nombre_archivo is None:
            titulo = f'{TEMP_FOLDER}/%(title)s.%(ext)s'
        else:
            titulo = f'{TEMP_FOLDER}/{nombre_archivo}.%(ext)s'
            
            
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'{titulo}',  # Guardar con título del video
            'cookies': './cookies.txt'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            mp3_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
        
        return mp3_file
    
    except Exception as e:
        print(f"Error: {e}")
        return None
    
@router.post('/download_mp3')
async def download_audio(request: Request_mp3_downloader):
    url = request.url
    
    if not url:
        raise HTTPException(status_code=400, detail="No se proporcionó la URL")

    mp3_file = descargar_mp3(url,request.nombre_archivo)
    
    
    if not mp3_file:
        raise HTTPException(status_code=500, detail="Error al descargar el audio")

    # Retornar el archivo MP3
    return FileResponse(mp3_file, media_type="audio/mpeg", filename=os.path.basename(mp3_file))

# Limpiar archivos temporales después de cada ejecución (opcional)
@router.on_event("shutdown")
def cleanup_files():
    shutil.rmtree(TEMP_FOLDER)
    os.makedirs(TEMP_FOLDER)
