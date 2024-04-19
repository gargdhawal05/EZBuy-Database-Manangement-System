import mysql.connector
connect = None

def get_connect():
    global connect 
    if connect is None:
        connect = mysql.connector.connect(user='root', password='suhanisql',
                              host='localhost',
                              database='EZBuyDatabase')
    return connect