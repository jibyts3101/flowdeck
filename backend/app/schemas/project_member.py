
from pydantic import BaseModel, ConfigDict, Field


class ProjectMemberCreate(BaseModel):
    user_id: int
    role: str = Field(default="developer")


class ProjectMemberUpdate(BaseModel):
    role: str


class ProjectMemberRead(BaseModel):
    id: int
    project_id: int
    user_id: int
    role: str
    username: str
    full_name: str | None
    email: str

    model_config = ConfigDict(from_attributes=True)
