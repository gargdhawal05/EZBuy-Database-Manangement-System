from connection import get_connect

def insert_order(connection, order):
    cursor = connection.cursor()

    # Check wallet balance
    customer_id = order['customer_id']
    check_wallet_query = "SELECT wallet FROM payment WHERE customer_id = %s"
    print(customer_id)
    cursor.execute(check_wallet_query, (customer_id,))
    wallet_balance = cursor.fetchone()

    if wallet_balance is None:
        print("Error: Wallet not found for the customer.")
        return None

    wallet_balance = wallet_balance[0]


    #assigning an available delivery agent to the order
    da_id_query = "SELECT DA.DeliveryAgent_ID FROM Delivery_Agent DA WHERE DA.Availability = 'YES' LIMIT 1"
    cursor.execute(da_id_query)
    da_id = cursor.fetchone()[0]

    #updating the delivery agent's availability
    update_daid = f"UPDATE Delivery_Agent SET Availability = 'NO' WHERE DeliveryAgent_ID = {da_id}"
    cursor.execute(update_daid)
   
    #inserting values in the orders table
    order_query = ("INSERT INTO orders(Customer_ID, DeliveryAgent_ID, discount,total_price) VALUES (%s,%s,%s,%s)")
    order_data = (order['customer_id'], da_id,00.00,00.00)

    cursor.execute(order_query, order_data)
    order_id = cursor.lastrowid

    order_details_query = ("INSERT INTO order_details "
                           "(order_id, product_id, quantity, price)"
                           "VALUES (%s, %s, %s, %s)")

    order_details_data = []
    for order_detail_record in order['order_details']:
        order_details_data.append([
            order_id,
            int(order_detail_record['product_id']),
            int(order_detail_record['quantity']),
            float(order_detail_record['price'])
        ])
    cursor.executemany(order_details_query, order_details_data)

    # update order details price based on product price
    update_order_details_price_query = f"UPDATE order_details AS od JOIN product AS p ON od.product_id = p.product_id SET od.price = p.price * od.quantity WHERE od.order_id = %s;"
    cursor.execute(update_order_details_price_query, (order_id,))

    # calculate total price for the order
    calculate_total_price_query =f"UPDATE orders AS o JOIN (SELECT order_id, SUM(price) AS total_price FROM order_details GROUP BY order_id) AS od ON o.order_id = od.order_id SET o.total_price = od.total_price WHERE o.order_id = %s;"
    cursor.execute(calculate_total_price_query, (order_id,))


    #calculating the total bill amount
    bill_query = f"UPDATE orders JOIN (SELECT order_id, SUM(price) AS final_price FROM order_details GROUP BY order_id) AS od ON orders.order_id = od.order_id SET orders.total_price = od.final_price;"
    cursor.execute(bill_query)

    select_query = "SELECT total_price FROM orders"
    cursor.execute(select_query)
    amount = cursor.fetchall()
    last_amount = amount[-1] if amount else None

    if wallet_balance < last_amount:
        print("Insufficient balance")
        return
    
    if wallet_balance >= last_amount:
        connection.commit()
        new_wallet_balance = wallet_balance - last_amount
        update_wallet_query = "UPDATE payment SET wallet = %s WHERE customer_id = %s"
        cursor.execute(update_wallet_query, (new_wallet_balance, customer_id))

    print("To pay:", last_amount[0])
    if order_id:
        print("Order Inserted successfully")
    else:
        print("Insert failed")

    return order_id

def get_order_details(connection, order_id):
    cursor = connection.cursor()

    query = """
        SELECT order_details.order_id, order_details.quantity, order_details.price,
               product.name AS product_name, product.price AS price_per_unit
        FROM order_details 
        LEFT JOIN product ON order_details.product_id = product.product_id 
        WHERE order_details.order_id = %s
    """

    cursor.execute(query, (order_id,))
    records = []
    for (order_id, quantity, price, name, price_per_unit) in cursor:
        records.append({
            'order_id': order_id,
            'quantity': quantity,
            'product_name': name,
            'price_per_unit': price_per_unit
        })
   
    cursor.close()

    return records


def get_order(connection):
    cursor = connection.cursor()

    query = ("SELECT * FROM orders")
    cursor.execute(query)
    response = []
    for (order_id, DeliveryAgent_ID, customer_id,discount, total_price) in cursor:
        response.append({
            'order_id': order_id,
            'deliveryagent_id': DeliveryAgent_ID,
            'customer_id': customer_id,
            'discount' : discount,
            'total_price' : total_price
        })

    cursor.close()

    # append order details in each order
    for record in response:
        record['order_details'] = get_order_details(connection, record['order_id'])
    return response


if __name__ == '__main__':
    connection = get_connect()
    
