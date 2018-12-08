from flask import Flask, render_template, url_for, flash, json, request, session, redirect
from flask_wtf import FlaskForm #form
from wtforms import StringField, SubmitField,PasswordField,ValidationError #field user
from wtforms.validators import Length,Email,EqualTo,DataRequired,regexp #validators


from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

#from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY']="AAAAB3NzaC1yc2EAAAABJQAAAgEAhHGjeoeQ09HKzCLLSSFQe/CnE7Yihyqkw7MFE2lv/PSNakeNp9kWeSItb+9gIUMqIq8wUGuTb/TcWXth+5/EYOvcjjpzr574YGrJ81tnHJxNEbVxDGEZzCUvGvEWVOsf7EA1Gm8zf49ECf15BYNDtE8KO4zxUBsJUjhYzYwoNBgOCukmEnBiyug4dP7VuJTP+onswS7+FBumLqxyQjci4YnfAijcidV2mF7j+Hc9yfsRjob8BcF6kB+7T0tfPuUhNs0zkaiVZBXtxF60r9LuvwM5YyGkL+22oTDimoExnGdIss7Z9kNIoL4nSancZTTw6/B56Z4nNGc5pYBqtHsJaFYBnWcS7uwUUWFSJE6NmXKyZMNog00bfwIGkI+fdbnUrRxPVI0aig8aRxpY79M5ejauRpaJNeHnrO092XsOk6Cox6fX+Cr1lewIsAkEKqCnjkSMFmWnqtAFP2ztSTfHrqUfZrmxcZ9MDrOcPRhcWjneogWt3Rwnu3PzAvevNvIBgMYrpELE2+fPXg+ZFhRuJOFuENwVG5woHkC6UE0ztskhbHGXO73uh5ftMLLPEJEBYlM0tbwrzPYJZ7aUFT5PZJqhpWa+Y3GjJ7Xky4/xA+zYcF6q0vQMImkVYbEUB7Y+E3oV8Jz0YysjHZFSmckh1M8SE8A3ON+ZtRhopCW0CDk="
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///sqlweb.db'
db=SQLAlchemy(app)
bcrypt=Bcrypt(app)


app.secret_key = "AAAAB3NzaC1yc2EAAAABJQAAAgEAhHGjeoeQ09HKzCLLSSFQe/CnE7Yihyqkw7MFE2lv/PSNakeNp9kWeSItb+9gIUMqIq8wUGuTb/TcWXth+5/EYOvcjjpzr574YGrJ81tnHJxNEbVxDGEZzCUvGvEWVOsf7EA1Gm8zf49ECf15BYNDtE8KO4zxUBsJUjhYzYwoNBgOCukmEnBiyug4dP7VuJTP+onswS7+FBumLqxyQjci4YnfAijcidV2mF7j+Hc9yfsRjob8BcF6kB+7T0tfPuUhNs0zkaiVZBXtxF60r9LuvwM5YyGkL+22oTDimoExnGdIss7Z9kNIoL4nSancZTTw6/B56Z4nNGc5pYBqtHsJaFYBnWcS7uwUUWFSJE6NmXKyZMNog00bfwIGkI+fdbnUrRxPVI0aig8aRxpY79M5ejauRpaJNeHnrO092XsOk6Cox6fX+Cr1lewIsAkEKqCnjkSMFmWnqtAFP2ztSTfHrqUfZrmxcZ9MDrOcPRhcWjneogWt3Rwnu3PzAvevNvIBgMYrpELE2+fPXg+ZFhRuJOFuENwVG5woHkC6UE0ztskhbHGXO73uh5ftMLLPEJEBYlM0tbwrzPYJZ7aUFT5PZJqhpWa+Y3GjJ7Xky4/xA+zYcF6q0vQMImkVYbEUB7Y+E3oV8Jz0YysjHZFSmckh1M8SE8A3ON+ZtRhopCW0CDk="
#mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'playground'
app.config['MYSQL_DATABASE_PASSWORD'] = 'playground'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)


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


##@app.route('/signUp',methods=['POST'])
##def signUp():
# create user code will be here !!
##   _name = request.form['inputName']
# _email = request.form['inputEmail']
# _password = request.form['inputPassword']


@app.route('/signUp', methods=['POST'])
def signUp():
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # validate the received values
    if _name and _email and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        _hashed_password = generate_password_hash(_password)
        cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
        data = cursor.fetchall()

        if len(data) is 0:
            conn.commit()
            return json.dumps({'message': 'User created successfully !'})
        else:
            return json.dumps({'error': str(data[0])})

        return json.dumps({'html': '<span>All fields good !!</span>'})
    else:
        return json.dumps({'html': '<span>Enter the required fields</span>'})


@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')


@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # connect to mysql

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_validateLogin', (_username,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')


    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html', error='Unauthorized Access')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


@app.route('/showAddWish')
def showAddWish():
    return render_template('addWish.html')


@app.route('/addWish', methods=['POST'])
def addWish():
    try:
        if session.get('user'):
            _title = request.form['inputTitle']
            _description = request.form['inputDescription']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('sp_addWish', (_title, _description, _user))
            data = cursor.fetchall()

            if len(data) is 0:
                conn.commit()
                return redirect('/userHome')
            else:
                return render_template('error.html', error='An error occurred!')

        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/getWish')
def getWish():
    try:
        if session.get('user'):
            _user = session.get('user')
            # Connect to MySQL and fetch data
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetWishByUser', (_user,))
            wishes = cursor.fetchall()

            wishes_dict = []
            for wish in wishes:
                wish_dict = {
                    'Id': wish[0],
                    'Title': wish[1],
                    'Description': wish[2],
                    'Date': wish[4]}
                wishes_dict.append(wish_dict)
            return json.dumps(wishes_dict)
        else:
            return render_template('error.html', error='Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error=str(e))
