from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
import os
import shutil

app = FastAPI()

origins = [
    "http://localhost:3000",  # React/Next.js frontend
    "http://127.0.0.1:3000",  # Alternate localhost
    "*"  # Allow all (not recommended for production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_DIR = "static"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def home():
    return {"message": "Hello from FastAPI!"}

# Store uploaded image URLs
uploaded_images = []

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    filename = f"{uuid4()}_{file.filename}"  # Unique filename
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_url = f"http://localhost:8000/static/{filename}"
        uploaded_images.append(file_url)  # Store image URL
        print(f"File uploaded successfully: {file_url}")
        return {"url": file_url}
    except Exception as e:
        print(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# ✅ New API: Fetch all uploaded images
@app.get("/images/")
async def get_uploaded_images():
    print("Fetching all uploaded images")
    return {"images": uploaded_images}

# ✅ New API: Delete an image
@app.delete("/delete/")
async def delete_image(image_url: str = Query(..., description="URL of the image to delete")):
    filename = image_url.split("/")[-1]
    file_path = os.path.join(UPLOAD_DIR, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        uploaded_images.remove(image_url)  # Remove from stored list
        print(f"Image deleted successfully: {image_url}")
        return {"message": "Image deleted successfully"}
    else:
        print(f"Image not found: {image_url}")
        raise HTTPException(status_code=404, detail="Image not found")

# Serve static files
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")