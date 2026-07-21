"""
SQLAlchemy ORM model for users and their roles.
This lives in PostgreSQL — identity/auth data, separate from ChromaDB (vectors).
"""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class RoleEnum(str, enum.Enum):
    EMPLOYEE = "Employee"
    MANAGER = "Manager"
    HR = "HR"


# Role hierarchy: which roles' documents each role is allowed to see.
# Manager sees Employee + Manager docs; HR sees everything.
ROLE_HIERARCHY: dict[str, list[str]] = {
    RoleEnum.EMPLOYEE.value: [RoleEnum.EMPLOYEE.value],
    RoleEnum.MANAGER.value: [RoleEnum.EMPLOYEE.value, RoleEnum.MANAGER.value],
    RoleEnum.HR.value: [RoleEnum.EMPLOYEE.value, RoleEnum.MANAGER.value, RoleEnum.HR.value],
}


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[RoleEnum] = mapped_column(SAEnum(RoleEnum, name="role_enum"), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    @property
    def visible_roles(self) -> list[str]:
        """Roles whose documents this user is permitted to retrieve."""
        return ROLE_HIERARCHY[self.role.value]

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"
