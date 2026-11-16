
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.models.user import User
from app.db.dependencies import get_db
from app.schemas.issue import IssueCreate, IssueRead, IssueUpdate
from app.services.issue_service import (
    DuplicateIssueError,
    IssueNotFoundError,
    IssueProjectNotFoundError,
    IssuePermissionError,
    IssueUserNotFoundError,
    create_issue,
    delete_issue,
    get_all_issues,
    get_issue_by_id,
    update_issue,
)

router = APIRouter(
    prefix="/issues",
    tags=["issues"],
    dependencies=[Depends(get_current_user)],
)
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=IssueRead, status_code=201)
def create_issue_endpoint(
    issue_data: IssueCreate,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return create_issue(db, issue_data, current_user.id)
    except IssueProjectNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except IssueUserNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except DuplicateIssueError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except IssuePermissionError as exc:
        raise HTTPException(
        status_code=403,
        detail=str(exc),
        ) from exc


@router.get("/", response_model=list[IssueRead])
def list_issues_endpoint(
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return get_all_issues(db, current_user.id)


@router.get("/{issue_id}", response_model=IssueRead)
def get_issue_endpoint(
    issue_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return get_issue_by_id(
            db,
            issue_id,
            current_user.id,
        )
    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except IssuePermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=str(exc),
        ) from exc


@router.patch("/{issue_id}", response_model=IssueRead)
def update_issue_endpoint(
    issue_id: int,
    issue_data: IssueUpdate,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        return update_issue(
            db,
            issue_id,
            issue_data,
            current_user.id,
        )
    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except IssueProjectNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except IssueUserNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except IssuePermissionError as exc:
        raise HTTPException(
            status_code=403, detail=str(exc)
        ) from exc
    except DuplicateIssueError as exc:
        raise HTTPException(
            status_code=409, detail=str(exc)
        ) from exc


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue_endpoint(
    issue_id: int,
    db: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        delete_issue(db, issue_id, current_user.id)
    except IssueNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except IssueProjectNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except IssuePermissionError as exc:
        raise HTTPException(
            status_code=403, detail=str(exc)
        ) from exc
