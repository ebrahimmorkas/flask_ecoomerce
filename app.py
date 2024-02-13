from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from flask_mysqldb import MySQL
import os, redis
from flask_session import Session
from datetime import timedelta
from flask_bcrypt import Bcrypt
import products
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
app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_TYPE'] = 'redis'
# app.config['SESSION_REDIS'] = redis.Redis(host='localhost', port=6379)
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
Session(app)

@app.route('/')
def home():
    if session.get('login') or session.get('vendorLogin'):
        if session.get('vendorLogin'):
            # vendor is logged in
            vendorID = session['vendorID']
            select_query = "SELECT * FROM product WHERE vendorid = %s"
            values = (vendorID,)
            cur = mysql.connection.cursor()
            cur.execute(select_query, values)
            data = cur.fetchall()
            cur.close()
            return render_template('index.html', data=data)
        else:
            # Buyer is logged in
            select_query = "SELECT * FROM product"
            cur = mysql.connection.cursor()
            cur.execute(select_query)
            data = cur.fetchall()
            buyerid = session['buyerID']
            select_query_for_cart = "SELECT productid FROM cart WHERE buyerid = %s"
            values_cart = (buyerid,)
            cur.execute(select_query_for_cart, values_cart)
            cartData = cur.fetchall()
            cartDataInList = []
            for cartRow in cartData:
                print(cartRow[0])
                cartDataInList.append(int(cartRow[0]))
            cur.close()
            # print("HI")
            # cartDataInDict = set(cartDataInList)
            # print(cartDataInDict)
            return render_template('index.html', data=data, cartData=cartDataInList)
    else:
        return redirect(url_for('login'))

# Route that will delete the product from cart
@app.route('/deleteFromCart', methods=['POST'])
def deleteFromCart():
    if session.get('buyerID'):
        if request.method == 'POST':
            productID = request.json['productID']
            delete_query = "DELETE FROM cart WHERE productid = %s"
            values = (productID,)
            cur = mysql.connection.cursor()
            cur.execute(delete_query, values)
            mysql.connection.commit()
            return jsonify({"msg": "Deletion successful"})
        else:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
# Creating the route for login
@app.route('/login')
def login():
    if session.get('login'):
        return redirect(url_for('home'))
    else:
        return render_template('loginAndSignup/login.html')

# Creating the route that will handle the login form
@app.route('/loginHandler', methods=['POST'])
def loginHandler():
    # Check whether the form has been submitted via POST request
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['password']
        if username == "" or password == "":
            return redirect(url_for('login', data="Incomplete data"))
        else:
            cur = mysql.connection.cursor()
            select_query = "SELECT * FROM users WHERE username = %s"
            values = (username,)
            cur.execute(select_query, values)
            results = cur.fetchall()
            # Checking whether username exists or not
            if results:
                hashedPassword = results[0][4]
                print(f"hiii{hashedPassword}")
                decryptedPassword = bcrypt.check_password_hash(hashedPassword, password)
                print(decryptedPassword)

                # Checking whether the entered password is correct or not
                if decryptedPassword:
                    session['login'] = True
                    session['name'] = results[0][1]
                    session['buyerID'] = results[0][0]
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('login', data="Username or password is wrong"))
            else:
                return redirect(url_for('login', data="Username or password is wrong"))
    else:
        return redirect(url_for('login', data="Form not submited"))

# Creating the route that will display the signup form
@app.route('/signup')
def signup():
    # Check whether session is not if session is not set then only proceed to signup
    if session.get('login'):
        return redirect(url_for('index.html'))
    else:
        return render_template('loginAndSignup/signup.html')

# Creating the route for signup page handler
@app.route('/signupHandler', methods=['POST'])
def signupHandler():
    # Check whether session is not if session is not set then only proceed to signup
    if session.get('name'):
        return redirect(url_for('home'))
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
            # data = request.form
            # print(data['name'])
            # print(data['username'])
            return redirect(url_for('signup', data="Form not submitted"))

# Creating the route that will display the vendor login page
@app.route('/vendorLogin')
def vendorLogin():
    if session.get('vendorLogin'):
        # User already logged in
        print("Already Logged in")
        return redirect(url_for('home'))
    else:
        # User not logged in
        print("not logged in")
        return render_template('vendor/login.html')

# Creating the route that will display the vendor signup page
@app.route('/vendorSignup')
def vendorSignup():
    if session.get('vendorLogin'):
        return redirect(url_for('vendorHome'))
    elif session.get('login'):
        return redirect(url_for('home'))
    else:
        return render_template('vendor/signup.html')

