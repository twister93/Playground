import os
import random
from PIL import Image
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import Flask, render_template, url_for, flash, redirect, request, abort, session, jsonify
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_mail import Mail, Message

from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from flask_socketio import SocketIO

# ---------------    DATABASE CONFIG SECTION ------------
app = Flask(__name__)
app.config[
    'SECRET_KEY'] = "AAAAB3NzaC1yc2EAAAABJQAAAgEAhHGjeoeQ09HKzCLLSSFQe/CnE7Yihyqkw7MFE2lv/PSNakeNp9kWeSItb+9gIUMqIq8wUGuTb/TcWXth+5/EYOvcjjpzr574YGrJ81tnHJxNEbVxDGEZzCUvGvEWVOsf7EA1Gm8zf49ECf15BYNDtE8KO4zxUBsJUjhYzYwoNBgOCukmEnBiyug4dP7VuJTP+onswS7+FBumLqxyQjci4YnfAijcidV2mF7j+Hc9yfsRjob8BcF6kB+7T0tfPuUhNs0zkaiVZBXtxF60r9LuvwM5YyGkL+22oTDimoExnGdIss7Z9kNIoL4nSancZTTw6/B56Z4nNGc5pYBqtHsJaFYBnWcS7uwUUWFSJE6NmXKyZMNog00bfwIGkI+fdbnUrRxPVI0aig8aRxpY79M5ejauRpaJNeHnrO092XsOk6Cox6fX+Cr1lewIsAkEKqCnjkSMFmWnqtAFP2ztSTfHrqUfZrmxcZ9MDrOcPRhcWjneogWt3Rwnu3PzAvevNvIBgMYrpELE2+fPXg+ZFhRuJOFuENwVG5woHkC6UE0ztskhbHGXO73uh5ftMLLPEJEBYlM0tbwrzPYJZ7aUFT5PZJqhpWa+Y3GjJ7Xky4/xA+zYcF6q0vQMImkVYbEUB7Y+E3oV8Jz0YysjHZFSmckh1M8SE8A3ON+ZtRhopCW0CDk="
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # eliminar warning
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# -------------- EMAIL SERVER SECTION --------------
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'playground.assistance@gmail.com'
app.config['MAIL_PASSWORD'] = 'playground(001)'

mail = Mail(app)  # inicialization

#--------------- GOOGLE MAPS API----------
GoogleMaps(app, key="AIzaSyDgqIyx02QRdO5Y42dyejOTC7AejFxRJxE")

#---- Socket IO initialization -----
socketio = SocketIO(app)

