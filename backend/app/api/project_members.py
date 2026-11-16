
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberRead,
    ProjectMemberUpdate,
)
from app.services.project_member_service import (
    add_project_member,
    get_project_members,
    update_project_member_role,
    remove_project_member,
    ProjectMemberNotFoundError,
    ProjectMemberUserNotFoundError,
    DuplicateProjectMemberError,
    InvalidProjectMemberRoleError,
    ProjectOwnerMembershipError,
)
from app.services.permission_service import (
    PermissionProjectNotFoundError,
    ProjectAccessDeniedError,
    ProjectRolePermissionError,
)

router = APIRouter(
    prefix="/projects/{project_id}/members",
    tags=["project-members"],
)

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# 1. Add a project member
@router.post(
    "/",
    response_model=ProjectMemberRead,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        return add_project_member(
            db,
            project_id,
            current_user.id,
            member_data,
        )
    except PermissionProjectNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ProjectMemberUserNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except DuplicateProjectMemberError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    except (InvalidProjectMemberRoleError, ProjectOwnerMembershipError) as exc:
        raise HTTPException(400, detail=str(exc)) from exc


# 2. List project members
@router.get("/", response_model=list[ProjectMemberRead])
def list_members(
    project_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        return get_project_members(
            db,
            project_id,
            current_user.id,
        )
    except PermissionProjectNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise HTTPException(403, detail=str(exc)) from exc


# 3. Update a member's role
@router.put(
    "/{user_id}",
    response_model=ProjectMemberRead,
)
def update_member(
    project_id: int,
    user_id: int,
    member_data: ProjectMemberUpdate,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        return update_project_member_role(
            db,
            project_id,
            user_id,
            current_user.id,
            member_data,
        )
    except PermissionProjectNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ProjectMemberNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except (InvalidProjectMemberRoleError, ProjectOwnerMembershipError) as exc:
        raise HTTPException(400, detail=str(exc)) from exc


# 4. Remove a project member
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    project_id: int,
    user_id: int,
    db: DbSession,
    current_user: CurrentUser,
):
    try:
        remove_project_member(
            db,
            project_id,
            user_id,
            current_user.id,
        )
    except PermissionProjectNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except (ProjectAccessDeniedError, ProjectRolePermissionError) as exc:
        raise HTTPException(403, detail=str(exc)) from exc
    except ProjectMemberNotFoundError as exc:
        raise HTTPException(404, detail=str(exc)) from exc
    except ProjectOwnerMembershipError as exc:
        raise HTTPException(400, detail=str(exc)) from exc
