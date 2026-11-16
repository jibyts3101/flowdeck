
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Issue, Project, ProjectMember, User
from app.schemas.issue import IssueCreate, IssueUpdate
from app.services.permission_service import (
    require_project_role,
    PermissionProjectNotFoundError,
    ProjectAccessDeniedError,
    ProjectRolePermissionError,
)


class IssueNotFoundError(Exception):
    pass


class IssueProjectNotFoundError(Exception):
    pass


class IssueUserNotFoundError(Exception):
    pass


class DuplicateIssueError(Exception):
    pass

class IssuePermissionError(Exception):
    pass


def create_issue(db: Session, issue_data: IssueCreate, reporter_id: int):

    project = db.get(Project, issue_data.project_id)

    if project is None:
        raise IssueProjectNotFoundError("Project not found")

    # Only Admins and Developers can create issues.
    try:
        require_project_role(
            db,
            issue_data.project_id,
            reporter_id,
            {"admin", "developer"},
        )
    except PermissionProjectNotFoundError as exc:
        raise IssueProjectNotFoundError(str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise IssuePermissionError(str(exc)) from exc

    reporter = db.get(User, reporter_id)

    if reporter is None:
        raise IssueUserNotFoundError("Reporter not found")

    if issue_data.assignee_id is not None:
        assignee = db.get(User, issue_data.assignee_id)

        if assignee is None:
            raise IssueUserNotFoundError("Assignee not found")

    issue_data_dict = issue_data.model_dump()
    issue_data_dict["reporter_id"] = reporter_id

    issue = Issue(**issue_data_dict)

    try:
        db.add(issue)
        db.commit()
        db.refresh(issue)
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateIssueError(
            "Could not create issue due to a database constraint"
        ) from exc

    return issue


def get_all_issues(
    db: Session,
    current_user_id: int,
) -> list[Issue]:

    statement = (
        select(Issue)
        .join(Project, Issue.project_id == Project.id)
        .outerjoin(
            ProjectMember,
            (ProjectMember.project_id == Project.id)
            & (ProjectMember.user_id == current_user_id),
        )
        .where(
            (Project.owner_id == current_user_id)
            | (ProjectMember.user_id == current_user_id)
        )
        .order_by(Issue.id)
    )

    return list(db.scalars(statement).all())


def get_issue_by_id(db: Session, issue_id: int) -> Issue:
    issue = db.get(Issue, issue_id)

    if issue is None:
        raise IssueNotFoundError("Issue not found")

    return issue

def update_issue(
    db: Session,
    issue_id: int,
    issue_data: IssueUpdate,
    current_user_id: int,
) -> Issue:

    # Step 1: Retrieve the issue
    issue = db.get(Issue, issue_id)

    if issue is None:
        raise IssueNotFoundError("Issue not found")

    # Step 2: Retrieve the associated project
    project = db.get(Project, issue.project_id)

    if project is None:
        raise IssueProjectNotFoundError("Project not found")

    # Step 3: Verify project role permissions
    try:
        require_project_role(
            db,
            issue.project_id,
            current_user_id,
            {"admin", "developer"},
        )
    except PermissionProjectNotFoundError as exc:
        raise IssueProjectNotFoundError(str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise IssuePermissionError(str(exc)) from exc

    # Step 4: Prepare the fields to update
    updates = issue_data.model_dump(exclude_unset=True)

    # Step 5: Validate the assignee
    if "assignee_id" in updates and updates["assignee_id"] is not None:
        assignee = db.get(User, updates["assignee_id"])

        if assignee is None:
            raise IssueUserNotFoundError("Assignee not found")

    # Step 6: Apply updates
    for field, value in updates.items():
        setattr(issue, field, value)

    # Step 7: Save changes
    try:
        db.commit()
        db.refresh(issue)
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateIssueError(
            "Could not update issue due to a database constraint"
        ) from exc

    return issue


def delete_issue(
    db: Session,
    issue_id: int,
    current_user_id: int,
) -> None:
    issue = db.get(Issue, issue_id)
    if issue is None:
        raise IssueNotFoundError("Issue not found")

    project = db.get(Project, issue.project_id)

    if project is None:
        raise IssueProjectNotFoundError("Project not found")

    # Only Admins can delete issues.
    try:
        require_project_role(
        db,
        issue.project_id,
        current_user_id,
        {"admin"},
        )
    except PermissionProjectNotFoundError as exc:
        raise IssueProjectNotFoundError(str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise IssuePermissionError(str(exc)) from exc

    db.delete(issue)
    db.commit()