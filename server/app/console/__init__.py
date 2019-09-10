from flask import Blueprint

bp = Blueprint('console', __name__)

from app.console import routes