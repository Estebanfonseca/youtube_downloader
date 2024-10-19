from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.mp3_downloader import  router as mp3_router


app = FastAPI(title='API downloader youtube',version='1.0.0',description='API para descargar audio de youtube')

app.include_router(mp3_router,tags=['mp3 downloader'])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)

@app.get('/')
def root():
    return {"message": "API downloader youtube is working"}


