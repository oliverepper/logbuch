from flask import Blueprint

bp = Blueprint('message_service', __name__)

from app.message_service import routes