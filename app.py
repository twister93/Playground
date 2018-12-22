from flask import Flask, render_template, url_for, flash, redirect
from flask import request, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY']="AAAAB3NzaC1yc2EAAAABJQAAAgEAhHGjeoeQ09HKzCLLSSFQe/CnE7Yihyqkw7MFE2lv/PSNakeNp9kWeSItb+9gIUMqIq8wUGuTb/TcWXth+5/EYOvcjjpzr574YGrJ81tnHJxNEbVxDGEZzCUvGvEWVOsf7EA1Gm8zf49ECf15BYNDtE8KO4zxUBsJUjhYzYwoNBgOCukmEnBiyug4dP7VuJTP+onswS7+FBumLqxyQjci4YnfAijcidV2mF7j+Hc9yfsRjob8BcF6kB+7T0tfPuUhNs0zkaiVZBXtxF60r9LuvwM5YyGkL+22oTDimoExnGdIss7Z9kNIoL4nSancZTTw6/B56Z4nNGc5pYBqtHsJaFYBnWcS7uwUUWFSJE6NmXKyZMNog00bfwIGkI+fdbnUrRxPVI0aig8aRxpY79M5ejauRpaJNeHnrO092XsOk6Cox6fX+Cr1lewIsAkEKqCnjkSMFmWnqtAFP2ztSTfHrqUfZrmxcZ9MDrOcPRhcWjneogWt3Rwnu3PzAvevNvIBgMYrpELE2+fPXg+ZFhRuJOFuENwVG5woHkC6UE0ztskhbHGXO73uh5ftMLLPEJEBYlM0tbwrzPYJZ7aUFT5PZJqhpWa+Y3GjJ7Xky4/xA+zYcF6q0vQMImkVYbEUB7Y+E3oV8Jz0YysjHZFSmckh1M8SE8A3ON+ZtRhopCW0CDk="
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #eliminar warning
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)

#--------------------------------------------------------
class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    student_no=db.Column(db.String(20),unique=True,nullable=True)
    email=db.Column(db.String(20),unique=True,nullable=True)
    name=db.Column(db.String(10),nullable=True)
    password=db.Column(db.String(30),nullable=True)
    role_id=db.Column(db.Integer,db.ForeignKey('role.id'),nullable=True)

    def __repr__(self):
        return "<Student %r>" % self.name

class Role(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(10),nullable=True)
    students=db.relationship('Student',backref='role',lazy=True)

    def __repr__(self):
        return "<Role %r>" % self.name

from forms import Formname, LoginForm, ContactForm


@app.before_first_request
def setup_db():
    db.create_all()

#---------------------------------------------------------------------

@app.route('/')
@app.route('/home')
def main():
    return render_template('index.html')

#---------------------------------------------------------------------

@app.route("/signup",methods=['POST','GET'])
def signup():
    formpage=Formname()
    if formpage.validate_on_submit():
        password=bcrypt.generate_password_hash(formpage.password.data)
        reg=Student(name=formpage.name.data,
                    student_no= formpage.student_no.data,
                    email= formpage.email.data,
                    password= password,
                    role_id=1)# role_id = Role.query.find_by(name='Student').first()
        db.session.add(reg)
        db.session.commit()
        return render_template("signin.html")
    return render_template('signup.html', formpage = formpage , title='Sign Up')

@app.route("/signin",methods=['POST','GET'])
def login():
    formpage=LoginForm()
    if formpage.validate_on_submit():
        # TODO do query db for login or use login from flask
        st=Student.query.filter_by(email=formpage.email.data).first()
        pass_check=bcrypt.generate_password_hash(formpage.password.data).decode('utf-8')
        if st and bcrypt.check_password_hash(st.password,formpage.password.data):
            session['email']=formpage.email.data
            return redirect(url_for('userHome'))
    return render_template('signin.html', formpage = formpage, email=session.get('email',False) , title='Sign In')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')
#---------------------------------------------------------------------

@app.route('/ContactUs')
def ContactUs():
    formpage=ContactForm()
    return render_template('contact.html', formpage=formpage, title='Contact Us')

@app.route('/userHome')
def userHome():
    return render_template('userHome.html')

if __name__ == '__main__':
    app.run(debug=True)