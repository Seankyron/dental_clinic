from flask import render_template, request, Blueprint
from flask_login import current_user, login_required
from main.models import Post

main1 = Blueprint('main', __name__)

@main1.route("/")
@main1.route("/home")
def home():
    return render_template('home.html')

@main1.route("/announcement")
@login_required
def announcement():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        return render_template('announcement.html', title='Announcement', posts=posts)

@main1.route("/appointment")
@login_required
def appointment():
    return render_template('appointment.html', title='Appointment')

@main1.route("/about")
def about():
    return render_template('about.html', title='About')

@main1.route("/treatment")
def treatment():
    return render_template('treatment.html', title='Treatments')

