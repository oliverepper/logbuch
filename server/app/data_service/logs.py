# CRUD Operations on Log
from typing import Dict

from sqlalchemy import or_

from app.models import Log, User

from . import DataServiceException


# CREATE
def create_log(log_data: Dict, user: User) -> Log:
    # FIXME: implement
    pass


# READ
def read_log(log_id: int, user: User) -> Log:
    try:
        return Log.query.filter(
            or_(Log.owner == user, Log.members.contains(user)), Log.id == log_id
        ).one()
    except Exception as e:
        raise DataServiceException(f"<Log {log_id}> not found in your logs.", 404)


# UPDATE
def update_log(log_id: int, user: User) -> Log:
    # FIXME: implement
    pass


# DELETE
def delete_log(log_id, user: User):
    # FIXME: implement
    pass
