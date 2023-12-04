from flask import render_template, request, Blueprint, abort
from flask_login import current_user, login_required
from main.models import Post

main1 = Blueprint('main', __name__)

@main1.route("/")
@main1.route("/home")
def home():
    return render_template('home.html')

@main1.route("/admin_announcement")
@login_required
def admin_announcement():
    if current_user.id == 1:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        #SELECT * FROM Post ORDER BY date_posted DESC LIMIT 5 OFFSET (page - 1) * 5;
        return render_template('admin_announcement.html', title='Announcement', posts=posts)
    else:
        abort(403)

@main1.route("/customer_announcement")
@login_required
def customer_announcement():
    if current_user.is_authenticated:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
        #SELECT * FROM Post ORDER BY date_posted DESC LIMIT 5 OFFSET (page - 1) * 5;
        return render_template('customer_announcement.html', title='Announcement', posts=posts)
    
@main1.route("/appointment")
@login_required
def appointment():
    return render_template('appointment.html', title='Appointment')


