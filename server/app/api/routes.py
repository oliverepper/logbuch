from flask import jsonify
from flask_cors import cross_origin

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import token_auth
from app.models import Log, LogSchema


# READ ALL
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


@bp.route('/api/logs/<int:id>', methods=['GET'])
def get_log(id):
    log = Log.query.get(id)
    if not log:
        raise ApiException("Log <" + str(id) + "> not in DB")
    return ApiResult(LogSchema().dump(log))
