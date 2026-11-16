from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router as user_router
from app.api.projects import router as project_router
from app.api.issues import router as issue_router
from app.api.auth import router as auth_router
from app.api.project_members import router as project_members_router

app = FastAPI(
    title="Flowdeck API",
    description="A project and issue management platform",
    version="1.0.0",
)

# Allow the Next.js frontend to communicate with FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(project_router)
app.include_router(issue_router)
app.include_router(auth_router)
app.include_router(project_members_router)