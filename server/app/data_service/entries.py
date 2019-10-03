# CRUD Operations on Entries
from typing import Dict, List, Tuple

from sqlalchemy import or_

from app import db
from app.models import Entry, EntrySchema, Log, User

from . import DataServiceException
from .logs import read_log


# CREATE
def create_entry(log_id: int, entry_data: Dict, user: User) -> Entry:
    log = read_log(log_id, user)  # this might throw

    entry = Entry(log=log, creator=user)
    db.session.add(entry)

    try:
        EntrySchema().load(
            entry_data, instance=entry, session=db.session
        )  # this might throw
    except Exception as e:
        raise DataServiceException(str(e))

    if entry.log != log:
        # fucker has tried to fool us about the log. (changed the log in the entry_data)
        # go fuck him back
        db.session.rollback()
        raise DataServiceException(f"Argument error. Log mismatch.", 403)
    db.session.commit()
    return entry


# READ ALL
def read_entries(log_id: int, user: User) -> List[Entry]:
    log = read_log(log_id, user)
    return log.entries


# READ
def read_entry(entry_id: int, user: User) -> Entry:
    try:
        return (
            Entry.query.join(Log)
            .filter(
                or_(Log.owner == user, Log.members.contains(user)), Entry.id == entry_id
            )
            .one()
        )
    except Exception as e:
        raise DataServiceException(f"<Entry {entry_id}> not found in your logs.", 404)


# UPDATE
def update_entry(entry_id: int, entry_data: Dict, user: User) -> Entry:
    entry = read_entry(entry_id, user)

    try:
        EntrySchema().load(entry_data, instance=entry, session=db.session)
    except Exception as e:
        raise DataServiceException(str(e))

    if entry.log.owner != user or not user.has_write_permission(entry.log):
        # fucker trying to fool us! go fuck him back
        db.session.rollback()
        raise DataServiceException("You're not allowed to perform this update.", 403)

    db.session.commit()
    return entry


# DELETE
def delete_entry(entry_id: int, user: User) -> (Entry, Log):
    entry = read_entry(entry_id, user)
    log = entry.log
    if entry.creator is user or entry.log.owner is user:
        db.session.delete(entry)
        db.session.commit()
        return (entry, log)
    raise DataServiceException("You're not allowed to delete this entry.", 403)