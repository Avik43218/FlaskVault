from flask import Blueprint, request, render_template
from blog.models import Post
from blog import limiter

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
@limiter.exempt
def home():

    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=5)

    print(type(posts))

    return render_template("home.html", posts=posts)


@main.route("/about")
@limiter.exempt
def about():

    return render_template("about.html", title='About')
