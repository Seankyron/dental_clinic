from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from main import db
from main.models import Post
from main.posts.forms import PostForm

posts = Blueprint('posts', __name__)

@posts.route("/new_post", methods=['GET', 'POST'])
@login_required
def new_post():
    #if statement para admin lang ang makakapag-post
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        '''
        "INSERT INTO Post (title, content, user_id) VALUES (%s, %s, %s)"
        values = (form.title.data, form.content.data, current_user.id)
        '''
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.new_post'))
    return render_template('new_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id) #"SELECT * FROM Post WHERE id = %s", (post_id,)
    return render_template('post.html', title=post.title, post=post)

@posts.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id) #"SELECT * FROM Post WHERE id = %s", (post_id,)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        '''"UPDATE Post SET title = %s, content = %s WHERE id = %s",
                       (form.title.data, form.content.data, post_id)'''
        db.session.commit() 
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('new_post.html', title='Update Post',
                           form=form, legend='Update Post')


@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id) #"SELECT * FROM Post WHERE id = %s", (post_id,)
    if post.author != current_user:
        abort(403)
    db.session.delete(post) #"DELETE FROM Post WHERE id = %s", (post_id,)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.admin_announcement'))


