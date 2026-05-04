from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)


class SourceItem(BaseModel):
    file: str
    chunk_id: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceItem]
