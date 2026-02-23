from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import uuid
import os
import threading
import time

app = FastAPI(title="Video Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Armazena o status dos jobs em memória
jobs = {}

class DownloadRequest(BaseModel):
    url: str

class BatchDownloadRequest(BaseModel):
    urls: list[str]

def get_video_info(url: str):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info

@app.get("/")
def root():
    return {"status": "ok", "message": "Video Downloader API is running"}

@app.post("/info")
def video_info(req: DownloadRequest):
    """Retorna informações do vídeo sem baixar"""
    try:
        info = get_video_info(req.url)
        return {
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "platform": info.get("extractor"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/download-link")
def get_download_link(req: DownloadRequest):
    """Retorna o link direto do MP4 sem baixar no servidor"""
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(req.url, download=False)
            
            # Pega o melhor formato MP4
            formats = info.get("formats", [])
            best_url = None
            best_quality = 0
            
            for f in formats:
                if f.get("ext") == "mp4" and f.get("url"):
                    height = f.get("height") or 0
                    if height > best_quality:
                        best_quality = height
                        best_url = f.get("url")
            
            # Fallback para URL direta
            if not best_url:
                best_url = info.get("url")
            
            if not best_url:
                raise HTTPException(status_code=404, detail="Não foi possível obter o link do vídeo")
            
            return {
                "success": True,
                "download_url": best_url,
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "platform": info.get("extractor"),
                "ext": "mp4",
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch-links")
def get_batch_download_links(req: BatchDownloadRequest):
    """Retorna links diretos para múltiplos vídeos"""
    if len(req.urls) > 20:
        raise HTTPException(status_code=400, detail="Máximo de 20 vídeos por vez")
    
    results = []
    for url in req.urls:
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                formats = info.get("formats", [])
                best_url = None
                best_quality = 0
                
                for f in formats:
                    if f.get("ext") == "mp4" and f.get("url"):
                        height = f.get("height") or 0
                        if height > best_quality:
                            best_quality = height
                            best_url = f.get("url")
                
                if not best_url:
                    best_url = info.get("url")
                
                results.append({
                    "url": url,
                    "success": True,
                    "download_url": best_url,
                    "title": info.get("title"),
                    "thumbnail": info.get("thumbnail"),
                    "platform": info.get("extractor"),
                })
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e),
            })
    
    return {"results": results}
