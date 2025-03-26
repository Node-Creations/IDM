from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
from fastapi import Request

app = FastAPI()

# Serve static files (CSS, JS, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Directory to save downloaded videos
DOWNLOAD_DIR = "downloads"

# Create the directory if it doesn't exist
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# Serve the HTML form when the user visits the root URL
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route for downloading the video
@app.get("/download/")
async def download_video(url: str = Query(..., title="Video URL")):
    """Download video from the given URL."""
    try:
        # Options for yt-dlp to download the video
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',  # Save path and filename template
            'format': 'best',  # Download the best format available
        }

        # Download the video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # Extract file name and provide the download link
        filename = os.path.basename(filename)  # Extract file name only, without path

        # HTML content for download button with dark mode styling
        html_content = f"""
        <html>
            <head>
                <title>Download Complete</title>
                <link rel="stylesheet" href="/static/css/style.css">
            </head>
            <body>
                <div class="container">
                    <h1>Download Complete!</h1>
                    <p>Your video has been successfully downloaded!</p>
                    <a href="/download-file/{filename}">
                        <button>Download {filename}</button>
                    </a>
                    <br><br>
                    <a href="/">
                        <button>Download Another Video</button>
                    </a>
                </div>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>Error!</h1><p>{str(e)}</p></body></html>")

# Serve the downloaded file when the user clicks the download button
@app.get("/download-file/{filename}")
async def download_file(filename: str):
    """Serve the downloaded video file to the user."""
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
    return HTMLResponse(content=f"<html><body><h1>File not found!</h1></body></html>")

# Run the app if this script is executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
