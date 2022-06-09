from pydantic import BaseModel

class Query(BaseModel):
    data: str