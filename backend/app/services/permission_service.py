from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project,ProjectMember


class PermissionProjectNotFoundError(Exception):
    pass


class ProjectAccessDeniedError(Exception):
    pass


class ProjectRolePermissionError(Exception):
    pass


def get_project_role(
    db:Session,
    project_id:int,
    user_id:int
)->str:
    project=db.get(Project,project_id)
    
    if project is None:
        raise PermissionProjectNotFoundError(
            "project not found"
        )
        
    # The project owner is automatically an admin.
    if project.owner_id == user_id:
        return "admin"

    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id,
    )

    membership = db.scalar(statement)

    if membership is None:
        raise ProjectAccessDeniedError(
            "You are not a member of this project"
        )

    return membership.role


def require_project_role(
    db: Session,
    project_id: int,
    user_id: int,
    allowed_roles: set[str],
) -> str:

    role = get_project_role(
        db,
        project_id,
        user_id,
    )

    if role not in allowed_roles:
        raise ProjectRolePermissionError(
            "You do not have permission to perform this action"
        )   

    return role