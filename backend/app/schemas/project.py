from datetime import datetime

from pydantic import BaseModel, ConfigDict,Field


class ProjectCreate(BaseModel):
    name:str=Field(min_length=1,max_length=100)
    key:str=Field(min_length=2,max_length=10,pattern=r"^[A-Z][A-Z0-9]*$",)
    description:str|None=None
    
    
    model_config= ConfigDict(extra="forbid")
    
    
    
    
class ProjectUpdate(BaseModel):
    name:str|None=Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    key:str|None=Field(
        default=None,
        min_length=2,
        max_length=10,
        pattern=r"^[A-Z][A-Z0-9]*$",
    )
    description:str|None=None
    
    
class ProjectRead(BaseModel):
    id:int
    name:str
    key:str
    description:str|None
    owner_id:int
    created_at: datetime
    updated_at: datetime
    
    
    model_config=ConfigDict(from_attributes=True)