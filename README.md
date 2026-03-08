# HuskyVoice Leave Management

A full-stack Leave Management web application built for the HuskyVoice.AI hiring assignment.

---

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Frontend   | Vue 3 (Composition API) + Vite          |
| Styling    | Tailwind CSS                            |
| State      | Pinia + localStorage                    |
| Routing    | Vue Router 4 (with navigation guards)   |
| HTTP       | Axios (with request/response interceptors) |
| Backend    | Python FastAPI + Uvicorn (ASGI)         |
| Database   | MongoDB Atlas (Motor async driver)      |
| Auth       | JWT (python-jose) + bcrypt (passlib)    |
| Deployment | Vercel (frontend) + Render (backend)    |

---

## Project Structure

```
huskyvoice-leave/
├── backend/
│   ├── main.py                  # FastAPI app entry point, CORS, routers
│   ├── database.py              # MongoDB Atlas connection + indexes
│   ├── requirements.txt
│   ├── .env.example
│   ├── models/
│   │   ├── user.py              # Pydantic schemas: UserRegister, UserLogin, UserResponse
│   │   └── leave.py             # Pydantic schemas: LeaveApply, LeaveStatusUpdate
│   ├── utils/
│   │   └── password.py          # hash_password(), verify_password()
│   ├── middleware/
│   │   └── auth.py              # create_access_token(), get_current_user(), require_employer()
│   └── routes/
│       ├── auth.py              # POST /api/auth/register, POST /api/auth/login
│       └── leave.py             # POST /apply, GET /my, GET /all, PATCH /{id}/status
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── .env.example
    └── src/
        ├── main.js              # Bootstrap: createApp, pinia, router
        ├── App.vue              # Root component with <RouterView>
        ├── style.css            # Tailwind directives
        ├── api/
        │   ├── axios.js         # Axios instance with interceptors
        │   ├── auth.js          # login(), register()
        │   └── leave.js         # applyLeave(), getMyLeaves(), getAllLeaves(), updateLeaveStatus()
        ├── store/
        │   └── auth.js          # Pinia store: token, user, isLoggedIn, isEmployer, login(), logout()
        ├── router/
        │   └── index.js         # Routes + beforeEach navigation guard
        ├── components/
        │   └── NavBar.vue       # Top navigation bar
        └── views/
            ├── LoginView.vue
            ├── RegisterView.vue
            ├── EmployeeDashboard.vue   # Employee: view own leave history
            ├── ApplyLeave.vue          # Employee: submit leave request
            ├── EmployerDashboard.vue   # Employer: view + approve/reject all leaves
            └── NotFound.vue
```

---

## API Endpoints

### Auth

| Method | URL                    | Body                                      | Auth     | Description          |
|--------|------------------------|-------------------------------------------|----------|----------------------|
| POST   | `/api/auth/register`   | `{ name, email, password, role }`         | None     | Create account       |
| POST   | `/api/auth/login`      | `{ email, password }`                     | None     | Login, returns JWT   |

### Leave

| Method | URL                           | Body                             | Auth              | Description              |
|--------|-------------------------------|----------------------------------|-------------------|--------------------------|
| POST   | `/api/leave/apply`            | `{ leave_type, start_date, end_date, reason }` | Employee       | Submit leave request     |
| GET    | `/api/leave/my`               | —                                | Any logged in     | My leave history         |
| GET    | `/api/leave/all`              | —                                | Employer only     | All employees' leaves    |
| PATCH  | `/api/leave/{id}/status`      | `{ status, note? }`              | Employer only     | Approve or Reject leave  |

---

## Local Development Setup

### Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — add your MongoDB Atlas connection string and a random JWT_SECRET

# 4. Run the development server
uvicorn main:app --reload --port 8000

# 5. Open API docs
# http://localhost:8000/docs   (Swagger UI — interactive API explorer)
```

### Frontend

```bash
cd frontend

# 1. Install Node dependencies
npm install

# 2. Configure environment
cp .env.example .env
# VITE_API_URL=http://localhost:8000 (already set correctly for local dev)

# 3. Run dev server
npm run dev

# 4. Open app
# http://localhost:5173
```

---

## Environment Variables

### Backend `.env`

| Variable              | Example                                  | Description                          |
|-----------------------|------------------------------------------|--------------------------------------|
| `MONGO_URI`           | `mongodb+srv://user:pass@cluster.mongodb.net/` | MongoDB Atlas connection string |
| `DB_NAME`             | `huskyvoice_leave`                       | Database name                        |
| `JWT_SECRET`          | `your-super-secret-key-here`             | Secret for signing JWT tokens        |
| `JWT_EXPIRE_MINUTES`  | `1440`                                   | Token lifetime (1440 = 24 hours)     |
| `ALLOWED_ORIGINS`     | `http://localhost:5173`                  | Comma-separated CORS whitelist       |

### Frontend `.env`

| Variable        | Example                            | Description                     |
|-----------------|------------------------------------|---------------------------------|
| `VITE_API_URL`  | `http://localhost:8000`            | FastAPI backend URL             |

---

## Deployment (Free Tier)

### MongoDB Atlas
1. Create free M0 cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a database user + whitelist `0.0.0.0/0`
3. Copy the connection string to your backend `.env`

### Render (Backend)
1. Push code to GitHub
2. New Web Service → connect repo → Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add all env vars from `.env` in the Environment tab

### Vercel (Frontend)
1. New Project → connect repo → Root Directory: `frontend`
2. Framework: Vite (auto-detected)
3. Add `VITE_API_URL=https://your-backend.onrender.com` as an Environment Variable
4. Deploy

---

## Key Design Decisions

- **JWT in localStorage** — Simple for a demo app. In production, prefer HttpOnly cookies.
- **Role-based access** — Enforced at both the API level (FastAPI `Depends`) and frontend (router guards).
- **Motor (async MongoDB)** — Required because FastAPI is async. PyMongo would block the event loop.
- **Pydantic v2** — Uses `field_validator` and `model_dump()`. Not the old v1 `@validator` / `.dict()`.
- **Axios interceptors** — Attach JWT automatically on every request; handle token expiry globally.
- **Optimistic UI update** — EmployerDashboard updates the local leave status after a successful PATCH without re-fetching the full list.

---

## Roles Summary

| Action                        | Employee | Employer |
|-------------------------------|----------|----------|
| Register / Login              | ✅       | ✅       |
| Apply for leave               | ✅       | ❌       |
| View own leave history        | ✅       | ❌       |
| View all employees' leaves    | ❌       | ✅       |
| Approve / Reject leave        | ❌       | ✅       |
