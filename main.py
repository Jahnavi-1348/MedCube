from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import Optional

# === PIPELINE ===
from service.retrieval import smart_retrieve

# === AUTH ===
from service.auth import (
    create_access_token,
    get_current_user,
    authenticate_user,
    check_rate_limit,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# === UPLOAD ROUTER ===
from uploads import router as upload_router


# === APP ===
app = FastAPI(title="MedCube", description="Medical PDF Retrieval & Summarization")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)


# === AUTH ENDPOINTS ===

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['username']}, you are authenticated!"}

@app.get("/ping")
def ping():
    return {"status": "alive"}
# === SEARCH ENDPOINT ===

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