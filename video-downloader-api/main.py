from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import uuid
import os
import tempfile

app = FastAPI(title="Video Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DownloadRequest(BaseModel):
    url: str

class BatchDownloadRequest(BaseModel):
    urls: list[str]

def download_video_with_audio(url: str, output_dir: str) -> dict:
    filename = str(uuid.uuid4())
    output_template = os.path.join(output_dir, filename + ".%(ext)s")

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "video")
        thumbnail = info.get("thumbnail", "")
        platform = info.get("extractor", "")

    for f in os.listdir(output_dir):
        if f.startswith(filename):
            return {
                "filepath": os.path.join(output_dir, f),
                "title": title,
                "thumbnail": thumbnail,
                "platform": platform,
            }

    raise Exception("Arquivo não encontrado após download")

@app.get("/")
def root():
    return {"status": "ok", "message": "Video Downloader API is running"}

@app.post("/download")
def download_single(req: DownloadRequest):
    """Baixa um vídeo com áudio e retorna o arquivo MP4"""
    tmp_dir = tempfile.mkdtemp()
    try:
        result = download_video_with_audio(req.url, tmp_dir)
        return FileResponse(
            path=result["filepath"],
            media_type="video/mp4",
            filename=result["title"][:50] + ".mp4",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch-info")
def get_batch_info(req: BatchDownloadRequest):
    """Retorna info dos vídeos"""
    if len(req.urls) > 20:
        raise HTTPException(status_code=400, detail="Máximo de 20 vídeos por vez")

    results = []
    for url in req.urls:
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                results.append({
                    "url": url,
                    "success": True,
                    "original_url": url,
                    "title": info.get("title", "Vídeo"),
                    "thumbnail": info.get("thumbnail", ""),
                    "platform": info.get("extractor", ""),
                })
        except Exception as e:
            results.append({
                "url": url,
                "success": False,
                "error": str(e),
            })

    return {"results": results}
