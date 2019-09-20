from flask import g, request

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import token_auth
from app.models import Log, LogSchema


# CREATE LOG
@bp.route("/api/logs", methods=["POST"])
@token_auth.login_required
def create_log():
    json_data = request.get_json() or {}
    try:
        log = LogSchema().load(json_data)
    except Exception as e:
        raise ApiException(str(e))
    existing_log = Log.query.filter_by(owner=g.current_user, title=log.title).first()
    if existing_log:
        raise ApiException(
            f'Your {existing_log} is titled "{existing_log.title}" already.'
        )
    log.owner = g.current_user
    db.session.add(log)
    db.session.commit()
    return ApiResult({"message": f"{log} created."}, 201)


# READ ALL LOGS
@bp.route("/api/logs", methods=["GET"])
@token_auth.login_required
def get_logs():
    logs = Log.query.filter_by(owner=g.current_user).all()
    return ApiResult({"logs": LogSchema(many=True).dump(logs)})


# READ LOG
@bp.route("/api/logs/<int:id>", methods=["GET"])
@token_auth.login_required
def get_log(id):
    try:
        log = Log.query.filter_by(owner=g.current_user, id=id).one()
    except Exception as e:
        raise ApiException(f"<Log {str(id)}> not available.", 404)
    return ApiResult(LogSchema().dump(log))


# UPDATE LOG
@bp.route("/api/logs/<int:id>", methods=["PUT"])
@token_auth.login_required
def update_log(id):
    json_data = request.get_json() or {}
    try:
        log = Log.query.filter_by(owner=g.current_user, id=id).one()
    except Exception as e:
        raise ApiException(f"<Log {id}> not found in your logs.", 404)
    try:
        LogSchema().load(json_data, instance=log, session=db.session)
    except Exception as e:
        raise ApiException(str(e))
    # with dump_only = ('id',) the following is no longer necessary
    # if log.id != id:
    #     db.session.rollback()
    #     raise ApiException(f"You're not allowed to change the id of {log}.", 403)
    if log.owner != g.current_user:
        db.session.rollback()
        raise ApiException(f"You are not allowed to update the owner for {log}.", 403)
    db.session.commit()
    return ApiResult({"message": f"{log} updated."})


# DELETE LOG
@bp.route("/api/logs/<int:id>", methods=["DELETE"])
@token_auth.login_required
def delete_log(id):
    try:
        log = Log.query.filter_by(owner=g.current_user, id=id).one()
    except Exception as e:
        raise ApiException(f"<Log {id}> not found in your logs.", 404)
    db.session.delete(log)
    db.session.commit()
    return ApiResult({"message": f"{log} deleted."})
