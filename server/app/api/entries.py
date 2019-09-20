import logging

from flask import g, request

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import token_auth
from app.models import Log, Entry, EntrySchema


# CREATE ENTRY
@bp.route("/api/logs/<int:log_id>/entries", methods=["POST"])
@token_auth.login_required
def create_entry(log_id):
    json_data = request.get_json() or {}
    try:
        log = Log.query.filter_by(owner=g.current_user, id=log_id).one()
    except Exception as e:
        raise ApiException(f"<Log {log_id}> not found in your logs. Cannot create Entry.", 404)
    entry = Entry(log=log)
    db.session.add(log)
    try:
        EntrySchema().load(json_data, instance=entry, session=db.session)
    except Exception as e:
        raise ApiException(str(e))
    if entry.log != log:
        raise ApiException(f"Argument error. Log mismatch.", 403)
        db.session.rollback()
    db.session.commit()
    return ApiResult({"message": f"{entry} created in {log}."}, 201)


# READ ALL ENTRIES
# @bp.route("/api/entries", methods=["GET"])
# @token_auth.login_required
# def get_entries():
#     entries = Entry.query.join(Log).filter(Log.owner == g.current_user).all()
#     return ApiResult({"entries": EntrySchema(many=True).dump(entries)})


# READ ALL ENTRIES IN A LOG
@bp.route("/api/logs/<int:id>/entries", methods=["GET"])
@token_auth.login_required
def get_entries_in_log(id):
    try:
        log = Log.query.filter_by(owner=g.current_user, id=id).one()
    except Exception as e:
        raise ApiException(f"Log <{str(id)}> not available.", 404)
    return ApiResult({"entries": EntrySchema(many=True).dump(log.entries)})


# READ ENTRY
@bp.route("/api/entries/<int:id>", methods=["GET"])
@token_auth.login_required
def get_entry(id):
    try:
        entry = (
            Entry.query.join(Log)
            .filter(Log.owner == g.current_user, Entry.id == id)
            .one()
        )
    except Exception as e:
        raise ApiException(f"Entry <{str(id)}> not available.", 404)
    return ApiResult(EntrySchema().dump(entry))


# UPDATE ENTRY
@bp.route("/api/entries/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_entry(id):
    logging.debug("in update_entry")
    try:
        entry = (
            Entry.query.join(Log)
            .filter(Log.owner == g.current_user, Entry.id == id)
            .one()
        )
    except Exception as e:
        raise ApiException(f"Entry <{str(id)}> not available. <{str(e)}>")
    logging.debug(f"Entry loaded from db: {entry}")
    json_data = request.get_json() or {}
    logging.debug(f"json_data: {json_data}")
    try:
        EntrySchema().load(json_data, instance=entry, session=db.session)
    except Exception as e:
        raise ApiException(str(e))
    logging.debug("Entry updated from json_data")
    # are we allowed to update?
    if entry.log.owner != g.current_user:
        raise ApiException(f"You're not allowed to update.")
    db.session.add(entry)
    db.session.commit()
    return ApiResult({"message": f"{entry} updated."})


# DELETE ENTRY
@bp.route("/api/entries/<int:id>", methods=["DELETE"])
@token_auth.login_required
def delete_entry(id):
    try:
        entry = (
            Entry.query.join(Log)
            .filter(Log.owner == g.current_user, Entry.id == id)
            .one()
        )
    except Exception as e:
        raise ApiException(f"Entry <{str(id)}> not available. <{str(e)}>")
    log = entry.log
    db.session.delete(entry)
    db.session.commit()
    return ApiResult({"message": f"Entry <{id}> deleted from {log}."})