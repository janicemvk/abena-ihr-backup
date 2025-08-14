from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import shutil

app = FastAPI()

# Ensure directories exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)

# Mount static files
app.mount('/static', StaticFiles(directory='static'), name='static')

# Jinja2 templates
templates = Jinja2Templates(directory='templates')

@app.get('/', response_class=HTMLResponse)
def telemedicine(request: Request):
    return templates.TemplateResponse('telemedicine.html', {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join("static/uploads", file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.get("/uploads")
def list_uploads():
    files = os.listdir("static/uploads")
    return {"files": files}

@app.get("/uploads/{filename}")
def get_upload(filename: str):
    file_path = os.path.join("static/uploads", filename)
    return FileResponse(file_path) 