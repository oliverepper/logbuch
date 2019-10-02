import logging

from flask import g, request
from sqlalchemy import or_

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import token_auth
from app.models import Entry, EntrySchema, Log, User

from app.data_service import entries
from app.data_service import DataServiceException


# CREATE ENTRY
@bp.route("/api/logs/<int:log_id>/entries", methods=["POST"])
@token_auth.login_required
def create_entry(log_id):
    json_data = request.get_json() or {}
    try:
        entry = entries.create_entry(log_id, json_data, g.current_user)
    except DataServiceException as e:
        raise ApiException(f"{e.message} Cannot create entry.", e.status)
    return ApiResult({"message": f"{entry} created in {entry.log}."}, 201)
    
    # json_data = request.get_json() or {}
    # try:
    #     # log = Log.query.filter_by(owner=g.current_user, id=log_id).one()
    #     log = Log.query.join(User).filter(
    #         or_(Log.owner == g.current_user, Log.members.contains(g.current_user)),
    #         Log.id == log_id,
    #     ).one()
    # except Exception as e:
    #     raise ApiException(
    #         f"<Log {log_id}> not found in your logs. Cannot create Entry.", 404
    #     )
    # entry = Entry(log=log, creator=g.current_user)
    # db.session.add(log)
    # try:
    #     EntrySchema().load(json_data, instance=entry, session=db.session)
    # except Exception as e:
    #     raise ApiException(str(e))
    # if entry.log != log:
    #     db.session.rollback()
    #     raise ApiException(f"Argument error. Log mismatch.", 403)
    # db.session.commit()
    # return ApiResult({"message": f"{entry} created in {log}."}, 201)


# READ ALL ENTRIES IN A LOG
@bp.route("/api/logs/<int:id>/entries", methods=["GET"])
@token_auth.login_required
def get_entries_in_log(id):
    try:
        log = Log.query.filter_by(owner=g.current_user, id=id).one()
    except Exception as e:
        raise ApiException(f"<Log {str(id)}> not available.", 404)
    return ApiResult({"entries": EntrySchema(many=True).dump(log.entries)})


# READ ENTRY
@bp.route("/api/entries/<int:id>", methods=["GET"])
@token_auth.login_required
def get_entry(id):
    try:
        entry = entries.read_entry(id, g.current_user)
    except Exception as e:
        raise ApiException(e.message, e.status)
    return ApiResult(EntrySchema().dump(entry))

    # try:
    #     entry = (
    #         Entry.query.join(Log)
    #         .filter(Log.owner == g.current_user, Entry.id == id)
    #         .one()
    #     )
    # except Exception as e:
    #     raise ApiException(f"Entry <{str(id)}> not available.", 404)
    # return ApiResult(EntrySchema().dump(entry))


# READ ALL ENTRIES
# @bp.route("/api/entries", methods=["GET"])
# @token_auth.login_required
# def get_entries():
#     entries = Entry.query.join(Log).filter(Log.owner == g.current_user).all()
#     return ApiResult({"entries": EntrySchema(many=True).dump(entries)})


# UPDATE ENTRY
@bp.route("/api/entries/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_entry(id):
    json_data = request.get_json() or {}
    try:
        entry = entries.update_entry(id, json_data, g.current_user)
    except DataServiceException as e:
        raise ApiException(f"{e.message} Cannot update entry.", e.status)
    return ApiResult({"message": f"{entry} updated."})

    # try:
    #     entry = (
    #         Entry.query.join(Log)
    #         .filter(Log.owner == g.current_user, Entry.id == id)
    #         .one()
    #     )
    # except Exception as e:
    #     raise ApiException(f"<Entry {str(id)}> not available.", 404)
    # json_data = request.get_json() or {}
    # try:
    #     EntrySchema().load(json_data, instance=entry, session=db.session)
    # except Exception as e:
    #     raise ApiException(str(e))
    # if entry.log.owner != g.current_user:
    #     db.session.rollback()
    #     raise ApiException(f"You're not allowed to perform this update.", 403)
    # db.session.add(entry)
    # db.session.commit()
    # return ApiResult({"message": f"{entry} updated."})


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
        raise ApiException(f"<Entry {str(id)}> not available.", 404)
    log = entry.log
    db.session.delete(entry)
    db.session.commit()
    return ApiResult({"message": f"{entry} deleted from {log}."})