# Creating the route that will handle the vendor signup functionality
@app.route('/vendorSignupHandler', methods=['POST'])
def vendorSignupHandler():
    # Check whether session is not if session is not set then only proceed to signup
    if session.get('vendorLogin'):
        return redirect(url_for('home'))
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
                phone = data['phoneNumber']
                print(phone)

                if name == "" or username == "" or password == "" or address == "" or email == "" or phone == "":
                    return redirect(url_for('vendorSignup', data="Please fill missing data"))
                else:
                    # Checking whether address is not greater than 100 and username is not greater than 45 and email is not greater than 45
                    if len(name) >= 45 or len(username) >= 45 or len(address) >= 100 or len(email) >= 45 or len(phone) != 10:
                        return redirect('veendorSignup', data="Too Long data has been entered")
                    else:
                        # Checking whether username or email exists in database or not
                        cur = mysql.connection.cursor()
                        select_query = "SELECT * FROM vendor WHERE email = %s OR phone = %s OR username = %s"
                        vendor_signup_values = (email, username, phone)
                        cur.execute(select_query, vendor_signup_values)
                        data = cur.fetchall()
                        # If size is zero that means data does not exists and proceed with inserting data
                        if len(data) == 0:
                            hashed_password = bcrypt.generate_password_hash(password,
                                                                            rounds=int(os.environ.get('ROUNDS')))
                            insert_query = "INSERT INTO vendor (username, password, name, email, phone, address) VALUES (%s, %s, %s, %s, %s, %s)"
                            values = (username, hashed_password, name, email, phone, address)
                            cur.execute(insert_query, values)
                            mysql.connection.commit()
                            cur.close()
                            return redirect(url_for('vendorLogin'))
                        else:
                            # Data already exists
                            cur.close()
                            return redirect(url_for('vendorSignup', data="The data you entered already exists"))
            else:
                return redirect(url_for('vendorSignup', data="Form has not been filled"))
        else:
            # data = request.form
            # print(data['name'])
            # print(data['username'])
            return redirect(url_for('vendorSignup', data="Form not submitted"))

# Route that will handle the vendor login functionality
@app.route('/vendorLoginHandler', methods=['POST'])
def vendorLoginHandler():
    print("form received")
    # Check whether the form has been submitted via POST request
    if request.method == 'POST':
        data = request.form
        username = data['username']
        password = data['password']
        if username == "" or password == "":
            return redirect(url_for('vendorLogin', data="Incomplete data"))
        else:
            cur = mysql.connection.cursor()
            select_query = "SELECT * FROM vendor WHERE username = %s"
            values = (username,)
            cur.execute(select_query, values)
            results = cur.fetchall()
            # Checking whether username exists or not
            if results:
                hashedPassword = results[0][2]
                decryptedPassword = bcrypt.check_password_hash(hashedPassword, password)

                # Checking whether the entered password is correct or not
                if decryptedPassword:
                    session['vendorLogin'] = True
                    session['name'] = results[0][3]
                    session['vendorID'] = results[0][0]
                    print(results[0][0])
                    return redirect(url_for('home'))
                else:
                    return redirect(url_for('vendorLogin', data="Username or password is wrong"))
            else:
                return redirect(url_for('vendorLogin', data="Username or password is wrong"))
    else:
        return redirect(url_for('vendorLogin', data="Form not submited"))

# Route that will show the page to add the product
@app.route('/product/addProduct')
def addProduct():
    if session.get('vendorLogin'):
        return render_template('products/addProduct.html')
    else:
        return redirect(url_for('vendorLogin'))

# Route that will handle the addition of product
@app.route('/product/addProductHandler', methods=['POST'])
def addProductHandler():
    if session.get('vendorLogin'):
        if request.method == 'POST':
            if request.form and request.files:
                ALLOWED_EXTENSION = {'jpeg', 'jpg', 'png'}
                ALLOWED_EXTENSION_FOR_ZIP = {'zip', 'rar'}

                # Function that will check the extension of productImage
                def check_file_extension(passedFilename):
                    return '.' in passedFilename and passedFilename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

                # Function that will check the extension of zip i.e. productZip
                def check_zip_extension(passedFilename):
                    return '.' in passedFilename and passedFilename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION_FOR_ZIP

                data = request.form
                productName = data['productName']
                productPrice = data['productPrice']
                productCategory = data['productCategory']
                productQuantity = data['productQuantity']
                productDescription = data['productDescription']
                image = request.files['productImage']
                productImageFilename = image.filename
                productImage = image.read()
                zipImage = request.files['productZip']
                productZipFilename = zipImage.filename
                productZip = zipImage.read()
                vendorID = session['vendorID']
                print("HI")
                print(vendorID)

                if productName == "" or productPrice == "" or productCategory == "" or productQuantity == "" or productDescription == "" or productImageFilename == "" or productZipFilename == "":
                    return redirect(url_for('addProduct', msg="Missing Form Data"))
                else:
                    # Check whether the product Image and Zip file is in correct format
                    if check_zip_extension(productZipFilename) and check_file_extension(productImageFilename):
                        cur = mysql.connection.cursor()
                        insert_query = "INSERT INTO product (name, category, price, description, quantity, image, imagefilename, zip, zipfilename, vendorid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        values = (productName, productCategory, productPrice, productDescription, productQuantity, productImage, productImageFilename, productZip, productZipFilename, vendorID)
                        cur.execute(insert_query, values)
                        mysql.connection.commit()
                        cur.close()
                        return redirect(url_for('addProduct', msg="Product added successfully"))
                    else:
                        return redirect(url_for('addProduct', msg="Image or Zip file may ot be in proper extension"))
            else:
                return redirect(url_for('addProduct', msg="Form does not contain data"))
        else:
            return redirect(url_for('addProduct', msg="Form not submitted"))
    else:
        return redirect(url_for('vendorLogin'))
