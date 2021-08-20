from flask_jwt import jwt_required, JWT
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from datetime import timedelta
from flask_cors import CORS
import sqlite3
import hmac


class UserInfo(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def create_user_table():
    with sqlite3.connect('point_sale.db') as connection:
        cursor = connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS user_info(user_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                       'full_name TEXT NOT NULL,'
                       'username TEXT NOT NULL,'
                       'password TEXT NOT NULL,'
                       'email TEXT NOT NULL)')
        print('User Table Created')


def create_product_table():
    connection = sqlite3.connect('point_sale.db')

    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS product_info(product_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                   'category TEXT NOT NULL,'
                   'name TEXT NOT NULL,'
                   'product_image_url TEXT NOT NULL,'
                   'price TEXT NOT NULL,'
                   'description TEXT NOT NULL)')
    print('Product Table Created')
    connection.close()


create_user_table()
create_product_table()


def fetch_users():
    with sqlite3.connect('point_sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_info")
        users_info = cursor.fetchall()

        new_data = []

        for data in users_info:
            new_data.append(UserInfo(data[0], data[2], data[3]))
    return new_data


fetch_users()

username_table = {u.username: u for u in fetch_users()}
userid_table = {u.id: u for u in fetch_users()}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
# email_password = "JM@y41020"
app.config['SECRET_KEY'] = 'super-secret'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=86400)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'jmay41020@gmail.com'
app.config['MAIL_PASSWORD'] = "JM@y41020"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
CORS(app)
jwt = JWT(app, authenticate, identity)


@app.route('/registration/', methods=['POST'])
def register_user():
    response = {}

    if request.method == "POST":
        full_name = request.json['full_name']
        username = request.json['username']
        password = request.json['password']
        email = request.json['email']

        with sqlite3.connect("point_sale.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO user_info("
                           "full_name,"
                           "username,"
                           "password,"
                           "email) VALUES(?, ?, ?, ?)", (full_name, username, password, email))
            connection.commit()
            response["message"] = "success"
            response["status_code"] = 201
            # if response["status_code"] == 201:
            #     msg = Message('Welcome Message', sender='jmay41020@gmail.com',
            #                   recipients=[email])
            #     msg.body = "Welcome, You are successfully registered ;)."
            #     mail.send(msg)
            return response


@app.route('/adding/', methods=["POST"])
@jwt_required()
def add_products():
    response = {}

    if request.method == "POST":
        category = request.json['category']
        name = request.json['name']
        product_image = request.json['product_image_url']
        price = request.json['price']
        description = request.json['description']

        # cloudinary.config(cloud_name='dzzwcmwvn', api_key='354923386558991', api_secret='K4Hwy9i2Glvukp1VlywM5YO2IbE')
        # upload_result = None
        #
        # app.logger.info('%s file_to_upload', product_image)
        # if product_image:
        #     upload_result = cloudinary.uploader.upload(product_image)
        #     app.logger.info(upload_result)

        with sqlite3.connect("point_sale.db") as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO product_info("
                           "category,"
                           "name,"
                           "product_image_url,"
                           "price,"
                           "description) VALUES(?, ?, ?, ?, ?)", (category, name, product_image, price, description))
            connection.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/viewing/')
def view_products():
    response = {}

    with sqlite3.connect("point_sale.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product_info")

        products = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = products
    return jsonify(response)


@app.route('/view-one/<int:product_id>/')
def view_one_product(product_id):
    response = {}

    with sqlite3.connect("point_sale.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM product_info WHERE product_id='{}'".format(str(product_id)))
        product = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = product
    return jsonify(response)


@app.route('/updating/<int:product_id>/', methods=["PUT"])
# @jwt_required()
def updating_products(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('point_sale.db') as conn:
            print(request.json)
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")

                with sqlite3.connect('point_sale.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product_info SET category =? WHERE product_id=?", (put_data["category"],
                                                                                              product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("name") is not None:
                put_data["name"] = incoming_data.get("name")

                with sqlite3.connect('point_sale.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product_info SET name =? WHERE product_id=?",
                                   (put_data["name"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("product_image_url") is not None:
                put_data["product_image_url"] = incoming_data.get("product_image_url")

                with sqlite3.connect('point_sale.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product_info SET product_image_url =? WHERE product_id=?",
                                   (put_data["product_image_url"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("price") is not None:
                put_data["price"] = incoming_data.get("price")

                with sqlite3.connect('point_sale.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product_info SET price =? WHERE product_id=?",
                                   (put_data["name"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("description") is not None:
                put_data["description"] = incoming_data.get("description")

                with sqlite3.connect('point_sale.db') as connection:
                    cursor = connection.cursor()
                    cursor.execute("UPDATE product_info SET description =? WHERE product_id=?",
                                   (put_data["description"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

    return response


@app.route('/get-user/<username>')
# @jwt_required()
def get_user(username):
    response = {}

    with sqlite3.connect('point_sale.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_info WHERE username='{}'".format(username))

        response['message'] = 'User data retrieved successful'
        response['status_code'] = 200
        response['user'] = cursor.fetchall()

    return response


@app.route('/deleting/<int:product_id>/')
def delete_products(product_id):
    response = {}

    with sqlite3.connect("point_sale.db") as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM product_info WHERE product_id=" + str(product_id))
        connection.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response


if __name__ == '__main__':
    app.run()
    app.debug = True
