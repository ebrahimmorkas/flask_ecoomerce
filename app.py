from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import os, redis
from flask_session import Session
from datetime import timedelta
from flask_bcrypt import Bcrypt
app = Flask(__name__)

# Configuration for hashing
bcrypt = Bcrypt(app)

# Configuration for the mysql
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD')
app.config['MYSQL_DB'] = "flask_ecommerce"
mysql = MySQL(app)

# Configuration for sessions
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
Session(app)

@app.route('/')
def home():
    if session.get('name'):
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

# Creating the route for login
@app.route('/login')
def login():
    # Checking whether the form has been submitted with post request and if not redirect the user to login page
    if request.method == 'POST':
        # checking whether the form has been submitted with data
        if request.form:
            data = request.form
            username = data['username']
            password = data['password']
    else:
        return render_template('loginAndSignup/login.html')


# Creating the route for signup
@app.route('/signup')
def signup():
    # Check whether session is not if session is not set then only proceed to signup
    if session.get('name'):
        return redirect(url_for('index.html'))
    else:
        # check whether the form is submitted via post request
        if request.form == 'POST':
            # check whether the form contains data or not
            if request.data:
                data = request.form
                name = data['name']
                username = data['username']
                password = data['password']
                address = data['address']
                email = data['email']
                hashed_password = bcrypt.generate_password_hash(password, rounds=os.environ.get('ROUNDS'))

            else:
                return redirect(url_for('signup', data="Form has not been filled"))
        else:
            return redirect(url_for('signup', data="Form not submitted"))
if __name__ == '__main__':
    app.run(debug=True)

