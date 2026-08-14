from typing import Optional
from pydantic import BaseModel


class UserProfile(BaseModel):
    age: Optional[int] = None
    state: Optional[str] = None
    occupation: Optional[str] = None
    education: Optional[str] = None
    income: Optional[int] = None