from flask import g
from flask_httpauth import HTTPTokenAuth

from app import ApiException
from app.models import ApiToken

token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(token) -> bool:
    api_token = ApiToken.query.filter_by(value=token).first()
    g.current_user = api_token.owner if api_token else None
    if g.current_user and not api_token.is_valid:
        raise ApiException(f'Hello {g.current_user} please update your api_token.', 401)
    return g.current_user is not None


@token_auth.error_handler
def token_auth_error():
    raise ApiException('Token not valid')
