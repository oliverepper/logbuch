from app import cli, create_app, db
from app.models import ApiToken, Entry, Log, Membership, MembershipType, User

app = create_app()
cli.register_app(app)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "ApiToken": ApiToken,
        "Log": Log,
        "Entry": Entry,
        "Membership": Membership,
        "MembershipType": MembershipType,
    }
