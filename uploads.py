import os
import datetime
from fastapi import FastAPI, UploadFile, File, Depends, APIRouter
from service.auth import get_current_user
from service.retrieval import chunk_pdf
from fastapi import HTTPException

app = FastAPI()
router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")
    
    filename = f"{user['username']}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    chunk_pdf(file_path)

    return {"message": f"PDF '{file.filename}' uploaded and indexed successfully"}