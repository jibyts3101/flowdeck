from sqlalchemy import ForeignKey,String,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.base import Base

class ProjectMember(Base):
    __tablename__=  "project_members"
    
    __table_args__=(
        UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_member",
        ),
    )
    
    id:Mapped[int]=mapped_column(
        primary_key=True,index=True
    )
    
    project_id:Mapped[int]=mapped_column(
        ForeignKey("projects.id",ondelete="CASCADE"),
        nullable=False,
    )
    
    user_id:Mapped[int]=mapped_column(
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
    )
    
    role:Mapped[str]=mapped_column(
        String(20),
        nullable=False,
        default="developer",
    )
    
    project=relationship("Project",back_populates="members")
    user=relationship("User",back_populates="project_members")