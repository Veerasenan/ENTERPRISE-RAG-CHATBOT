"""
One-time local setup script: creates the Postgres tables (if missing) and
inserts three test users, one per role, with password "test1234".

Run from the backend/ directory with:
    python -m scripts.seed_users
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))  # allow `app.*` imports

from app.config.database import SessionLocal, init_db
from app.core.security import hash_password
from app.models.user import RoleEnum, User

TEST_USERS = [
    {"email": "employee@company.com", "full_name": "Emma Employee", "role": RoleEnum.EMPLOYEE},
    {"email": "manager@company.com", "full_name": "Mark Manager", "role": RoleEnum.MANAGER},
    {"email": "hr@company.com", "full_name": "Hannah HR", "role": RoleEnum.HR},
]
DEFAULT_PASSWORD = "test1234"


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        for u in TEST_USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if existing:
                print(f"Skipping {u['email']} (already exists)")
                continue
            user = User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=hash_password(DEFAULT_PASSWORD),
                role=u["role"],
            )
            db.add(user)
            print(f"Created {u['email']} with role {u['role'].value}")
        db.commit()
    finally:
        db.close()

    print(f"\nDone. All test users have password: {DEFAULT_PASSWORD}")


if __name__ == "__main__":
    seed()
