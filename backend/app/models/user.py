
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column,relationship


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.issue import Issue
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    
    full_name:Mapped[str|None]=mapped_column(
        String(100),
        nullable=True,
        
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    
    password_hash: Mapped[str | None] = mapped_column(
    String(255),
    nullable=True,
    )

    owned_projects: Mapped[list["Project"]] = relationship(
    back_populates="owner",
    )
    
    reported_issues: Mapped[list["Issue"]] = relationship(
    back_populates="reporter",
    foreign_keys="Issue.reporter_id",
    )
    
    assigned_issues: Mapped[list["Issue"]] = relationship(
    back_populates="assignee",
    foreign_keys="Issue.assignee_id",
    )
    
    project_members = relationship(
    "ProjectMember",
    back_populates="user",
    cascade="all, delete-orphan",
    )


