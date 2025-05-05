from blog.models import User, Post
from blog import create_app, db

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Post': Post,
    }

if __name__ == "__main__":
    app.run(debug=True)

