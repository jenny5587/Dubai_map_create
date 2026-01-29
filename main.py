# ==========================================================
# dubai 지도 MVP 백엔드
# ==========================================================

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from lat_lon import get_lat_lng_from_address
import warnings
import os
#  CORS 설정 추가
from fastapi.middleware.cors import CORSMiddleware
warnings.filterwarnings("ignore")

# ==========================================================
# DB 설정
# ==========================================================

DATABASE_URL = "sqlite:///./dubai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ==========================================================
# DB 모델
# ==========================================================

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    lat = Column(Float)
    lng = Column(Float)
    address = Column(String)
    price = Column(String)
    place_url = Column(String)
    last_verified_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ==========================================================
# Pydantic 스키마
# ==========================================================

class StoreCreate(BaseModel):
    name: Optional[str] = "dubai 지도"
    lat: float
    lng: float
    address: Optional[str] = None
    price: Optional[str] = None
    place_url: Optional[str] = None

class StoreOut(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    address: Optional[str]
    price: Optional[str]
    place_url: Optional[str]
    last_verified_at: datetime

    class Config:
        orm_mode = True

# ==========================================================
# FastAPI 앱 생성
# ==========================================================

app = FastAPI(title="dubai API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 현재 디렉토리의 "static" 폴더 마운트
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
@app.get("/")
def root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    else:
        return {"error": "index.html not found"}

# ==========================================================
# API Routes
# ==========================================================

## stores/docs해서 try it out으로 db에 추가 기입 가능 (26.01.09)
@app.post("/api/stores", response_model=StoreOut)
def create_store(store: StoreCreate):
    lat, lng = get_lat_lng_from_address(store.address)

    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="주소를 찾을 수 없습니다.")
    
    """지도에 새로운 가게 등록"""
    db = SessionLocal()
    
    db_store = Store(
        name=store.name,
        lat=store.lat,
        lng=store.lng,
        address=store.address,
        price=store.price,
        place_url=store.place_url,
        last_verified_at=datetime.utcnow()
    )
    
    db.add(db_store)
    db.commit()
    db.refresh(db_store)
    db.close()
    
    return db_store

@app.get("/api/stores", response_model=List[StoreOut])
def get_stores():
    """지도에 표시할 모든 가게 목록 조회"""
    db = SessionLocal()
    stores = db.query(Store).all()
    db.close()
    return stores

@app.get("/api/geocode")
def geocode(address: str):
    lat, lng = get_lat_lng_from_address(address)
    return {"lat": lat, "lng": lng}

# ==========================================================
# 실행: uvicorn main:app --reload
# ==========================================================