# --------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ----------------   User Model ----------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    email = db.Column(db.String(20), unique=True, nullable=True)
    name = db.Column(db.String(10), nullable=True)
    password = db.Column(db.String(30), nullable=True)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')
    games = db.relationship('Games', backref='creator', lazy=True)
    teams = db.relationship('Teams', backref='begginer', lazy=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return "<User email %r>" % self.email


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    members = db.Column(db.Text,nullable=True,)
    vacant = db.Column(db.Integer, nullable=False)
    sport = db.Column(db.String(100), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    location = db.Column(db.String(100), nullable=False)
    slot = db.Column(db.String(100), nullable=True)
    slot_id = db.Column(db.Integer, nullable=True)
    price = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return "<Game Title %r>" % self.title

class Courts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    sport = db.Column(db.String(100),nullable=True)

    def __repr__(self):
        return "<Court Name %r>" % self.name

class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.Text, nullable=False)
    members = db.Column(db.Text,nullable=True,)
    players_number = db.Column(db.Integer, nullable=False)
    vacant = db.Column(db.Integer, nullable=False)
    sport = db.Column(db.String(100), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return "<Team Name %r>" % self.name

class Slots(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court_number = db.Column(db.Integer,unique=False, nullable=False)
    players_number = db.Column(db.Integer,unique=False, nullable=False)
    slot_date_time = db.Column(db.String(100), unique=False, nullable=False)
    availability = db.Column(db.String(5), unique=False, nullable=False)
    court = db.Column(db.String(100), nullable=True)
    price = db.Column(db.String(50), unique=False, nullable=False)

    def __repr__(self):
        return "<Slot %r>" % self.slot_date_time

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=True)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return "<Role %r>" % self.name

from forms import SignUpname, LoginForm, ContactForm, UpdateAccountForm, GameForm, RequestResetForm, ResetPasswordForm, \
                    JoinForm, DeleteForm, TeamForm, LeaveForm, MessageForm

@app.before_first_request
def setup_db():
    db.create_all()

# ---------------------------------------------------------------------
@app.route('/')
@app.route('/home')
def main():
    return render_template('index.html', title="Welcome Page")


# ---------------------------------------------------------------------

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('soccer'))
    formpage = SignUpname()
    if formpage.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(formpage.password.data)
        user_reg = User(phone=formpage.phone.data,
                        email=formpage.email.data,
                        name=formpage.name.data,
                        password=hashed_password,
                        role_id=1)
        db.session.add(user_reg)
        db.session.commit()
        flash('Your account has been created!! you are now able to login!!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', formpage=formpage, title='Sign Up')


@app.route("/signin", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('soccer'))
    formpage = LoginForm()
    if formpage.validate_on_submit():  # Form processing work
        # TODO do query db for login or use login from flask
        user = User.query.filter_by(email=formpage.email.data).first()
        if user and bcrypt.check_password_hash(user.password, formpage.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash('Login requested for user {}'.format(formpage.email.data), 'success')
            # session['email']=formpage.email.data
            return redirect(next_page) if next_page else redirect(url_for('soccer'))  # turnary codition
        else:
            flash('Login Unsuccesful. Please check email and password', 'danger')
    return render_template('signin.html', formpage=formpage, email=session.get('email', False), title='Sign In')


@app.route('/logout')
def logout():
    logout_user()
    # session.clear()
    return render_template('index.html')


# ---------------------------------------------------------------------
@app.route('/shops')
def shops():
    return render_template('shops.html', title='Sportive Shops')


@app.route('/AboutUs')
def about():
    return render_template('about.html', title='About Us')


# -------------------- CONTACT US EMAIL PAGE ------------------------------------
def send_mail(name, email, message):
    msg = Message('Contact Us Message from ' + name, sender=email, recipients=[app.config['MAIL_USERNAME']])
    msg.body = '''Message from: ''' + email + '''
Message Content:

''' + message
    mail.send(msg)

@app.route('/ContactUs', methods=['POST', 'GET'])
def ContactUs():
    formpage = ContactForm()
    if formpage.validate_on_submit():
        name = formpage.name.data
        email = formpage.email.data
        msg = formpage.message.data
        send_mail(name, email, msg)
        flash('An email has been send to our Team, we will contact you ASAP', 'info')
        return redirect(url_for('main'))
    return render_template('contact.html', formpage=formpage, title='Contact Us')

# ------------------- SOCCER GAME ---------------------------------------------------
@app.route('/soccer')
@login_required
def soccer():
    teams = Teams.query.filter_by(sport='soccer').all()
    games = Games.query.filter_by(sport='soccer').all()
    return render_template('soccer.html', title='Soccer', games=games, teams=teams)

@app.route('/soccer/new_game', methods=['POST', 'GET'])
@login_required
def new_game():
    formpage = GameForm()
    formpage.court.choices=[(court.name,court.name+' - Address: '+court.location) for court in Courts.query.filter_by(sport='soccer').all()]
    formpage.slot.choices=[(slot.id,'Court No: '+str(slot.court_number)+' | Schedule at: '+slot.slot_date_time+ ' | Max Players: '
                            +str(slot.players_number)+' | Price : '+slot.price)
                           for slot in Slots.query.filter_by(court='Circolo della Stampa - Sporting A.S.D.', availability='True').all()]
    if request.method == 'POST':
        try:
            slot = Slots.query.filter_by(id=formpage.slot.data).first()
            slot.availability='False'
        except:
            flash('There is no slots available to book!!','success')

        else:
            vacant = slot.players_number - 1
            if formpage.team.data==True:
                vacant=0
            game = Games(title=formpage.title.data,
                         description=formpage.description.data,
                         members=current_user.name+' Cel: '+current_user.phone+' ',
                         vacant=vacant,
                         sport='soccer',
                         creator=current_user,
                         location=formpage.court.data,
                         slot='Court #: '+str(slot.court_number)+'| at '+slot.slot_date_time+'| for: '+str(slot.players_number)+' players',
                         slot_id=slot.id,
                         price=slot.price)
            db.session.add(game)
            db.session.commit()
            flash('Your post has been created!', 'success')
        return redirect(url_for('soccer'))
    #Map handler
    soccermap = Map(
        identifier="view-side",
        lat=45.0728612,
        lng=7.6474516,
        zoom=12,
        markers=[
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 45.0396017,
             'lng': 7.6452646,
             'infobox': "Circolo della Stampa - Sporting A.S.D."

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 45.0521902,
             'lng': 7.6101512,
             'infobox': "Poligru L'oasi dello sport"

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
             'lat': 45.0700943,
             'lng': 7.651680199999987,
             'infobox': "Nuova Golden Goal"

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
             'lat': 45.0699097,
             'lng': 7.655949400000054,
             'infobox': "Cit Turin LDE"

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             'lat': 45.068541,
             'lng': 7.62848699999995,
             'infobox': "Pozzomaina S.R.L. S.S.D."

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
             'lat': 45.0601674,
             'lng': 7.644224300000019,
             'infobox': "Centro sportivo Robillant"
            }
        ]
    )
    return render_template('new_soccer_game.html', title='Create Soccer Game', formpage=formpage, soccermap=soccermap)

@app.route('/soccer/new_game/slots/<court>')
@login_required
def slot(court):
    slots = Slots.query.filter_by(court=court,availability='True').all()

    slotArray = []

    for slot in slots:
        slotObj = {}
        slotObj['id'] =slot.id
        slotObj['slot_date_time'] = 'Court #: '+str(slot.court_number)+' at '+slot.slot_date_time+ ' Players Numer: '+str(slot.players_number)
        slotArray.append(slotObj)
    return jsonify({'slots' : slotArray})

@app.route('/soccer/<int:game_id>s', methods=['POST', 'GET'])
@login_required
def game(game_id):
    game = Games.query.get_or_404(game_id)
    flag = 1
    formpage = None
    if game.vacant!=0:
        if game.creator != current_user:
            flag = 0
            if current_user.phone in game.members:
                formpage = LeaveForm()
                if formpage.validate_on_submit():
                    toreplace =' | '+current_user.name+' Cel: '+current_user.phone
                    members = game.members.replace(toreplace,'')
                    game.members = members
                    new_vacant = game.vacant +1
                    game.vacant = new_vacant
                    db.session.commit()
                    flash('You have leave!!!', 'success')
                    return redirect(url_for('soccer'))
            else:
                formpage = JoinForm()
                if formpage.validate_on_submit():
                    members = game.members +' | '+current_user.name+' Cel: '+current_user.phone
                    game.members = members
                    new_vacant = game.vacant -1
                    game.vacant = new_vacant
                    db.session.commit()
                    flash('You have join the team!!!', 'success')
                    return redirect(url_for('soccer'))
    if game.creator == current_user:
        flag=0
        formpage = DeleteForm()
        if formpage.validate_on_submit():
            slot = Slots.query.get_or_404(game.slot_id)
            slot.availability = 'True'
            flash('The game has been deleted!!!','success')
            db.session.delete(game)
            db.session.commit()
            return redirect(url_for('soccer'))
    return render_template('game.html', title='Update Game', formpage=formpage, flag = flag, game=game)  # title=game.title
# ------------------- BASKET GAME ---------------------------------------------------
@app.route('/basket')
@login_required
def basket():
    games = Games.query.filter_by(sport='basket').all()
    teams = Teams.query.filter_by(sport='basket').all()
    return render_template('basket.html', title='Basket', games=games, teams=teams)


@app.route('/basket/new_basket_game', methods=['POST', 'GET'])
@login_required
def new_game_basket():
    formpage = GameForm()
    formpage.court.choices=[(court.name,court.name+' - Address: '+court.location) for court in Courts.query.filter_by(sport='basket').all()]
    formpage.slot.choices=[(slot.id,'Court No: '+str(slot.court_number)+' | Schedule at: '+slot.slot_date_time+ ' | Max Players: '
                            +str(slot.players_number)+' | Price : '+slot.price)
                           for slot in Slots.query.filter_by(court='Circolo della Stampa - Sporting A.S.D. - Basket', availability='True').all()]
    if request.method == 'POST':
        try:
            slot = Slots.query.filter_by(id=formpage.slot.data).first()
            slot.availability='False'
        except:
            flash('There is no slot to book!!','success')

        else:
            vacant = slot.players_number - 1
            if formpage.team.data==True:
                vacant=0
            game = Games(title=formpage.title.data,
                         description=formpage.description.data,
                         members=current_user.name+' Cel: '+current_user.phone+' ',
                         vacant=vacant,
                         sport='basket',
                         creator=current_user,
                         location=formpage.court.data,
                         slot='Court #: '+str(slot.court_number)+'| at '+slot.slot_date_time+'| for: '+str(slot.players_number)+' players',
                         slot_id=slot.id,
                         price=slot.price)
            db.session.add(game)
            db.session.commit()
            flash('Your game has been created!', 'success')
        return redirect(url_for('basket'))
    #Map handler
    basketmap = Map(
        identifier="view-side",
        lat=45.0728612,
        lng=7.6474516,
        zoom=12,
        markers=[
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 45.0396017,
             'lng': 7.6452646,
             'infobox': "Circolo della Stampa - Sporting A.S.D. - Basket"

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
             'lat': 45.0736286,
             'lng': 7.631213300000013,
             'infobox': "Basket court"

            },
            {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
             'lat': 45.0601674,
             'lng': 7.644224300000019,
             'infobox': "Centro sportivo Robillant - Basket"
            }
        ]
    )
    return render_template('new_basket_game.html', title='Create Basket Game', formpage=formpage, basketmap=basketmap)


