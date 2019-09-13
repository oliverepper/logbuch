from flask import g, jsonify
from flask_cors import cross_origin

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models import Log, LogSchema


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


# READ ALL LOGS
@bp.route("/api/logs", methods=["GET"])
@token_auth.login_required
def get_logs():
    """
    Get the user that sends the request via his token and then return an ApiResult for his logs
    logs = g.current_user.logs
    return ApiResult({"logs": LogSchema(many=True).dump(logs).data})
    """
    logs = Log.query.all()
    return ApiResult({"logs": LogSchema(many=True).dump(logs)})


# READ LOG
@bp.route("/api/logs/<int:id>", methods=["GET"])
@token_auth.login_required
def get_log(id):
    log = Log.query.get(id)
    if not log:
        raise ApiException("Log <" + str(id) + "> not in DB")
    return ApiResult(LogSchema().dump(log))


# UPDATE LOG

# DELETE LOG
