"""Role and job-family taxonomy helpers."""

from typing import Any, Dict, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.db.models import JobFamily, Role


def _normalize(value: str) -> str:
    return " ".join(value.strip().split())


def get_or_create_family(db: Session, family_name: Optional[str]) -> Optional[int]:
    if not family_name or not str(family_name).strip():
        return None
    normalized = _normalize(str(family_name))
    family = (
        db.query(JobFamily)
        .filter(func.lower(JobFamily.name) == normalized.lower())
        .first()
    )
    if family is None:
        family = JobFamily(name=normalized, description=None)
        db.add(family)
        db.commit()
        db.refresh(family)
    return family.family_id


class RoleTaxonomyMapper:
    @staticmethod
    def get_or_create_family(db: Session, family_name: Optional[str]) -> Optional[int]:
        return get_or_create_family(db, family_name)

    @staticmethod
    def map_role_to_taxonomy(db: Session, role_name: str) -> Dict[str, Any]:
        if not role_name or not role_name.strip():
            raise ValueError("role_name is required")
        normalized = _normalize(role_name)
        role = (
            db.query(Role)
            .filter(func.lower(Role.role_name) == normalized.lower())
            .first()
        )
        if role is None:
            raise ValueError(f"Role {role_name!r} not found in taxonomy")
        return {"role_name": role.role_name}
