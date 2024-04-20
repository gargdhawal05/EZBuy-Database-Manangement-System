from connection import get_connect

def analysis(connection,choice):
    cursor = connection.cursor()

    queries = [
        "SELECT p.name AS Product_Name, SUM(od.price) AS Revenue FROM order_details od INNER JOIN product p ON od.product_id = p.product_id GROUP BY p.name ORDER BY Revenue DESC LIMIT 1;",
        "SELECT p.name AS Product_Name, SUM(od.quantity) AS total_quantity FROM order_details od INNER JOIN product p ON od.product_id = p.product_id GROUP BY p.name ORDER BY total_quantity DESC LIMIT 5;",
        "SELECT name AS Product_Name, quantity AS stock FROM product WHERE quantity < 5;"
    ]

    query = queries[choice - 1]  
    cursor.execute(query)
    result = cursor.fetchall()

    if choice == 1:
        print("Most Revenue Generating Product:")
        for row in result:
            print(f"Product Name: {row[0]}")
            print(f"Revenue: {row[1]}")
    elif choice == 2:
        print("Top 5 Most Purchased Products:")
        for row in result:
            print(f"Product Name: {row[0]}")
            print(f"Total Quantity Purchased: {row[1]}")
    elif choice == 3:
        print("Products with Low Stock:")
        for row in result:
            print(f"Product Name: {row[0]}")
            print(f"Stock Quantity: {row[1]}")

    connection.commit()

