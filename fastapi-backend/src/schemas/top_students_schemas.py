from pydantic import BaseModel
from typing import List, Optional

class TopStudentSchema(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    university_id: Optional[str] = None
    rating: Optional[int] = None
    solved_count: int

    class Config:
        from_attributes = True

class TopStudentsResponse(BaseModel):
    students: List[TopStudentSchema]
    total: int