# Route that will Show the page to update the product
@app.route('/product/updateProduct')
def updateProduct():
    if session.get('vendorLogin'):
        return render_template('products/updateProduct.html')
    else:
        return redirect(url_for('vendorLogin'))

# Route that will handle the searching of product in the updateProduct Form
@app.route('/product/searchProduct', methods=['POST'])
def searchProduct():
    if session.get('vendorLogin'):
        if request.method == 'POST':
            # print("Request recieved")
            productID = request.json['productID']
            select_query = 'SELECT * FROM product WHERE id = %s'
            values = (productID,)
            cur = mysql.connection.cursor()
            cur.execute(select_query, values)
            data = cur.fetchall()
            # print(data)
            if data:
                fetchedImage = data[0][6]
                image = send_file(fetchedImage, mimetype='image/*')
                results = {
                    "productName": data[0][1],
                    "productCategory": data[0][2],
                    "productPrice": data[0][3],
                    "productDescription": data[0][4],
                    "productQuantity": data[0][5],
                    "productImageFilename": data[0][7],
                    "productZipFilename": data[0][9]
                }
                return jsonify(results)
            else:
                error = {"msg": "The given ID does not exist"}
                return jsonify(error)
        else:
            return redirect(url_for('updateProduct'))
    else:
        return redirect(url_for('vendorLogin'))

# Route that is going to show the vendor that are being sold
@app.route('/product/soldProduct')
def soldProducts():
    return "Sold Products"

# Route that i going to delete the product
@app.route('/product/deleteProduct', methods=['POST'])
def deleteProduct():
    print("Request Received")
    if session.get('vendorLogin'):
        if request.method == "POST":
            productId = request.json['productID']
            cur = mysql.connection.cursor()
            select_query = 'SELECT * FROM product WHERE id = %s'
            values = (productId,)
            cur.execute(select_query, values)
            data = cur.fetchall()
            if data:
                delete_query = "DELETE FROM product WHERE id = %s"
                delete_values = (productId,)
                cur.execute(delete_query, delete_values)
                mysql.connection.commit()
                vendorID = session['vendorID']
                # Again sending the ID of the deleted product to remove that row from the table
                dataToBeSent = {'product': productId}
                return jsonify(dataToBeSent)
            else:
                # No data found
                dataToBeSent = {"msg": "No data Found"}
                return jsonify(dataToBeSent)
        else:
            return redirect(url_for('displayProducts'))
    else:
        return redirect(url_for('vendorLogin'))

# Route that is going to display all the products
@app.route('/product/myProducts')
def displayProducts():
    if session.get('vendorLogin'):
        vendorID = session['vendorID']
        select_query = "SELECT * FROM product WHERE vendorid = %s"
        values = (vendorID,)
        cur = mysql.connection.cursor()
        cur.execute(select_query, values)
        data = cur.fetchall()
        cur.close()
        # print(data[0][1])
        # print(data[0][2])
        # print(data[0][3])
        # print(data[0][5])
        return render_template('products/allProducts.html', data=data)
    else:
        return redirect(url_for('vendorLogin'))

# Route that will display the image that has been uploaded for the product
@app.route('/product/viewImage/<int:id>')
def viewImage():
    pass

# Route that will handle the addition of item to cart
@app.route('/addToCart', methods=['POST'])
def cart():
    if session.get('login'):
        if request.method == 'POST':
            productID = request.json['productID']
            buyerID = session['buyerID']
            insert_query = "INSERT INTO cart (productid, buyerid) VALUES (%s, %s)"
            values = (productID, buyerID)
            cur = mysql.connection.cursor()
            cur.execute(insert_query, values)
            mysql.connection.commit()
            cur.close()
            return jsonify({"msg": "Product added to cart"})
        else:
            return jsonify({"msg": "Something went wrong"})
    else:
        return redirect(url_for('login'))

# Route that will handle logout functionality
@app.route('/logout')
def logoutHandler():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)

