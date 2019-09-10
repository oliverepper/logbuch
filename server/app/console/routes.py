from app.console import bp


@bp.route("/")
def index():
    return "Willkommen bei Logbuch"


@bp.route("/register", methods=["GET", "POST"])
def register():
    pass


@bp.route("/complete_registration/<token>", methods=["GET","POST"])
def complete_registration(token):
    pass