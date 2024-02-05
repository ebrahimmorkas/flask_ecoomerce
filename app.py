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


# Creating the route that will display the signup form
@app.route('/signup')
def signup():
    # Check whether session is not if session is not set then only proceed to signup
    if session.get('name'):
        return redirect(url_for('index.html'))
    else:
        return render_template('loginAndSignup/signup.html')

# Creating the route for signup page handler
@app.route('/signupHandler', methods=['POST'])
def signupHandler():
    # Check whether session is not if session is not set then only proceed to signup
    if session.get('name'):
        return redirect(url_for('index.html'))
    else:
        # check whether the form is submitted via post request
        if request.method == 'POST':
            # check whether the form contains data or not
            if request.form:
                data = request.form
                name = data['name']
                username = data['username']
                password = data['password']
                address = data['address']
                email = data['email']

                if name == "" or username == "" or password == "" or address == "" or email == "":
                    return redirect(url_for('signup', data="Please fill missing data"))
                else:
                    # Checking whether address is not greater than 100 and username is not greater than 45 and email is not greater than 45
                    if len(name) >= 45 or len(username) >= 45 or len(address) >= 100 or len(email) >= 45:
                        return redirect('signup', data="Too Long data has been entered")
                    else:
                        # Checking whether username or email exists in database or not
                        cur = mysql.connection.cursor()
                        select_query = "SELECT * FROM users WHERE email = 'xyz' OR username = 'abc'"
                        cur.execute(select_query)
                        data = cur.fetchall()
                        # If size is zero that means data does not exists and proceed with inserting data
                        if len(data) == 0:
                            hashed_password = bcrypt.generate_password_hash(password, rounds=int(os.environ.get('ROUNDS')))
                            insert_query = "INSERT INTO users (name, username, address, password, email) VALUES (%s, %s, %s, %s, %s)"
                            values = (name, username, address, hashed_password, email)
                            cur.execute(insert_query, values)
                            mysql.connection.commit()
                            cur.close()
                            return redirect(url_for('login'))
                        else:
                            # Data already exists
                            cur.close()
                            return redirect(url_for('signup', data="The data you entered already exists"))
            else:
                return redirect(url_for('signup', data="Form has not been filled"))
        else:
            data = request.form
            print(data['name'])
            print(data['username'])
            return redirect(url_for('signup', data="Form not submitted"))
if __name__ == '__main__':
    app.run(debug=True)

