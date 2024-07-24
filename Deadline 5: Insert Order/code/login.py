from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re
c_id=10
app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Myfamily5*'
app.config['MYSQL_DB'] = 'EZBuyDatabase'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM customer WHERE Email= %s AND Password = %s', (email,password))
        customer = cursor.fetchone() 

        cursor.execute('SELECT Blocked FROM customer WHERE Email = %s', (email,))
        blocked_status = cursor.fetchone()

        if blocked_status[0]==1:
            msg='Your account is blocked!'

        elif customer and password:  
            session['loggedin'] = True
            session['id'] = customer[0]  
            session['email'] = customer[2]  
            msg = 'Logged in successfully!'
            return redirect(url_for('index'))  
        else:
            cursor.execute('INSERT INTO login_attempts (Pass,Email) VALUES (%s, %s)', (password, email))
            mysql.connection.commit()

            cursor.execute('SELECT Blocked FROM customer WHERE Email = %s', (email,))
            blocked_status = cursor.fetchone()
            
            if blocked_status and blocked_status[0] == 1:
                msg = 'Your account has been blocked due to multiple failed login attempts. Please contact support for assistance.'
            else:
                msg = 'Incorrect email / password!'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)       
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'password' in request.form and 'email' in request.form:
        password = request.form['password']
        email = request.form['email']
        firstname = request.form['firstname']
        lastname = request.form.get('lastname')
        phone = request.form['phone']
        altphone = request.form.get('altphone')
        address = request.form['address']
        cursor = mysql.connection.cursor()
        Customer_id = c_id+1
        cursor.execute('SELECT * FROM customer WHERE Email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif len(password) < 8:
            msg = 'Password must be at least 8 characters long!'
        else:
            cursor.execute('INSERT INTO customer (Customer_id,First_name, Second_name, Email, Password, Address) VALUES (%s,%s, %s, %s, %s, %s)',
                           (Customer_id,firstname, lastname, email, password, address))
            
            cursor.execute('INSERT INTO customer_phone_numbers (customer_id, Phone_number) VALUES (%s, %s)',
                           (Customer_id, phone))
            if altphone:
                cursor.execute('INSERT INTO customer_phone_numbers (customer_id, Phone_number) VALUES (%s, %s)',
                               (Customer_id, altphone))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/index')
def index():
    if 'loggedin' in session:
        if 'email' in session: 
            return render_template('index.html', email=session['email'])
        else:
            return render_template('index.html', username=session['username']) 
    return redirect(url_for('login'))  


if __name__ == "__main__":
    app.run(debug=True)
