from typing import Annotated
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.dependencies import get_db


router=APIRouter()


@router.get("/health")
def healthcheck():
    return {"status":"healthy"}


@router.get("/health/database")
def database_healthcheck(
    db:Annotated[Session,Depends(get_db)],
):
    db.execute(text("SELECT 1"))
    return {"database":"connected"}