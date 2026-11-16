from sqlalchemy import select,or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Project,User,ProjectMember
from app.schemas.project import ProjectCreate,ProjectUpdate

class ProjectNotFoundError(Exception):
    pass


class ProjectOwnerNotFoundError(Exception):
    pass


class DuplicateProjectError(Exception):
    pass

class ProjectPermissionError(Exception):
    pass


def create_project(db: Session, project_data: ProjectCreate, owner_id: int):
    owner = db.get(User,owner_id)
    
    if owner is None:
        raise ProjectOwnerNotFoundError("Project owner does not exist")
    
    project = Project(
    name=project_data.name,
    key=project_data.key,
    description=project_data.description,
    owner_id=owner_id,
    )
    
    try:
        db.add(project)
        db.commit()
        db.refresh(project)
        return project
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateProjectError(
            "A project with this key already exists"
        )from exc
        
        
def get_all_projects(
    db: Session,
    current_user_id: int,
) -> list[Project]:

    statement = (
        select(Project)
        .outerjoin(
            ProjectMember,
            ProjectMember.project_id == Project.id,
        )
        .where(
            or_(
                Project.owner_id == current_user_id,
                ProjectMember.user_id == current_user_id,
            )
        )
        .distinct()
        .order_by(Project.id)
    )

    return list(db.scalars(statement).all())

def get_project_by_id(db:Session,project_id:int)->Project:
    project=db.get(Project,project_id)
    
    if project is None:
        raise ProjectNotFoundError("project not found")
    return project


def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate,
    current_user_id: int,
) -> Project:
    project = get_project_by_id(db, project_id)

    if project.owner_id != current_user_id:
        raise ProjectPermissionError(
            "You do not have permission to update this project"
        )

    update_data = project_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(project, field, value)

    try:
        db.commit()
        db.refresh(project)
        return project
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateProjectError(
            "A project with this key already exists"
        ) from exc
        
        
def delete_project(
    db: Session,
    project_id: int,
    current_user_id: int,
) -> None:
    project = get_project_by_id(db, project_id)

    if project.owner_id != current_user_id:
        raise ProjectPermissionError(
            "You do not have permission to delete this project"
        )

    db.delete(project)
    db.commit()
        