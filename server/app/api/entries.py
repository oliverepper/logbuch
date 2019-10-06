from flask import g, request

from app import ApiException, ApiResult
from app.api import bp
from app.api.auth import token_auth
from app.data_service import DataServiceException, entries
from app.models import EntrySchema


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
    

# READ ALL ENTRIES IN A LOG
@bp.route("/api/logs/<int:id>/entries", methods=["GET"])
@token_auth.login_required
def get_entries_in_log(id):
    try:
        entry_list = entries.read_entries(id, g.current_user)
    except DataServiceException as dse:
        raise ApiException(dse.message, dse.status)
    return ApiResult({"entries": EntrySchema(many=True).dump(entry_list)})
    

# READ ENTRY
@bp.route("/api/entries/<int:id>", methods=["GET"])
@token_auth.login_required
def get_entry(id):
    try:
        entry = entries.read_entry(id, g.current_user)
    except Exception as e:
        raise ApiException(e.message, e.status)
    return ApiResult(EntrySchema().dump(entry))


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


# DELETE ENTRY
@bp.route("/api/entries/<int:id>", methods=["DELETE"])
@token_auth.login_required
def delete_entry(id):
    try:
        entry, log = entries.delete_entry(id, g.current_user)
    except DataServiceException as dse:
        raise ApiException(dse.message, dse.status)
    return ApiResult({"message": f"{entry} deleted from {log}."})


# READ ALL ENTRIES
# @bp.route("/api/entries", methods=["GET"])
# @token_auth.login_required
# def get_entries():
#     entries = Entry.query.join(Log).filter(Log.owner == g.current_user).all()
#     return ApiResult({"entries": EntrySchema(many=True).dump(entries)})
