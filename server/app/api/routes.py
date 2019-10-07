import logging

from flask import g, jsonify, request
from flask_cors import cross_origin

from app import ApiException, ApiResult, db
from app.api import bp
from app.api.auth import basic_auth, token_auth
from app.models import Entry, EntrySchema, Log, LogSchema

from . import logs, entries


# GET TOKEN FOR USER
@bp.route("/token", methods=["GET"])
@basic_auth.login_required
def get_token():
    token = g.current_user.api_token
    # FIXME: token can be null, here
    if not token.is_valid:
        g.current_user.update_api_token()
        db.session.commit()
        token = g.current_user.api_token
    return ApiResult({"token": token.value})
