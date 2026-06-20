from database import SessionLocal
from crud import create_user, get_user_by_username
from schemas import UserRegister

db = SessionLocal()

if get_user_by_username(db, "admin"):
    print("Admin already exists.")
else:
    create_user(db, UserRegister(
        username="admin",
        email="admin@medcube.com",
        full_name="System Admin",
        password="Admin123",
        role="admin"
    ))
    print("Admin created successfully.")

db.close()