@app.route('/basket/new_basket_game/slots/<court>')
@login_required
def slot_b(court):
    slots = Slots.query.filter_by(court=court,availability='True').all()

    slotArray = []

    for slot in slots:
        slotObj = {}
        slotObj['id'] =slot.id
        slotObj['slot_date_time'] = 'Court #: '+str(slot.court_number)+' at '+slot.slot_date_time+ ' Players Numer: '+str(slot.players_number)
        slotArray.append(slotObj)
    return jsonify({'slots' : slotArray})

@app.route('/basket/<int:game_id>b', methods=['POST', 'GET'])
@login_required
def game_b(game_id):
    game = Games.query.get_or_404(game_id)
    formpage = None
    flag = 1
    if game.vacant!=0:
        if game.creator != current_user:
            flag = 0
            if current_user.phone in game.members:
                formpage = LeaveForm()
                if formpage.validate_on_submit():
                    toreplace = ' | ' + current_user.name + ' Cel: ' + current_user.phone
                    members = game.members.replace(toreplace, '')
                    game.members = members
                    new_vacant = game.vacant + 1
                    game.vacant = new_vacant
                    db.session.commit()
                    flash('You have leave!!!', 'success')
                    return redirect(url_for('basket'))
            else:
                formpage = JoinForm()
                if formpage.validate_on_submit():
                    members = game.members + ' | ' + current_user.name + ' Cel: ' + current_user.phone
                    game.members = members
                    new_vacant = game.vacant - 1
                    game.vacant = new_vacant
                    db.session.commit()
                    flash('You have join the team!!!', 'success')
                    return redirect(url_for('basket'))
    if game.creator == current_user:
        flag=0
        formpage = DeleteForm()
        if formpage.validate_on_submit():
            slot = Slots.query.get_or_404(game.slot_id)
            slot.availability = 'True'
            flash('The game has been deleted!!!','success')
            db.session.delete(game)
            db.session.commit()
            return redirect(url_for('basket'))
    return render_template('game.html', title='Update Game', formpage=formpage, game=game,flag=flag)

