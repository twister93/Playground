from flask import Flask, render_template, url_for, flash, json, request, session, redirect
from flask_wtf import FlaskForm #form
from wtforms import StringField, SubmitField,PasswordField,ValidationError #field user
from wtforms.validators import Length,Email,EqualTo,DataRequired,regexp #validators


from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SECRET_KEY']="AAAAB3NzaC1yc2EAAAABJQAAAgEAhHGjeoeQ09HKzCLLSSFQe/CnE7Yihyqkw7MFE2lv/PSNakeNp9kWeSItb+9gIUMqIq8wUGuTb/TcWXth+5/EYOvcjjpzr574YGrJ81tnHJxNEbVxDGEZzCUvGvEWVOsf7EA1Gm8zf49ECf15BYNDtE8KO4zxUBsJUjhYzYwoNBgOCukmEnBiyug4dP7VuJTP+onswS7+FBumLqxyQjci4YnfAijcidV2mF7j+Hc9yfsRjob8BcF6kB+7T0tfPuUhNs0zkaiVZBXtxF60r9LuvwM5YyGkL+22oTDimoExnGdIss7Z9kNIoL4nSancZTTw6/B56Z4nNGc5pYBqtHsJaFYBnWcS7uwUUWFSJE6NmXKyZMNog00bfwIGkI+fdbnUrRxPVI0aig8aRxpY79M5ejauRpaJNeHnrO092XsOk6Cox6fX+Cr1lewIsAkEKqCnjkSMFmWnqtAFP2ztSTfHrqUfZrmxcZ9MDrOcPRhcWjneogWt3Rwnu3PzAvevNvIBgMYrpELE2+fPXg+ZFhRuJOFuENwVG5woHkC6UE0ztskhbHGXO73uh5ftMLLPEJEBYlM0tbwrzPYJZ7aUFT5PZJqhpWa+Y3GjJ7Xky4/xA+zYcF6q0vQMImkVYbEUB7Y+E3oV8Jz0YysjHZFSmckh1M8SE8A3ON+ZtRhopCW0CDk="
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlweb.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #eliminar warning
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)



@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)

@app.route('/ContactUs')
def ContactUs():
    return render_template('contact.html')


@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/userHome')
def userHome():
    return render_template('userHome.html')


@app.route('/logout')
def logout():
    #session.pop('user', None)
    return redirect('/')


