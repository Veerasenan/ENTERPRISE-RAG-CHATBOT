# Enterprise RAG Chatbot — Role-Based Company Policy Assistant

A production-style Retrieval-Augmented Generation chatbot where answers are
scoped to the logged-in user's role (Employee / Manager / HR). Built with
FastAPI + PostgreSQL (identity/roles) + ChromaDB (vectors) + LangChain +
React (TypeScript).

## Architecture
- **PostgreSQL** — stores users, roles, and the document registry (who uploaded what, visible to which roles).
- **ChromaDB** — stores embedded PDF chunks, tagged with boolean role flags (`role_employee`, `role_manager`, `role_hr`).
- **FastAPI** — auth (JWT), HR-only upload endpoint, chat endpoint that filters retrieval by the caller's role BEFORE the LLM sees any text.
- **React** — login screen, role-aware sidebar, chat UI, and an HR-only document management screen.

## Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# create the Postgres database first, e.g. in pgAdmin:
#   CREATE DATABASE enterprise_rag_db;

copy .env.example .env        # then edit DATABASE_URL, GOOGLE_API_KEY, JWT_SECRET_KEY

python -m scripts.seed_users  # creates employee@company.com / manager@company.com / hr@company.com (password: test1234)

uvicorn app.main:app --reload --port 8000
```

Open http://localhost:8000/docs for the interactive API docs.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — log in with one of the seeded test accounts.

## Testing the role-based behavior
1. Log in as `hr@company.com` → go to **Manage documents** → upload a PDF, check only "Manager" and "HR" → upload.
2. Log out, log in as `employee@company.com` → ask a question about that document's content → you'll get the "not available to your role" message.
3. Log in as `manager@company.com` → ask the same question → you'll get a real answer, because Manager is in the document's allowed roles.

## Docker (optional)
```bash
docker compose up --build
```
