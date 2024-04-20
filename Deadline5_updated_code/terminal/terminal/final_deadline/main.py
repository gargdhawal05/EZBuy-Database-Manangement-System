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

def gethistory(connection, cid):
    cursor = connection.cursor()

    query = """
        SELECT * 
        FROM orders 
        WHERE Customer_id = %s
    """

    cursor.execute(query, (cid,))
    orders_history = cursor.fetchall()

    if orders_history:
        print("Order History:")
        for order in orders_history:
            print("Order ID:", order[0])
            print("Delivery Agent ID:", order[2])
            print("Total Price:", order[4])
            print("\nOrder Details:")
            # Get order details for each order
            order_details = orders.get_order_details(connection, order[0])
            for detail in order_details:
                print("Product name:", detail['product_name'])
                print("Quantity:", detail['quantity'])
                print("Price per Unit:", detail['price_per_unit'])
            print("=" * 30)
    else:
        print("No order history found for this customer.")

    cursor.close()



def add_to_cart(connection, cid, cart):
    cursor = connection.cursor()

    while True:
        pid = input("Enter the product id you want to add to the cart (or -1 to exit): ")
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

        # Checking if the product quantity asked is available
        if pqty > stock:
            print("Not enough quantity available.")
            continue

        cart.append({
            'product_id': pid,
            'quantity': pqty,
            'price': product['price']
        })

        print("Product added to the cart successfully.")

    return cart

def remove_from_cart(cart):
    if not cart:
        print("Cart is empty.")
        return cart

    print("Current Cart:")
    for i, item in enumerate(cart):
        print(f"{i+1}. Product ID: {item['product_id']}, Quantity: {item['quantity']}, Price: {item['price']}")

    index = int(input("Enter the index of the item you want to remove (starting from 1): ")) - 1

    if 0 <= index < len(cart):
        del cart[index]
        print("Product removed from the cart successfully.")
    else:
        print("Invalid index.")

    return cart

def view_cart(cart):
    if not cart:
        print("Cart is empty.")
        return

    total_amount = sum(item['price'] * item['quantity'] for item in cart)

    print("Current Cart:")
    for i, item in enumerate(cart):
        print(f"{i+1}. Product ID: {item['product_id']}, Quantity: {item['quantity']}, Price: {item['price']}")

    print(f"Total Amount: {total_amount}")

def place_order(connection, cid, cart):
    if not cart:
        print("Cart is empty. Add some products to the cart first.")
        return

    order = {'customer_id': cid, 'order_details': cart}
    order_id = orders.insert_order(connection, order)
    if order_id:
        print("Order placed successfully.")
        return True
    else:
        print("Failed to place the order.")
        return False

def order_products(connection, cid):
    cart = []
    while True:
        print("\nOptions:")
        print("1. Add product to cart")
        print("2. Remove product from cart")
        print("3. View cart")
        print("4. Place order")
        print("5. Exit")
        option = int(input("Enter your choice: "))

        if option == 1:
            cart = add_to_cart(connection, cid, cart)
        elif option == 2:
            cart = remove_from_cart(cart)
        elif option == 3:
            view_cart(cart)
        elif option == 4:
            if place_order(connection, cid, cart):
                break
        elif option == 5:
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

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
        
        option2 = input("\n1.Press Enter to continue browsing\n2.Press 2 to login/register\n3.Press 3 to view your order history\n4.Press -1 to exit\n Enter option: ")
        if option2 == '-1':
            break
        elif option2 == '2':
            continue
        elif option2 == '3':
            if cid:
                gethistory(connection,cid)
            else:
                print("Please login first.")
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
                    order_products(connection,cid)
                else:
                    print("Kindly register")
            else:
                print("="*30)    
        