# ------------------- TENNIS GAME ---------------------------------------------------

@app.route('/tennis')
@login_required
def tennis():
    teams = Teams.query.filter_by(sport='tennis').all()
    games = Games.query.filter_by(sport='tennis').all()
    return render_template('tennis.html', title='Tennis', games=games, teams=teams)

@app.route('/tennis/new_tennis_game', methods=['POST', 'GET'])
@login_required
def new_game_tennis():
    formpage = GameForm()
    formpage.court.choices=[(court.name,court.name+' - Address: '+court.location) for court in Courts.query.filter_by(sport='tennis').all()]
    formpage.slot.choices=[(slot.id,'Court No: '+str(slot.court_number)+' | Schedule at: '+slot.slot_date_time+ ' | Max Players: '
                            +str(slot.players_number)+' | Price : '+slot.price)
                           for slot in Slots.query.filter_by(court='Circolo della Stampa - Sporting A.S.D. - Tennis', availability='True').all()]#Ojo debe ir el primero siempre
    if request.method == 'POST':
        try:
            slot = Slots.query.filter_by(id=formpage.slot.data).first()
            slot.availability='False'
        except:
            flash('There is no slot to book!!','success')

        else:
            vacant = slot.players_number - 1
            if formpage.team.data==True:
                vacant=0
            game = Games(title=formpage.title.data,
                         description=formpage.description.data,
                         members=current_user.name+' Cel: '+current_user.phone+' ',
                         vacant=vacant,
                         sport='tennis',
                         creator=current_user,
                         location=formpage.court.data,
                         slot='Court #: '+str(slot.court_number)+'| at '+slot.slot_date_time+'| for: '+str(slot.players_number)+' players',
                         slot_id=slot.id,
                         price=slot.price)
            db.session.add(game)
            db.session.commit()
            flash('Your post has been created!', 'success')
        return redirect(url_for('tennis'))
    #Map handler
    tennismap = Map(
        identifier="view-side",
        lat=45.0728612,
        lng=7.6474516,
        zoom=12,
        markers=[
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat': 45.0396017,
                'lng': 7.6452646,
                'infobox': "Circolo della Stampa - Sporting A.S.D."

            },
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
                'lat': 45.0521902,
                'lng': 7.6101512,
                'infobox': "Poligru L'oasi dello sport"

            },
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                'lat': 45.08472099999999,
                'lng': 7.6406868999999915,
                'infobox': "Nord Tennis Sport Club"

            },
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/purple-dot.png',
                'lat': 45.0601674,
                'lng': 7.644224300000019,
                'infobox': "Centro sportivo Robillant"
            }
        ]
    )
    return render_template('new_tennis_game.html', title='Create Tennis Game', formpage=formpage, tennismap=tennismap)


