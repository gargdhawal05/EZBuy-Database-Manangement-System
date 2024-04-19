from connection import get_connect

import products
import orders
import login
import analysis

def display_products(connection):
    products_table = products.get_product(connection)
    for product in products_table:
        print("Product ID:", product['product_id'])
        print("Name:", product['name'])
        print("Category:", product['category'])
        print("Price:", product['price'])
        print("Description:", product['description'])
        print("Returnable:", product['returnable'])
        print("="*30)  



def order_product(connection, cid):
    cursor = connection.cursor()
    cid = cid
    order = {'customer_id': cid, 'order_details': []}
    while True:
        pid = input("Enter the product id you want to add in the cart (or -1 to exit): ")
        if pid == '-1':
            print("Exiting...")
            break

        # Checking if the product is available
        product = products.get_product_by_id(connection, pid)
        if not product:
            print("Error: Product not found.")
            continue


        # Checking if the stock is not 0
        product = product[0]
        stock = product['quantity']
        if stock == 0:
            print("Error: The product is out of stock.")
            continue
        pqty = int(input("Enter its quantity to be added: "))
        
        #Checking if the product quantity asked is available
        if pqty > stock:
            print("Not enough quantity available.")
            continue


        order['order_details'].append({
            'product_id': pid,
            'quantity': pqty,
            'price': 0  
        })

        # Update product quantity in the inventory directly
        update_query = "UPDATE product SET quantity = quantity - %s WHERE product_id = %s"
        cursor.execute(update_query, (pqty, pid))

    orders.insert_order(connection, order)

def loginfun(connection):
    cursor = connection.cursor()
    print("Login as customer")
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    cid = login.check_login(connection, email, password)
    if cid:
        greeting_query = "SELECT CONCAT('Welcome, ', First_name, ' ', COALESCE(Second_name, '')) AS greeting FROM customer WHERE Customer_id = %s"
        cursor.execute(greeting_query, (cid,))
        response = cursor.fetchone()
        if response:
            print(response[0])
    return cid

def registerfun(connection):
    cid = login.register(connection)
    if cid:
        return cid
    else:
        print("Registration Failed")

def adminfun(connection):
    print("Admin Login")
    admin_id = login.admin_login(connection)
    return admin_id

def add_product():
    product = {}
    product['name'] = input("Enter product name: ")
    product['category'] = input("Enter product category: ")
    product['description'] = input("Enter product description: ")
    product['quantity'] = int(input("Enter product quantity: "))
    product['returnable'] = input("Is the product returnable? (yes/no): ").lower() == 'yes'
    product['price'] = float(input("Enter product price: "))
    return product

def stats(connection):
    print("Inventory Analysis:")
    print("1. Display the most revenue generating product.")
    print("2. Display the top 5 most purchased products.")
    print("3. Display products with low stock")

    choice = int(input("Enter your choice: "))
    analysis.analysis(connection,choice)
    return None

def print_order(connection):
    response = orders.get_order(connection)
    for order in response:
        print("Order ID:", order['order_id'])
        print("Delivery Agent ID:", order['deliveryagent_id'])
        print("Customer ID:", order['customer_id'])
        # print("Discount:", order['discount'])
        print("Total Price:", order['total_price'])
        print("Order Details:")
        for detail in order['order_details']:
            print("\nQuantity:", detail['quantity'])
            print("Product Name:", detail['product_name'])
            print("Price per Unit:", detail['price_per_unit'])
        print("=" * 30)

if __name__ == '__main__':
    connection = get_connect()
    while True:
        print("Select an option:\n1.Login as customer\n2.Register\n3.Login as an admin\n4.Exit")
        choice = int(input("Enter choice: "))
        if(choice == 1):
            cid = loginfun(connection)
        elif (choice == 2):
            cid = registerfun(connection)
        elif (choice == 3):
            admin_id = adminfun(connection)
            if admin_id:
                while True:
                    print("Select an option:\n1.Insert new product\n2.Delete Product\n3.View Stats\n4.View orders\n5.Exit")
                    option = int(input("Enter option: "))
                    if option == 1:
                        product_data = add_product()
                        product_id = products.insert_product(connection,product_data)
                        if product_id:
                            print("Product added successfully")
                    elif option == 2:
                        product_id = input("Enter product id to be deleted: ")
                        products.delete_product(connection,product_id)
                        print("Product deleted successfully")
                    elif (option == 3):
                        stats(connection)
                    elif (option == 4):
                        print_order(connection)
                    elif (option == 5):
                        break
                    else:
                        print("Invalid option")
        elif(choice == 4):
            break
        else:
            print("Invalid choice")
        
        option2 = input("\n1.Press Enter to continue browsing\n2.Press 2 to login/register\n3.Press -1 to exit\n Enter option: ")
        if option2 == '-1':
            break
        elif option2 == '2':
            continue
        else:
            choice2 = int(input("1.Displaying products:\n2.Ordering Products\n"))
            if(choice2 == 1):
                print("Displaying products:")
                display_products(connection)
            elif (choice2 == 2):
                if cid is not None:
                    print("Ordering products")
                    print("Products list:")
                    display_products(connection)
                    order_product(connection, cid)
                else:
                    print("Kindly register")
            else:
                print("="*30)    
        