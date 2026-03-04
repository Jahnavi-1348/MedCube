# auth.py
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Dummy user DB (replace with real DB later)
FAKE_USERS_DB = {
    "testuser": 
    {"username": "testuser",
      "password": "password123"
      }
}


ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set!")





oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "sub": data.get("sub")  # make sure 'sub' is set
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")   
        if username is None or username not in FAKE_USERS_DB:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return FAKE_USERS_DB[username]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    print("--- Authentication script finished successfully! ---")