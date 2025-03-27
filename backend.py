import os
import uvicorn
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store downloads
DOWNLOADS_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.post("/download")
async def download_video(link: str = Form(...)):
    try:
        youtube_dl_options = {
            "format": "bv+ba/best",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
            "postprocessors": [
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"},
                {"key": "FFmpegEmbedSubtitle"},
            ],
        }

        with yt_dlp.YoutubeDL(youtube_dl_options) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp4").replace(".mkv", ".mp4")
            filepath = os.path.join(DOWNLOADS_DIR, filename)

        return {"status": "Download complete", "filename": filename, "filepath": f"/files/{filename}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# Serve downloaded files
@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join(DOWNLOADS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type="video/mp4")
    return {"status": "error", "message": "File not found"}

# Render assigns a dynamic port, so we use it
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    uvicorn.run(app, host="0.0.0.0", port=port)
