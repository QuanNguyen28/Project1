from datetime import datetime, timezone

from typing import List

from sqlalchemy import func

from sqlalchemy.orm import Session

from src.db.models import JDVersion


def create_version(
    db: Session,
    jd_id: int,
    content_md: str,
    updated_by: str,
    timestamp: datetime | None = None,
) -> int:

    latest = (
        db.query(func.max(JDVersion.version_number))
        .filter(JDVersion.jd_id == jd_id)
        .scalar()
        or 0
    )

    version = JDVersion(
        jd_id=jd_id,
        version_number=latest + 1,
        content_md=content_md,
        edited_by=updated_by or "system",
        edited_at=timestamp or datetime.now(timezone.utc).replace(tzinfo=None),
    )

    db.add(version)

    db.commit()

    db.refresh(version)

    return version.version_number


def get_versions_by_jd_id(db: Session, jd_id: int) -> List[JDVersion]:

    return (
        db.query(JDVersion)
        .filter(JDVersion.jd_id == jd_id)
        .order_by(JDVersion.version_number.desc())
        .all()
    )


def get_all_chunks(db: Session):

    return [
        {"text": chunk, "vector": []}
        for version in db.query(JDVersion).all()
        for chunk in version.content_md.split("\n\n")
        if chunk.strip()
    ]
