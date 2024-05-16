from connection import get_connect
import re


def check_login(connection, email, password):
    cursor = connection.cursor()
    cursor.execute("SELECT Customer_id FROM customer WHERE Email=%s AND Password=%s", (email, password))
    customer_id = cursor.fetchone()
    # print(customer_id[0])
    if customer_id:
        print("Login Successful")
        cursor.close()
        return customer_id[0]
    else:
        print("Wrong email or password. Login Attempt Failed.")
        cursor.close()
        return None


def register(connection):
    email = input("Enter your email: ")
    password = input("Enter your password(8 characters): ")
    firstname = input("Enter your first name: ")
    lastname = input("Enter your last name: ")
    phone = input("Enter your phone number: ")
    altphone = input("Enter your alternative phone number (optional): ")
    address = input("Enter your address: ")

    cursor = connection.cursor()
    cursor.execute('SELECT * FROM customer WHERE Email = %s', (email,))
    account = cursor.fetchone()
    if account:
        print('Account already exists!')
        return False

    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        print('Invalid email address!')
        return False
    elif len(password) < 8:
        print('Password must be at least 8 characters long!')
        return False
    else:
        cursor.execute('INSERT INTO customer (First_name, Second_name, Email, Password, Address) VALUES (%s, %s, %s, %s, %s)',
                        (firstname, lastname, email, password, address))
        last_inserted_customer_id = cursor.lastrowid
        
        cursor.execute('INSERT INTO customer_phone_numbers (customer_id, Phone_number) VALUES (%s, %s)',
                        (last_inserted_customer_id, phone))
        if altphone:
            cursor.execute('INSERT INTO customer_phone_numbers (customer_id, Phone_number) VALUES (%s, %s)',
                            (last_inserted_customer_id, altphone))
        connection.commit()
        print('You have successfully registered!')
        return last_inserted_customer_id

def index(customer):
    print("Welcome, ", customer['Email'])  
    return

def admin_login(connection):
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    cursor = connection.cursor()
    cursor.execute("SELECT manager_id FROM database_manager WHERE username = %s AND password = %s", (username, password))
    admin = cursor.fetchone()

    if admin:
        print("Admin login successful!")
        return admin[0]
    else:
        print("Invalid username or password. Admin login failed.")
        return None


