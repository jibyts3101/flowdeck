# Flowdeck – Project & Issue Management Platform

Flowdeck is a full-stack project and issue management platform designed to help teams organize projects, manage tasks, track progress, and collaborate through role-based access control.

The application provides a REST API built with **Python and FastAPI**, a **PostgreSQL** database, and a responsive web interface developed using **Next.js, TypeScript, and Tailwind CSS**.

## Features

### Authentication and User Management
- User registration and login.
- Secure password hashing.
- JWT-based authentication.
- Protected application routes.

### Project Management
- Create and view projects.
- Update project details.
- Delete projects.
- Assign project owners.
- Manage project members.

### Role-Based Access Control

Project membership supports three roles:

| Role | Description |
|---|---|
| Admin | Manages project members and has elevated project access. |
| Developer | Participates in project work and issue management. |
| Viewer | Has read-oriented project access. |

The project creator is the **Owner**, with ownership privileges separate from the three membership roles.

### Issue Management
- Create, view, update, and delete issues.
- Support for Task, Bug, and Story issue types.
- Track issue status: Todo, In Progress, and Done.
- Set priorities: Low, Medium, High, and Critical.
- Assign issues to users.
- Track issue reporters.

### Dashboard
- View project and issue statistics.
- Track issue statuses.
- Monitor high-priority and critical issues.
- View recent issues.

## Technology Stack

| Area | Technology |
|---|---|
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migrations | Alembic |
| Authentication | JWT |
| Password Hashing | pwdlib |
| Frontend | Next.js, React, TypeScript |
| Styling | Tailwind CSS |
| API Communication | REST API |
| Version Control | Git and GitHub |

## Project Structure

```text
flowdeck/
│
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── main.py
│   ├── alembic.ini
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   └── app/
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
│
├── .gitignore
└── README.md
```

## Getting Started

Follow these instructions to run Flowdeck locally.

### Prerequisites

Install the following:

- Python 3.14 or a compatible Python version.
- Node.js and npm.
- PostgreSQL.
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/jibyts3101/flowdeck.git
cd flowdeck
```

### 2. Backend Setup

Open a terminal in the project root:

```powershell
cd backend
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the backend example configuration:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and configure your local PostgreSQL credentials and a secure JWT secret:

```env
APP_NAME=Flowdeck API
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/flowdeck
SECRET_KEY=replace_with_a_secure_random_secret
```

Make sure PostgreSQL is running and the `flowdeck` database has been created.

**Important:** Never commit your actual `.env` file or secret values to GitHub.

### 4. Run Database Migrations

From the `backend` directory:

```powershell
alembic upgrade head
```

### 5. Start the Backend Server

```powershell
python -m uvicorn main:app --reload
```

Backend API:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### 6. Frontend Setup

Open another terminal in the project root:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Copy the frontend example configuration:

```powershell
Copy-Item .env.example .env.local
```

The `.env.local` file contains the backend API URLs:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
API_URL=http://127.0.0.1:8000
```

Make sure the backend server is running before starting the frontend.

Start the frontend:

```powershell
npm run dev
```

Open the application:

http://localhost:3000

## API Modules

The backend provides REST API endpoints for:

| Module | Endpoint |
|---|---|
| Authentication | `/auth/` |
| Users | `/users/` |
| Projects | `/projects/` |
| Project Members | `/projects/{project_id}/members/` |
| Issues | `/issues/` |
| Health Check | `/health` |

For detailed endpoint schemas and interactive testing, open the FastAPI Swagger documentation at `/docs`.

## Learning Objectives

This project was developed to gain practical experience with:

- Building REST APIs using FastAPI.
- Designing relational databases using PostgreSQL.
- Working with SQLAlchemy and Alembic.
- Implementing JWT authentication and authorization.
- Organizing backend code using models, schemas, services, and API routes.
- Building frontend applications using Next.js and TypeScript.
- Integrating frontend applications with backend APIs.
- Implementing role-based access control.
- Using Git and GitHub for version control.

## Future Enhancements

- AI-powered project assistant.
- Advanced project analytics.
- Notifications and activity tracking.
- Enhanced team collaboration features.

## Author

**Jiby Ts**

GitHub: [@jibyts3101](https://github.com/jibyts3101)

---

*Flowdeck – Organize Projects. Track Progress. Collaborate Better.*