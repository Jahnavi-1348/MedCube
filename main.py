from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import Optional
import os, time

# === IMPORT PIPELINE ===
from service.retrieval import chunk_pdf, smart_retrieve
from service.summarize import summarize_text, prepare_text_for_summarization
from service.indexing import embed_and_store

# === AUTH IMPORT ===
from service.auth import create_access_token, get_current_user, FAKE_USERS_DB, ACCESS_TOKEN_EXPIRE_MINUTES

# === UPLOAD ROUTER ===
from uploads import router as upload_router

app = FastAPI(title="MedCube", description="Medical PDF Retrieval & Summarization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)

# === RATE LIMITING ===
RATE_LIMIT = 10
user_requests = {}

def check_rate_limit(user: str):
    now = time.time()
    if user not in user_requests:
        user_requests[user] = []
    user_requests[user] = [t for t in user_requests[user] if now - t < 60]
    if len(user_requests[user]) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    user_requests[user].append(now)


# === AUTH ENDPOINT ===
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or form_data.password != user["password"]:
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, you are authenticated!"}


@app.get("/search")
async def medical_search(
    user_query: str,
    dept: Optional[str] = Query(None),
    doc: Optional[str] = Query(None),
    issue: Optional[str] = Query(None),
    meds: Optional[str] = Query(None),
    patient: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    check_rate_limit(current_user["username"])

    filters = {k: v for k, v in {
        "department": dept,
        "doctor": doc,
        "issue": issue,
        "medications": meds,
        "patient_name": patient
    }.items() if v}

    response = smart_retrieve(query=user_query, metadata_filter=filters)

    return response