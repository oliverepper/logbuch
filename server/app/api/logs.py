from flask import g, request

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import token_auth
from app.data_service import DataServiceException, logs
from app.models import Log, LogSchema


# CREATE LOG
@bp.route("/logs", methods=["POST"])
@token_auth.login_required
def create_log():
    json_data = request.get_json() or {}
    try:
        log = logs.create_log(json_data, g.current_user)
    except DataServiceException as dse:
        raise ApiException(dse.message, dse.status)
    return ApiResult({"message":f"{log} created."}, 201)


# READ ALL LOGS
@bp.route("/logs", methods=["GET"])
@token_auth.login_required
def get_logs():
    log_list = logs.read_logs(g.current_user)
    return ApiResult({"logs": LogSchema(many=True).dump(log_list)})


# READ LOG
@bp.route("/logs/<int:id>", methods=["GET"])
@token_auth.login_required
def get_log(id):
    try:
        log = logs.read_log(id, user=g.current_user)
    except DataServiceException as e:
        raise ApiException(e.message, e.status)
    return ApiResult(LogSchema().dump(log))


# UPDATE LOG
@bp.route("/logs/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_log(id):
    json_data = request.get_json() or {}
    try:
        log = logs.update_log(id, json_data, g.current_user)
    except DataServiceException as dse:
        raise ApiException(f"{dse.message} Cannot update log.", dse.status)
    return ApiResult({"message":f"{log} updated."})


# DELETE LOG
@bp.route("/logs/<int:id>", methods=["DELETE"])
@token_auth.login_required
def delete_log(id):
    try:
        log = logs.delete_log(id, g.current_user)
    except DataServiceException as dse:
        raise ApiException(dse.message, dse.status)
    return ApiResult({"message": f"{log} deleted."})
