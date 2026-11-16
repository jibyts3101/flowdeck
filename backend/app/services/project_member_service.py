
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Project, ProjectMember, User
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberUpdate,
)
from app.services.permission_service import (
    require_project_role,
    PermissionProjectNotFoundError,
    ProjectAccessDeniedError,
    ProjectRolePermissionError,
)


class ProjectMemberNotFoundError(Exception):
    pass


class ProjectMemberUserNotFoundError(Exception):
    pass


class DuplicateProjectMemberError(Exception):
    pass


class InvalidProjectMemberRoleError(Exception):
    pass


class ProjectOwnerMembershipError(Exception):
    pass


ALLOWED_ROLES = {"admin", "developer", "viewer"}



def build_member_response(
    member: ProjectMember,
    user: User,
) -> dict:
    return {
        "id": member.id,
        "project_id": member.project_id,
        "user_id": member.user_id,
        "role": member.role,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
    }



def check_admin_permission(
    db: Session,
    project_id: int,
    current_user_id: int,
) -> None:
    require_project_role(
        db,
        project_id,
        current_user_id,
        {"admin"},
    )


def add_project_member(
    db: Session,
    project_id: int,
    current_user_id: int,
    member_data: ProjectMemberCreate,
) -> dict:

    check_admin_permission(db, project_id, current_user_id)

    if member_data.role not in ALLOWED_ROLES:
        raise InvalidProjectMemberRoleError(
            "Role must be admin, developer, or viewer"
        )

    project = db.get(Project, project_id)

    if project.owner_id == member_data.user_id:
        raise ProjectOwnerMembershipError(
            "Project owner is already an admin"
        )

    user = db.get(User, member_data.user_id)

    if user is None:
        raise ProjectMemberUserNotFoundError(
            "User not found"
        )

    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_data.user_id,
    )

    existing_member = db.scalar(statement)

    if existing_member is not None:
        raise DuplicateProjectMemberError(
            "User is already a project member"
        )

    new_member = ProjectMember(
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role,
    )

    db.add(new_member)

    try:
        db.commit()
        db.refresh(new_member)
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateProjectMemberError(
            "User is already a project member"
        ) from exc

    return build_member_response(new_member, user)



def get_project_members(
    db: Session,
    project_id: int,
    current_user_id: int,
) -> list[dict]:

    check_admin_permission(db, project_id, current_user_id)

    statement = (
        select(ProjectMember, User)
        .join(User, ProjectMember.user_id == User.id)
        .where(ProjectMember.project_id == project_id)
        .order_by(ProjectMember.id)
    )

    results = db.execute(statement).all()

    return [
        build_member_response(member, user)
        for member, user in results
    ]




def update_project_member_role(
    db: Session,
    project_id: int,
    target_user_id: int,
    current_user_id: int,
    member_data: ProjectMemberUpdate,
) -> dict:

    check_admin_permission(db, project_id, current_user_id)

    if member_data.role not in ALLOWED_ROLES:
        raise InvalidProjectMemberRoleError(
            "Role must be admin, developer, or viewer"
        )

    project = db.get(Project, project_id)

    if project.owner_id == target_user_id:
        raise ProjectOwnerMembershipError(
            "The project owner's role cannot be changed"
        )

    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == target_user_id,
    )

    member = db.scalar(statement)

    if member is None:
        raise ProjectMemberNotFoundError(
            "Project member not found"
        )

    member.role = member_data.role

    db.commit()
    db.refresh(member)

    user = db.get(User, member.user_id)

    return build_member_response(member, user)



def remove_project_member(
    db: Session,
    project_id: int,
    target_user_id: int,
    current_user_id: int,
) -> None:

    check_admin_permission(db, project_id, current_user_id)

    project = db.get(Project, project_id)

    if project.owner_id == target_user_id:
        raise ProjectOwnerMembershipError(
            "The project owner cannot be removed"
        )

    statement = select(ProjectMember).where(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == target_user_id,
    )

    member = db.scalar(statement)

    if member is None:
        raise ProjectMemberNotFoundError(
            "Project member not found"
        )

    db.delete(member)
    db.commit()
