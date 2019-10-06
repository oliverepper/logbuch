# CRUD Operations on Log
from typing import Dict, List

from sqlalchemy import or_

from app import db
from app.models import Log, LogSchema, User

from . import DataServiceException


# CREATE
def create_log(log_data: Dict, user: User) -> Log:
    if title:=log_data["title"]:
        existing_log = Log.query.filter_by(owner=user, title=title).first()
        if existing_log:
            raise DataServiceException(f'Your {existing_log} is titled "{title}" already.')
    
    log = Log(owner=user)
    db.session.add(log)

    try:
        LogSchema().load(log_data, instance=log, session=db.session)  # this might throw
    except Exception as e:
        # TODO: omitting this rollback could be a really bad bug! Double check
        db.session.rollback()
        raise DataServiceException(str(e))

    # some additional business logic would go here
    # logs_total = Log.query.filter_by(owner=user, title=log.title).all()
    # if len(logs_total) > 1:
    #     db.session.rollback()
    #     raise DataServiceException(f'Your {logs_total[0]} is titled "{log.title}" already.')
        
    db.session.commit()
    return log


# READ ALL
def read_logs(user: User) -> List[Log]:
    return user.my_logs


# READ
def read_log(log_id: int, user: User) -> Log:
    try:
        return Log.query.filter(
            or_(Log.owner == user, Log.members.contains(user)), Log.id == log_id
        ).one()
    except Exception as e:
        raise DataServiceException(f"<Log {log_id}> not found in your logs.", 404)


# UPDATE
def update_log(log_id: int, log_data: Dict, user: User) -> Log:
    log = read_log(log_id, user)

    try:
        LogSchema().load(log_data, instance=log, session=db.session)
    except Exception as e:
        raise DataServiceException(str(e))

    # additional business logic would go here
    if not user.has_write_permission(log):
        # fucker trying to fool us? Is that still possible? - Only if owner is not dump_only
        db.session.rollback()
        raise DataServiceException(f"You are not allowed to update the owner for {log}.", 403)

    db.session.commit()
    return log


# DELETE
def delete_log(log_id: int, user: User) -> Log:
    log = read_log(log_id, user)
    if log.owner is user:
        db.session.delete(log)
        db.session.commit()
        return log
    raise DataServiceException("You're not allowed to delete this log.", 403)