@app.route('/tennis/new_tennis_game/slots/<court>')
@login_required
def slot_t(court):
    slots = Slots.query.filter_by(court=court,availability='True').all()

    slotArray = []

    for slot in slots:
        slotObj = {}
        slotObj['id'] =slot.id
        slotObj['slot_date_time'] = 'Court #: '+str(slot.court_number)+' at '+slot.slot_date_time+ ' Players Numer: '+str(slot.players_number)
        slotArray.append(slotObj)
    return jsonify({'slots' : slotArray})

@app.route('/tennis/<int:game_id>t', methods=['POST', 'GET'])
@login_required
def game_t(game_id):
    game = Games.query.get_or_404(game_id)
    flag = 1
    formpage = None
    if game.vacant!=0:
        if game.creator != current_user:
            flag = 0
            if current_user.phone in game.members:
                formpage = LeaveForm()
                if formpage.validate_on_submit():
                    toreplace = ' | ' + current_user.name + ' Cel: ' + current_user.phone
                    members = game.members.replace(toreplace, '')
                    game.members = members
                    new_vacant = game.vacant + 1
                    game.vacant = new_vacant
                    db.session.commit()
                    flash('You have leave!!!', 'success')
                    return redirect(url_for('tennis'))
            else:
                formpage = JoinForm()
                if formpage.validate_on_submit():
                    members = game.members + ' | ' + current_user.name + ' Cel: ' + current_user.phone
                    game.members = members
                    new_vacant = game.vacant - 1
                    game.vacant = new_vacant
                    db.session.commit()
                    flash('You have join the team!!!', 'success')
                    return redirect(url_for('tennis'))
    if game.creator == current_user:
        flag=0
        formpage = DeleteForm()
        if formpage.validate_on_submit():
            slot = Slots.query.get_or_404(game.slot_id)
            slot.availability = 'True'
            flash('The game has been deleted!!!','success')
            db.session.delete(game)
            db.session.commit()
            return redirect(url_for('tennis'))
    return render_template('game.html', title='Update Game', formpage=formpage, flag = flag, game=game)

# --------------------------------------------------------------------------------------------------------

