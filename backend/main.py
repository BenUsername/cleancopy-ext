from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List
from config import settings
from pydantic import BaseModel, Field
from bson import ObjectId
import certifi

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageCreate(BaseModel):
    session_id: str
    role: str
    content: str
    timestamp: datetime

class Message(MessageCreate):
    id: str = Field(default_factory=lambda: str(ObjectId()))

    class Config:
        json_encoders = {
            ObjectId: str
        }

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL, tlsCAFile=certifi.where())
    app.mongodb = app.mongodb_client[settings.DATABASE_NAME]
    
    # Create indexes
    await app.mongodb.messages.create_index("session_id")
    await app.mongodb.messages.create_index("timestamp")
    await app.mongodb.messages.create_index([("content", "text")])

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

def verify_api_key(api_key: str = Header(...)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403)
    return api_key

@app.post("/api/chat")
async def create_message(
    message: MessageCreate,
    api_key: str = Depends(verify_api_key)
):
    new_message = Message(
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        timestamp=message.timestamp
    )
    
    await app.mongodb.messages.insert_one(new_message.dict())
    return {"status": "success"}

@app.get("/api/chat/{session_id}")
async def get_session(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    messages = await app.mongodb.messages.find(
        {"session_id": session_id}
    ).sort("timestamp", 1).to_list(None)
    return messages

@app.get("/api/search")
async def search_messages(
    query: str,
    api_key: str = Depends(verify_api_key)
):
    messages = await app.mongodb.messages.find(
        {"$text": {"$search": query}}
    ).sort("timestamp", 1).to_list(None)
    return messages

@app.delete("/api/chat/{session_id}")
async def delete_session(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    result = await app.mongodb.messages.delete_many({"session_id": session_id})
    return {"deleted_count": result.deleted_count} 