from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str|None=None
    
class UserUpdate(BaseModel):
    username:str
    email:EmailStr
    full_name: str|None=None

class UserRead(BaseModel):
    id:int
    username:str
    email:EmailStr
    full_name: str|None=None
    
    model_config=ConfigDict(from_attributes=True)