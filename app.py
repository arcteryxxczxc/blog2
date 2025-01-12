from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mirka2003@localhost/blog_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/images'

db = SQLAlchemy(app)

# Models
friendships = db.Table('friendships',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
                       )


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    profile_picture = db.Column(db.String(100), default='default.jpg')
    friends = db.relationship('User', secondary=friendships,
                              primaryjoin=id == friendships.c.user_id,
                              secondaryjoin=id == friendships.c.friend_id,
                              backref='friends_back')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts')


# Routes
@app.route('/')
def home():
    if 'user_id' not in session:
        flash('Please login to see the main page.', 'info')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    # Friends' posts
    friends_posts = Post.query.join(User).filter(User.id.in_(
        [friend.id for friend in user.friends])).all()

    # Popular posts (for example, last 5 posts)
    popular_posts = Post.query.order_by(Post.id.desc()).limit(5).all()

    return render_template('home.html', friends_posts=friends_posts, popular_posts=popular_posts)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'], method='pbkdf2:sha256')

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration was successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))

        session['user_id'] = user.id
        flash('Login completed successfully.', 'success')
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    posts = Post.query.filter_by(user_id=user.id).all()
    friends = user.friends
    return render_template('profile.html', user=user, posts=posts, friends=friends)


@app.route('/profile/posts/add', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        flash('Please log in first', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = Post(title=title, content=content, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        flash('Post added successfully.', 'success')
        return redirect(url_for('profile'))

    return render_template('add_post.html')


@app.route('/profile/friends/add', methods=['GET', 'POST'])
def add_friend():
    if 'user_id' not in session:
        flash('Please login to add a friend.', 'info')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        search_name = request.form['search_name']
        potential_friends = User.query.filter(User.name.ilike(f"%{search_name}%"), User.id != user.id).all()
        return render_template('add_friend.html', user=user, potential_friends=potential_friends)

    return render_template('add_friend.html', user=user, potential_friends=[])


@app.route('/profile/friends/add/<int:friend_id>')
def add_friend_by_id(friend_id):
    if 'user_id' not in session:
        flash('Please login to add a friend.', 'info')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    friend = User.query.get(friend_id)

    if friend not in user.friends:
        user.friends.append(friend)
        db.session.commit()
        flash(f'User {friend.name} added as a friend.', 'success')
    else:
        flash(f'User {friend.name} already your friend.', 'info')

    return redirect(url_for('profile'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You are logged out', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
