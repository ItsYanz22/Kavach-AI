from pydantic import BaseModel

class MessageInput(BaseModel):
    text: str

class DetectResponse(BaseModel):
    classification: str
    confidence: float
    reason: str