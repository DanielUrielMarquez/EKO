
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models import UserSession
from app.services.session_service import cleanup_old_sessions


def test_cleanup_old_sessions(db_session, test_user):
    now = datetime.now(timezone.utc)

    old_expired = UserSession(
        jti=str(uuid4()),
        user_id=test_user.id,
        expires_at=now - timedelta(days=31),
    )

    old_revoked = UserSession(
        jti=str(uuid4()),
        user_id=test_user.id,
        expires_at=now + timedelta(days=10),
        revoked_at=now - timedelta(days=31),
    )

    recent_expired = UserSession(
        jti=str(uuid4()),
        user_id=test_user.id,
        expires_at=now - timedelta(days=10),
    )

    active_session = UserSession(
        jti=str(uuid4()),
        user_id=test_user.id,
        expires_at=now + timedelta(days=10),
    )

    db_session.add_all([
        old_expired,
        old_revoked,
        recent_expired,
        active_session,
    ])
    db_session.commit()

    deleted_count = cleanup_old_sessions(db_session)

    remaining_sessions = db_session.query(UserSession).all()
    remaining_jtis = {session.jti for session in remaining_sessions}

    assert deleted_count == 2
    assert len(remaining_sessions) == 2
    assert recent_expired.jti in remaining_jtis
    assert active_session.jti in remaining_jtis
