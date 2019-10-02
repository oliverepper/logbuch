# CRUD Operations on Log
from app.models import Log, User
from sqlalchemy import or_
from . import DataServiceException


def read_log(log_id: int, user: User):
    try:
        return Log.query.filter(
            or_(Log.owner == user, Log.members.contains(user)), Log.id == log_id
        ).one()
    except Exception as e:
        raise DataServiceException(f"<Log {log_id}> not found in your logs.", 404)
