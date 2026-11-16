from fastapi import FastAPI
from app.api.users import router as user_router
from app.api.projects import router as project_router
from app.api.issues import router as issue_router
from app.api.auth import router as auth_router
from app.api.project_members import router as project_members_router

app=FastAPI(
     title="Jira Clone API",
    description="A project and issue management platform",
    version="1.0.0",
)

app.include_router(user_router)
app.include_router(project_router)
app.include_router(issue_router)
app.include_router(auth_router)
app.include_router(project_members_router)