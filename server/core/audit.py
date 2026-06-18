from server.core.database import AuditLog, get_session


def add_audit(
    user_id: int = None,
    username: str = "system",
    action: str = None,
    resource_type: str = None,
    resource_id: str = None,
    old_value: str = None,
    new_value: str = None,
):
    session = get_session()
    try:
        audit = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
        )
        session.add(audit)
        session.commit()
    finally:
        session.close()


def get_audit_trail(filters: dict = None):
    session = get_session()
    try:
        q = session.query(AuditLog)
        if filters:
            if "user_id" in filters:
                q = q.filter(AuditLog.user_id == filters["user_id"])
            if "action" in filters:
                q = q.filter(AuditLog.action == filters["action"])
            if "resource_type" in filters:
                q = q.filter(AuditLog.resource_type == filters["resource_type"])
        q = q.order_by(AuditLog.created_at.desc()).limit(500)
        return [
            {
                "id": a.id,
                "user_id": a.user_id,
                "username": a.username,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "old_value": a.old_value,
                "new_value": a.new_value,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in q.all()
        ]
    finally:
        session.close()