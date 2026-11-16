from datetime import date,datetime
from enum import Enum as PyEnum

from sqlalchemy import Date,DateTime,Enum,ForeignKey,String,Text,func
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.base import Base

class IssueType(str,PyEnum):
    TASK="task"
    BUG="bug"
    STORY="story"
    
    
    
    
class IssueStatus(str,PyEnum):
    TODO="todo"
    IN_PROGRESS="in_progress"
    DONE="done"
    
    
class IssuePriority(str,PyEnum):
    LOW="low"
    MEDIUM="medium"
    HIGH="high"
    CRITICAL="critical"
    
def enum_values(enum_class):
    return [item.value for item in enum_class]


class Issue(Base):
    __tablename__="issues"
    
    id:Mapped[int]=mapped_column(primary_key=True,index=True)
    
    title:Mapped[str]=mapped_column(String(200),nullable=False)
    description:Mapped[str|None]=mapped_column(Text,nullable=True)
    
    issue_type:Mapped[IssueType]=mapped_column(
        Enum(
            IssueType,
            name="issue_type",
            values_callable=enum_values,
        ),
        nullable=False,
        default=IssueType.TASK,
    )
    
    status:Mapped[IssueStatus]=mapped_column(
        Enum(
            IssueStatus,
            name="issue_status",
            values_callable=enum_values,
        ),
        nullable=False,
        default=IssueStatus.TODO,
    )
    
    priority:Mapped[IssuePriority]=mapped_column(
        Enum(
            IssuePriority,
            name="issue_priority",
            values_callable=enum_values,
        ),
        nullable=False,
        default=IssuePriority.MEDIUM,
    )
    
    project_id:Mapped[int]=mapped_column(
        ForeignKey("projects.id",ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    reporter_id:Mapped[int]=mapped_column(
        ForeignKey("users.id",ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    
    assignee_id:Mapped[int|None]=mapped_column(
        ForeignKey("users.id",ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    
    due_date:Mapped[date |None]=mapped_column(Date,nullable=True)
    
    created_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    updated_at:Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    
    project:Mapped["Project"]=relationship(back_populates="issues")
    
    
    reporter:Mapped["User"]=relationship(
        back_populates="reported_issues",
        foreign_keys=[reporter_id],
    )
    
    assignee:Mapped["User|None"]=relationship(
        back_populates="assigned_issues",
        foreign_keys=[assignee_id],
    )
    
    