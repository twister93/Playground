from app import Student
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,ValidationError
from wtforms.validators import Length,Email,EqualTo,DataRequired,regexp



class Formname(FlaskForm):
    name = StringField('Name:', validators=[DataRequired(), Length(min=2, max=80)])
    student_no = StringField('Student No.:', validators=[DataRequired(), Length(min=2, max=10)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_con = PasswordField('Confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_student_no(self,student_no):
        student = Student.query.filter_by(student_no=student_no.data).first()
        if student:
            raise ValidationError('your student no has been registered')

    def validate_email(self,email):
        email = Student.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('your student no has been registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(),Length(min=4,max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')