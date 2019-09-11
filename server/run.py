from app import create_app, cli, db
from app.models import User, Log


app = create_app()
cli.register_app(app)

@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Log": Log}
