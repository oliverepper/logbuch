import logging

from flask import g, jsonify, request
from flask_cors import cross_origin

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models import Entry, EntrySchema, Log, LogSchema

from . import logs


# GET TOKEN FOR USER
@bp.route("/api/token", methods=["GET"])
@basic_auth.login_required
def get_token():
    token = g.current_user.api_token
    if not token.is_valid:
        g.current_user.update_api_token()
        db.session.commit()
        token = g.current_user.api_token
    return ApiResult({"token": token.value})




# READ ENTRY
@bp.route("/api/logs/<int:id>/entries", methods=["GET"])
@token_auth.login_required
def get_entries_in_log(id):
    try:
        log = Log.query.filter_by(owner=g.current_user, id=id).one()
    except Exception as e:
        raise ApiException(f"Log <{str(id)}> not available. [{str(e)}]")
    return ApiResult(EntrySchema(many=True).dump(log.entries))


# CREATE ENTRY
@bp.route("/api/entries", methods=["POST"])
@token_auth.login_required
def create_entry():
    json_data = request.get_json() or {}
    logging.debug(f"json:\n{json_data}")
    try:
        entry = EntrySchema().load(json_data, session=db.session)
    except Exception as e:
        raise ApiException(e)
    logging.debug(f"entry: {entry}")
    logging.debug(f"entry.content: {entry.content}")
    logging.debug(f"entry.log: {entry.log}")
    # FIXME: if entry has non or invalid log do something clever
    if entry.log.owner != g.current_user:
        raise ApiException("Cannot save for another user")
    try:
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        raise ApiException(e)
    return ApiResult({"message": f"{entry} added."})


# ALL ENTRIES
@bp.route("/api/entries", methods=["GET"])
@token_auth.login_required
def get_entries():
    entries = Entry.query.join(Log).filter(Log.owner == g.current_user).all()
    return ApiResult({"entries": EntrySchema(many=True).dump(entries)})


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
        raise ApiException(f"Entry <{str(id)}> not available. <{str(e)}>")
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
