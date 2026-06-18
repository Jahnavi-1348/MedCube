import os
import asyncio
import logging
from pathlib import Path
from fastapi import UploadFile, File, Depends, APIRouter, HTTPException
from service.auth import get_current_user
from service.retrieval import chunk_pdf
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
router = APIRouter()
 
# Upload directory: relative to this file's location, or overridden by env var
_default_upload_dir = Path(__file__).parent.parent / "uploaded_pdfs"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", _default_upload_dir))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
 
MAX_FILE_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 500))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
 
 
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    # Validate file extension
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are accepted.")
 
    # Sanitize filename — strip any directory components from client-supplied name
    safe_filename = os.path.basename(file.filename)
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
 
    prefixed_filename = f"{user['username']}_{safe_filename}"
    file_path = UPLOAD_DIR / prefixed_filename
 
    # Reject duplicate uploads to avoid Pinecone vector duplication
    if file_path.exists():
        raise HTTPException(
            status_code=409,
            detail=f"File '{safe_filename}' already uploaded. Delete it first before re-uploading."
        )
 
    # Stream file to disk in chunks to avoid loading entire file into memory
    total_bytes = 0
    try:
        with open(file_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_MB}MB."
                    )
                f.write(chunk)
    except HTTPException:
        # Clean up partial file on size violation
        if file_path.exists():
            file_path.unlink()
        raise
    except Exception as e:
        # Clean up partial file on any write error
        if file_path.exists():
            file_path.unlink()
        logger.error(f"Failed to save uploaded file '{prefixed_filename}': {e}")
        raise HTTPException(status_code=500, detail="Failed to save file.")
 
    # Run chunk_pdf in a thread pool — it's synchronous and CPU/IO heavy.
    # Calling it directly in an async route would block the event loop.
    try:
        await asyncio.to_thread(chunk_pdf, str(file_path))
    except Exception as e:
        # Clean up saved file if indexing fails — avoids orphaned files
        if file_path.exists():
            file_path.unlink()
        logger.error(f"Failed to index '{prefixed_filename}': {e}")
        raise HTTPException(status_code=500, detail="File saved but indexing failed. Please retry.")
 
    logger.info(f"User '{user['username']}' uploaded and indexed '{safe_filename}' ({total_bytes} bytes)")
    return {
        "message": f"PDF '{safe_filename}' uploaded and indexed successfully.",
        "file_size_bytes": total_bytes
    }
 