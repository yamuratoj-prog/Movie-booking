from fastapi import APIRouter, HTTPException
from app.app.infrastructure.db import mongo
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health/db")
async def health_db():
    if await mongo.ping():
        return JSONResponse(content={"status": "ok", "db": mongo.db_name})
    raise HTTPException(status_code=503, detail="DB connection failed")
