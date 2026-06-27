from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

# === DATABASE ===
from database import engine, get_db
import models
models.Base.metadata.create_all(bind=engine)  # creates tables on startup

# === PIPELINE ===
from service.retrieval import smart_retrieve

# === AUTH ===
from service.auth import (
    create_access_token,
    get_current_user,
    authenticate_user,
    check_rate_limit,
    require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# === CRUD + SCHEMAS ===
from crud import create_user, get_user_by_username, get_user_by_email, get_all_users, deactivate_user
from schemas import UserRegister, UserResponse, TokenResponse

# === UPLOAD ROUTER ===
from uploads import router as upload_router


# === APP ===
app = FastAPI(title="MedCube", description="Medical PDF Retrieval & Summarization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)


# === AUTH ENDPOINTS ===

@app.post("/register", response_model=UserResponse, summary="Create a new doctor account (admin only)")
def register(
    user_data: UserRegister,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=409, detail="Username already taken.")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=409, detail="Email already registered.")
    return create_user(db, user_data)



@app.post("/token", response_model=TokenResponse, summary="Login and receive a JWT token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username
    }


@app.get("/protected", summary="Test authenticated access")
def protected_route(current_user=Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}, you are authenticated as {current_user.role}!"}


# === ADMIN ENDPOINTS ===

@app.get("/admin/users", response_model=list[UserResponse], summary="List all users (admin only)")
def list_users(
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return get_all_users(db)


@app.delete("/admin/users/{username}", summary="Deactivate a user (admin only)")
def deactivate(
    username: str,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    user = deactivate_user(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": f"User '{username}' has been deactivated."}


# === SEARCH ENDPOINT ===

@app.get("/search", summary="Search uploaded medical PDFs")
async def medical_search(
    user_query: str = Query(..., description="Natural language medical question"),
    dept: Optional[str] = Query(None),
    doc: Optional[str] = Query(None),
    issue: Optional[str] = Query(None),
    meds: Optional[str] = Query(None),
    patient: Optional[str] = Query(None),
    current_user=Depends(get_current_user)
):
    check_rate_limit(current_user.username)

    filters = {k: v for k, v in {
        "department": dept,
        "doctor": doc,
        "issue": issue,
        "medications": meds,
        "patient_name": patient
    }.items() if v}

    result = smart_retrieve(query=user_query, metadata_filter=filters if filters else None)

    return {
        "query": user_query,
        "filters_applied": filters,
        "summary": result.get("summary", "No summary available."),
        "chunks_found": len(result.get("raw_chunks", [])),
        "sources": list({
            m.get("file_name", "unknown")
            for m in result.get("metadata", [])
        }),
        "results": [
            {
                "text": chunk,
                "file_name": meta.get("file_name"),
                "page_number": meta.get("page_number"),
            }
            for chunk, meta in zip(
                result.get("raw_chunks", []),
                result.get("metadata", [])
            )
        ]
    }