from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func
from sqlalchemy.orm import Session

from app.models import UserSession


SESSION_RETENTION_DAYS = 30


def cleanup_old_sessions(db: Session) -> int:
    now = datetime.now(timezone.utc)
    retention_limit = now - timedelta(days=SESSION_RETENTION_DAYS)

    statement = delete(UserSession).where(
        func.coalesce(
            UserSession.revoked_at,
            UserSession.expires_at,
        ) < retention_limit
    )

    result = db.execute(statement)
    db.commit()

    return result.rowcount or 0