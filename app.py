from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
#TODO: ONLY ALLOW UNIQUE USERNAMES
app = Flask(__name__)
app.secret_key = 'mysecretkey'

# Replace the URI with your own values
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

#db.create_all()
current_user = User()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if email or username is already taken
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already taken', 'error')
            return redirect('/register')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already taken', 'error')
            return redirect('/register')

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, email=email)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password, password):
            session['username'] = username

            return redirect('/dashboard')
        else:
            return 'Invalid username or password'
    else:
        return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('app/dashboard.html')
    else:
        return redirect('/login')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if request.method == 'POST':
            user_form = request.form['username']
            email_form = request.form['email']
            user.username = user_form
            user.email = email_form
            session['username'] = user_form
            db.session.commit()

        return render_template('app/profile/profile.html', current_user=user)
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'username' in session:
        username = session['username']
        user = User.query.filter_by(username=username).first()
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            # Get the current user based on the logged in user


            # Check if the current password provided matches the user's password
            if not check_password_hash(user.password, current_password):
                flash('Current password is incorrect. Please try again.', 'error')
                return redirect('/change_password')

            # Check if the new password and confirm password match
            if new_password != confirm_password:
                flash('New password and confirm password do not match. Please try again.', 'error')
                return redirect('/change_password')

            # Update the user's password with the new password
            user.password = generate_password_hash(new_password)
            db.session.commit()

            flash('Password successfully changed.', 'success')
            return redirect('/dashboard')

        return render_template('app/profile/change_password.html')

        if request.method == 'POST':
            user_form = request.form['username']
            email_form = request.form['email']
            user.username = user_form
            user.email = email_form
            session['username'] = user_form
            db.session.commit()

        return render_template('app/profile/change_password.html', current_user=user)
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
