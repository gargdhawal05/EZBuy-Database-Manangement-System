from connection import get_connect

def get_product(connection):
    cursor = connection.cursor()
    query = ("select product.product_id, product.name, product.category, product.price, product.description, product.returnable from product")
    cursor.execute(query)
    response = []
    for (product_id, name, category, price, description, returnable) in cursor:
        response.append({
            'product_id': product_id,
            'name': name,
            'category': category,
            'price': price,
            'description': description,
            'returnable' : returnable
        })
    return response

def get_product_by_id(connection, product_id):
    cursor = connection.cursor()
    query = "SELECT * FROM product WHERE product_id = %s"
    cursor.execute(query, (product_id,))
    response = []
    for (product_id, name, category, description, quantity, returnable, price) in cursor:
        response.append({
            'product_id': product_id,
            'quantity': quantity,
            'name': name,
            'category': category,
            'price': price,
            'description': description,
            'returnable': returnable
        })
    return response




def insert_product(connection,product):
    cursor = connection.cursor()
    query=("INSERT INTO product"
           "(name, category, description, quantity, returnable, price)"
           "VALUES (%s,%s,%s,%s,%s,%s)")
    data=(product['name'],product['category'],product['description'],product['quantity'],product['returnable'],product['price'])
    cursor.execute(query,data)
    connection.commit()
    product_id = cursor.lastrowid
    return product_id

def delete_product(connection, product_id):
    cursor = connection.cursor()
    delete_query = "DELETE FROM product WHERE product_id = %s IF EXISTS (SELECT 1 FROM product WHERE product_id = %s)"
    cursor.execute(delete_query, (product_id, product_id))
    
    if cursor.rowcount == 0:
        print("Product ID does not exist.")
    else:
        print("Product deleted successfully.")
    connection.commit()
    cursor.close()

 


# if __name__ == '__main__':
#     connection = get_connect()
#     products_table = get_product(connection)
#     for product in products_table:
#         print("Product ID:", product['product_id'])
#         print("Name:", product['name'])
#         print("Category:", product['category'])
#         print("Price:", product['price'])
#         print("Description:", product['description'])
#         print("Returnable:", product['returnable'])
#         print("="*30)  

   
