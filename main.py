from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app
app = FastAPI()

# Database models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # "customer" or "admin"

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    resolved = Column(Boolean, default=False)
    customer_id = Column(Integer, ForeignKey("users.id"))

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class ComplaintCreate(BaseModel):
    title: str
    description: str

class ComplaintResponse(BaseModel):
    id: int
    title: str
    description: str
    resolved: bool
    customer_id: int

    class Config:
        orm_mode = True

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.post("/register/", status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password=user.password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully", "user_id": db_user.id}

@app.post("/complaints/", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
def create_complaint(complaint: ComplaintCreate, customer_id: int, db: Session = Depends(get_db)):
    db_complaint = Complaint(**complaint.dict(), customer_id=customer_id)
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

@app.get("/complaints/", response_model=List[ComplaintResponse])
def get_complaints(resolved: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(Complaint)
    if resolved is not None:
        query = query.filter(Complaint.resolved == resolved)
    return query.all()

@app.put("/complaints/{complaint_id}/resolve/", response_model=ComplaintResponse)
def resolve_complaint(complaint_id: int, db: Session = Depends(get_db)):
    db_complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db_complaint.resolved = True
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

@app.get("/complaints/{complaint_id}/", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    db_complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not db_complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return db_complaint