# -----------------------CREATE A TEAM SECTION--------------------------------------------------
@app.route('/new_team', methods=['POST', 'GET'])
@login_required
def new_team():
    formpage = TeamForm()
    if formpage.validate_on_submit():
        sport = formpage.sport.data
        team = Teams(name=formpage.name.data,
                     description=formpage.description.data,
                     members=current_user.name+' Cel: '+current_user.phone+' ',
                     players_number=formpage.players_number.data,
                     vacant=formpage.players_number.data-1,
                     sport=formpage.sport.data,
                     begginer=current_user,)
        db.session.add(team)
        db.session.commit()
        flash('Your new team has been created!', 'success')
        return redirect(url_for(sport))
    return render_template('new_team.html', title='Create New Team', formpage=formpage)

@app.route('/teams/<int:team_id><string:sport>', methods=['POST', 'GET'])
@login_required
def team(team_id,sport):
    team = Teams.query.get_or_404(team_id)
    formpage = None
    flag = 1
    link = 'http://127.0.0.1:5000/'+str(team_id)+sport+'/chat'
    if team.vacant!=0:
        if team.begginer != current_user:
            flag = 0
            if current_user.phone in team.members:
                formpage = LeaveForm()
                if formpage.validate_on_submit():
                    toreplace = ' | ' + current_user.name + ' Cel: ' + current_user.phone
                    members = team.members.replace(toreplace, '')
                    team.members = members
                    new_vacant = team.vacant + 1
                    team.vacant = new_vacant
                    db.session.commit()
                    flash('You have leave!!!', 'success')
                    return redirect(url_for(sport))
            else:
                formpage = JoinForm()
                if formpage.validate_on_submit():
                    members = team.members + ' | ' + current_user.name + ' Cel: ' + current_user.phone
                    team.members = members
                    new_vacant = team.vacant - 1
                    team.vacant = new_vacant
                    db.session.commit()
                    flash('You have join the team!!!', 'success')
                    return redirect(url_for(sport))
    if team.begginer == current_user:
        flag=0
        formpage = DeleteForm()
        if formpage.validate_on_submit():
            flash('The team has been deleted!!!','success')
            db.session.delete(team)
            db.session.commit()
            return redirect(url_for(sport))
    return render_template('team.html', title='Update Team', formpage=formpage, team=team,flag=flag, link=link)

@app.route('/<int:team_id><string:sport>/chat', methods=['POST', 'GET'])
@login_required
def sessions(team_id,sport):
    team = Teams.query.get_or_404(team_id)
    if current_user.phone in team.members:
        username = current_user.name
        formpage = MessageForm()
        if request.method == 'GET':
            formpage.username.data = current_user.name
    else:
        flash('Your not part of the team, you can not get into the chat!!')
        return redirect(url_for(sport))
    return render_template('session.html',title='Team Chat', formpage=formpage, username=username)

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)




# -----------------------PROFILE SECTION--------------------------------------------------
def save_picture(form_picture):
    f_name, f_ext = os.path.splitext(form_picture.filename)
    random_name = random.randint(1, 9999999999999999)  # change to unique name
    picture_fn = str(random_name) + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    # resize image
    output_size = (230, 230)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    formpage = UpdateAccountForm()
    if formpage.validate_on_submit():
        if formpage.picture.data:  # save profile picture
            picture_file = save_picture(formpage.picture.data)
            current_user.image_file = picture_file
        current_user.name = formpage.name.data
        current_user.email = formpage.email.data
        current_user.phone = formpage.phone.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        formpage.name.data = current_user.name
        formpage.email.data = current_user.email
        formpage.phone.data = current_user.phone
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file, formpage=formpage)

# ------------------ RESET PASSWORD ROUTES AND FUNCTIONS ---------------------------------
def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
    url = url_for('reset_token', token=token, _external=True)
    msg.body = '''To reset your password, visit the following link:
    ''' + url + '''

If you did not make this request then simply ignore this email and no changes will be made.'''
    mail.send(msg)

@app.route('/reset_password', methods=['POST', 'GET'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('soccer'))
    formpage = RequestResetForm()
    if formpage.validate_on_submit():
        user = User.query.filter_by(email=formpage.email.data).first()
        send_reset_email(user)
        flash('An email has been send with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', formpage=formpage)

@app.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('soccer'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid Token', 'warning')
        return redirect(url_for('reset_request'))
    formpage = ResetPasswordForm()
    if formpage.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(formpage.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!! you are now able to login!!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', formpage=formpage)

# ----------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
