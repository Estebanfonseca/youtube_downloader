from pydantic import BaseModel 
from typing import Union

# clases para mp3 descargar

class Request_mp3_downloader(BaseModel):
    url:str
    nombre_archivo:Union[str,None] = None
