from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models.user import User
from app.db.dependencies import get_db
from app.schemas.project import ProjectCreate,ProjectRead,ProjectUpdate

from app.services.permission_service import (
    require_project_role,
    PermissionProjectNotFoundError,
    ProjectAccessDeniedError,
    ProjectRolePermissionError,
)
from app.services.project_service import (
    create_project,
    delete_project,
    get_all_projects,
    get_project_by_id,
    update_project,
    ProjectNotFoundError,
    ProjectOwnerNotFoundError,
    DuplicateProjectError,
    ProjectPermissionError
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)],
)
DbSession=Annotated[Session,Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=ProjectRead, status_code=201)
def create_project_endpoint(
    project_data: ProjectCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return create_project(db, project_data, current_user.id)
    except ProjectOwnerNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except DuplicateProjectError as error:
        raise HTTPException(status_code=409, detail=str(error))
    
    
@router.get("/", response_model=list[ProjectRead])
def list_projects(
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ProjectRead]:

    return get_all_projects(db, current_user.id)

@router.get("/{project_id}", response_model=ProjectRead)
def read_project(
    project_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> ProjectRead:
    try:
        require_project_role(
            db,
            project_id,
            current_user.id,
            {"admin", "developer", "viewer"},
        )

        return get_project_by_id(db, project_id)

    except PermissionProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except ProjectAccessDeniedError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    except ProjectRolePermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc

    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    
    
@router.patch("/{project_id}", response_model=ProjectRead)
def edit_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectRead:
    try:
        return update_project(
            db,
            project_id,
            project_data,
            current_user.id,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except ProjectPermissionError as exc:
        raise HTTPException(
            status_code=403, detail=str(exc)
        ) from exc
    except DuplicateProjectError as exc:
        raise HTTPException(
            status_code=409, detail=str(exc)
        ) from exc
    
    
@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project(
    project_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    try:
        delete_project(db, project_id, current_user.id)

    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc

    except ProjectPermissionError as exc:
        raise HTTPException(
            status_code=403, detail=str(exc)
        ) from exc