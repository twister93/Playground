from app import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField,SubmitField,PasswordField,ValidationError,TextAreaField,DateTimeField,SelectField,BooleanField
from wtforms.validators import Length,Email,EqualTo,DataRequired,regexp

courts = [('Parco Ruffini', 'Viale Leonardo Bistolfi, 10141 Torino TO'), ('Pozzomaina S.R.L. S.S.D.', 'Via Monte Ortigara, 78, 10141 Torino TO')]

class SignUpname(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=2, max=80)])
    phone = StringField('Phone Number:', validators=[DataRequired(), Length(min=10, max=13)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_con = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_email(self,email):
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('This email have been registered before')

    def validate_phone(self, phone):
        phone = User.query.filter_by(phone=phone.data).first()
        if phone:
            raise ValidationError('That phone has already been used')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(),Length(min=4,max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),Length(min=4,max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=4, max=50)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=4,max=600)])
    submit = SubmitField('Submit')


class UpdateAccountForm(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=2, max=80)])
    phone = StringField('Phone Number:', validators=[DataRequired(), Length(min=10, max=13)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')

    def validate_name(self,name):
        if name.data != current_user.name:
            namel = User.query.filter_by(name=name.data).first()
            if name:
                raise ValidationError('This name have been registered before')

    def validate_email(self,email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('This email have been registered before')

    def validate_phone(self, phone):
        if phone.data != current_user.phone:
            phone = User.query.filter_by(phone=phone.data).first()
            if phone:
                raise ValidationError('That phone has already been used')

#-----------------CREATE and DELETE A GAME ------------------------------

class GameForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    description = TextAreaField('Description',validators=[DataRequired()])
    num_players = SelectField('num_players',choices=[('')])
    court = SelectField('court', choices=[''])
    slot = SelectField('slot',choices=[''])
    team = BooleanField('Check! If it is a Game for your TEAM   ')
    submit = SubmitField('Play')

class JoinForm(FlaskForm):
    submit = SubmitField('Join')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
#-----------------------------------------------------------
class RequestResetForm (FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is None:
            raise ValidationError('There is not an account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password_con = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')