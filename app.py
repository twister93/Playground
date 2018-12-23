import os
import random
from PIL import Image
from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, request
from flask import request, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required


app = Flask(__name__)
app.config['SECRET_KEY']="AAAAB3NzaC1yc2EAAAABJQAAAgEAhHGjeoeQ09HKzCLLSSFQe/CnE7Yihyqkw7MFE2lv/PSNakeNp9kWeSItb+9gIUMqIq8wUGuTb/TcWXth+5/EYOvcjjpzr574YGrJ81tnHJxNEbVxDGEZzCUvGvEWVOsf7EA1Gm8zf49ECf15BYNDtE8KO4zxUBsJUjhYzYwoNBgOCukmEnBiyug4dP7VuJTP+onswS7+FBumLqxyQjci4YnfAijcidV2mF7j+Hc9yfsRjob8BcF6kB+7T0tfPuUhNs0zkaiVZBXtxF60r9LuvwM5YyGkL+22oTDimoExnGdIss7Z9kNIoL4nSancZTTw6/B56Z4nNGc5pYBqtHsJaFYBnWcS7uwUUWFSJE6NmXKyZMNog00bfwIGkI+fdbnUrRxPVI0aig8aRxpY79M5ejauRpaJNeHnrO092XsOk6Cox6fX+Cr1lewIsAkEKqCnjkSMFmWnqtAFP2ztSTfHrqUfZrmxcZ9MDrOcPRhcWjneogWt3Rwnu3PzAvevNvIBgMYrpELE2+fPXg+ZFhRuJOFuENwVG5woHkC6UE0ztskhbHGXO73uh5ftMLLPEJEBYlM0tbwrzPYJZ7aUFT5PZJqhpWa+Y3GjJ7Xky4/xA+zYcF6q0vQMImkVYbEUB7Y+E3oV8Jz0YysjHZFSmckh1M8SE8A3ON+ZtRhopCW0CDk="
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #eliminar warning
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

#--------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



#--------------------------------------------------------
class User(db.Model, UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    phone=db.Column(db.String(20),unique=True,nullable=True)
    email=db.Column(db.String(20),unique=True,nullable=True)
    name=db.Column(db.String(10),nullable=True)
    password=db.Column(db.String(30),nullable=True)
    image_file = db.Column(db.String(20),nullable=False,default='default.png')
    games = db.relationship('Games', backref='creator', lazy=True)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'),nullable=True)

    def __repr__(self):
        return "<User email %r>" % self.email


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100),unique=True,nullable=False)
    date_game = db.Column(db.DateTime,nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text,nullable=False)
    sport = db.Column(db.String(100),unique=True,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=True)
    Location = db.Column(db.String(100),nullable=False, default='Parco Ruffini, Viale Leonardo Bistolfi, 10141 Torino TO')

    def __repr__(self):
        return "<Game Title %r>" % self.title



class Role(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10),nullable=True)
    users=db.relationship('User',backref='role',lazy=True)

    def __repr__(self):
        return "<Role %r>" % self.name

from forms import SignUpname, LoginForm, ContactForm, UpdateAccountForm, GameForm


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]


@app.before_first_request
def setup_db():
    db.create_all()

#---------------------------------------------------------------------

@app.route('/')
@app.route('/home')
def main():
    return render_template('index.html', title="Welcome Page")

#---------------------------------------------------------------------

@app.route("/signup",methods=['POST','GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('soccer'))
    formpage=SignUpname()
    if formpage.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(formpage.password.data)
        user_reg=User(phone=formpage.phone.data,
                    email= formpage.email.data,
                    name=formpage.name.data,
                    password= hashed_password,
                    role_id=1)# role_id = Role.query.find_by(name='Student').first()
        db.session.add(user_reg)
        db.session.commit()
        flash('Your account has been created!! you are now able to login!!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', formpage = formpage , title='Sign Up')

@app.route("/signin",methods=['POST','GET'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('soccer'))
    formpage=LoginForm()
    if formpage.validate_on_submit(): #Form processing work
        # TODO do query db for login or use login from flask
        user=User.query.filter_by(email=formpage.email.data).first()
        if user and bcrypt.check_password_hash(user.password,formpage.password.data):
            login_user(user,remember = True)
            next_page = request.args.get('next')
            flash('Login requested for user {}'.format(formpage.email.data), 'success')
            #session['email']=formpage.email.data
            return redirect(next_page) if next_page else redirect(url_for('soccer')) #turnary codition
        else:
            flash('Login Unsuccesful. Please check email and password','danger')
    return render_template('signin.html', formpage = formpage, email=session.get('email',False) , title='Sign In')

@app.route('/logout')
def logout():
    logout_user()
    #session.clear()
    return render_template('index.html')
#---------------------------------------------------------------------

@app.route('/ContactUs')
def ContactUs():
    formpage=ContactForm()
    return render_template('contact.html', formpage=formpage, title='Contact Us')

@app.route('/soccer')
@login_required
def soccer():
    return render_template('soccer.html', title='Soccer', posts=posts)

@app.route('/soccer/new_game',methods=['POST','GET'])
@login_required
def new_game():
    formpage = GameForm()
    if formpage.validate_on_submit():
        flash('Your post has been created!','success')
        return redirect(url_for('soccer'))
    return render_template('new_soccer_game.html', title='Create Soccer Game', formpage = formpage)

@app.route('/basket')
@login_required
def basket():
    return render_template('basket.html', title='Basket')

@app.route('/tennis')
@login_required
def tennis():
    return render_template('tennis.html', title='Tenis')

def save_picture(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    random_name = random.randint(1, 9999999999999999)#change to unique name
    picture_fn = str(random_name) + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)

    #resize image
    output_size = (230,230)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/profile',methods=['POST','GET'])
@login_required
def profile():
    formpage = UpdateAccountForm()
    if formpage.validate_on_submit():
        if formpage.picture.data:#save profile picture
            picture_file = save_picture(formpage.picture.data)
            current_user.image_file = picture_file
        current_user.name = formpage.name.data
        current_user.email = formpage.email.data
        current_user.phone = formpage.phone.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        formpage.name.data = current_user.name
        formpage.email.data = current_user.email
        formpage.phone.data = current_user.phone
    image_file= url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file , formpage=formpage)


if __name__ == '__main__':
    app.run(debug=True)