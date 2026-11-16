
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.issue import IssuePriority, IssueStatus, IssueType


class IssueCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None

    issue_type: IssueType = IssueType.TASK
    status: IssueStatus = IssueStatus.TODO
    priority: IssuePriority = IssuePriority.MEDIUM

    project_id: int = Field(gt=0)
    assignee_id: int | None = Field(default=None, gt=0)

    due_date: date | None = None
    
    model_config=ConfigDict(extra="forbid")


class IssueUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None

    issue_type: IssueType | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None

    assignee_id: int | None = Field(default=None, gt=0)
    due_date: date | None = None


class IssueRead(BaseModel):
    id: int
    title: str
    description: str | None

    issue_type: IssueType
    status: IssueStatus
    priority: IssuePriority

    project_id: int
    reporter_id: int
    assignee_id: int | None
    due_date: date | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
