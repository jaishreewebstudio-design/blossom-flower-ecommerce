from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_from_directory,
    session,
    redirect,
)

from flask_cors import CORS
from flasgger import Swagger

import sqlite3
import os

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "blossom-flower-shop-secret-key",
)


# =========================================================
# CORS
# =========================================================

CORS(
    app,
    supports_credentials=True,
)


# =========================================================
# SWAGGER
# =========================================================

swagger = Swagger(app)


# =========================================================
# DATABASE
# =========================================================

DATABASE = os.path.join(
    BASE_DIR,
    "flower_shop.db",
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = get_db()

    try:

        # =================================================
        # USERS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                email TEXT NOT NULL UNIQUE,

                password TEXT NOT NULL,

                created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


        # =================================================
        # FLOWERS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flowers (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,

                category TEXT NOT NULL,

                description TEXT,

                price REAL NOT NULL,

                image TEXT,

                stock INTEGER DEFAULT 0,

                created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


        # =================================================
        # CART
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cart (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                flower_id INTEGER NOT NULL,

                quantity INTEGER NOT NULL DEFAULT 1,

                status TEXT DEFAULT 'In Cart',

                created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(user_id)
                    REFERENCES users(id),

                FOREIGN KEY(flower_id)
                    REFERENCES flowers(id)
            )
            """
        )


        # =================================================
        # ORDERS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                customer_name TEXT NOT NULL,

                phone TEXT NOT NULL,

                address TEXT NOT NULL,

                payment TEXT NOT NULL,

                total REAL NOT NULL,

                status TEXT DEFAULT 'Processing',

                created_at
                    TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(user_id)
                    REFERENCES users(id)
            )
            """
        )


        # =================================================
        # ORDER ITEMS
        # =================================================

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS order_items (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                order_id INTEGER NOT NULL,

                flower_id INTEGER NOT NULL,

                flower_name TEXT NOT NULL,

                price REAL NOT NULL,

                quantity INTEGER NOT NULL,

                subtotal REAL NOT NULL,

                FOREIGN KEY(order_id)
                    REFERENCES orders(id),

                FOREIGN KEY(flower_id)
                    REFERENCES flowers(id)
            )
            """
        )


        # =================================================
        # FLOWER DATA
        # =================================================

        flower_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM flowers
            """
        ).fetchone()[0]


        if flower_count == 0:

            flowers = [

                (
                    "Red Rose Bouquet",
                    "Rose",
                    "Beautiful fresh red roses arranged in an elegant bouquet.",
                    499,
                    "/static/images/red-rose.jpg",
                    25,
                ),

                (
                    "White Lily",
                    "Lily",
                    "Fresh white lilies perfect for gifts and special occasions.",
                    599,
                    "/static/images/white-lily.jpg",
                    20,
                ),

                (
                    "Pink Tulip",
                    "Tulip",
                    "Beautiful fresh pink tulips with a soft and elegant look.",
                    699,
                    "/static/images/pink-tulip.jpg",
                    30,
                ),

                (
                    "Sunflower Bouquet",
                    "Sunflower",
                    "Bright yellow sunflowers arranged into a cheerful bouquet.",
                    399,
                    "/static/images/yellow-sunflower.jpg",
                    15,
                ),

                (
                    "Pink Rose Bouquet",
                    "Rose",
                    "Elegant pink roses arranged beautifully for your loved ones.",
                    549,
                    "/static/images/pink-rose.jpg",
                    18,
                ),

                (
                    "Orange Lily Bouquet",
                    "Lily",
                    "Fresh orange lilies with a vibrant and beautiful appearance.",
                    649,
                    "/static/images/orange-lily.jpg",
                    20,
                ),
            ]


            conn.executemany(
                """
                INSERT INTO flowers
                (
                    name,
                    category,
                    description,
                    price,
                    image,
                    stock
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                flowers,
            )


        conn.commit()


    except Exception as error:

        conn.rollback()

        print(
            "Database Initialization Error:",
            error
        )

        raise


    finally:

        conn.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# PAGE ROUTES
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )


@app.route("/register")
def register_page():

    return render_template(
        "register.html"
    )


@app.route("/flower")
@app.route("/flowers")
def flower_page():

    return render_template(
        "flower.html"
    )


@app.route("/cart")
@app.route("/cart.html")
def cart_page():

    return render_template(
        "cart.html"
    )


@app.route("/checkout")
@app.route("/checkout.html")
def checkout_page():

    return render_template(
        "checkout.html"
    )


@app.route("/orders")
@app.route("/orders.html")
def orders_page():

    return render_template(
        "orders.html"
    )


@app.route("/about")
@app.route("/about.html")
def about_page():

    return render_template(
        "about.html"
    )


@app.route("/contact")
@app.route("/contact.html")
def contact_page():

    return render_template(
        "contact.html"
    )


# =========================================================
# STATIC CSS
# =========================================================

@app.route("/style.css")
def style_css():

    return send_from_directory(
        BASE_DIR,
        "style.css"
    )


# =========================================================
# STATIC JAVASCRIPT
# =========================================================

@app.route("/js/<path:filename>")
def javascript_files(filename):

    return send_from_directory(
        os.path.join(
            BASE_DIR,
            "js"
        ),
        filename
    )


# =========================================================
# API HOME
# =========================================================

@app.route(
    "/api",
    methods=["GET"]
)
def api_home():

    return jsonify(
        {
            "success": True,

            "message":
                "Blossom Flower Shop API is running",
        }
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():

    conn = None

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Request body is required",
                }
            ), 400


        name = str(
            data.get(
                "name",
                ""
            )
        ).strip()


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        if not name or not email or not password:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Name, email and password are required",
                }
            ), 400


        if len(password) < 6:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Password must be at least 6 characters",
                }
            ), 400


        conn = get_db()


        existing = conn.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(TRIM(email)) = ?
            LIMIT 1
            """,
            (email,),
        ).fetchone()


        if existing:

            return jsonify(
                {
                    "success": False,

                    "registered": True,

                    "message":
                        "Email already registered. Please login.",
                }
            ), 409


        password_hash = generate_password_hash(
            password
        )


        cur = conn.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash,
            ),
        )


        conn.commit()


        return jsonify(
            {
                "success": True,

                "registered": True,

                "message":
                    "Registration successful. You can now login.",

                "user":
                    {
                        "id":
                            cur.lastrowid,

                        "name":
                            name,

                        "email":
                            email,
                    },
            }
        ), 201


    except sqlite3.IntegrityError:

        return jsonify(
            {
                "success": False,

                "registered": True,

                "message":
                    "Email already registered. Please login.",
            }
        ), 409


    except Exception as error:

        print(
            "REGISTER ERROR:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Something went wrong during registration.",
            }
        ), 500


    finally:

        if conn:

            conn.close()


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():

    conn = None

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify(
                {
                    "success": False,

                    "registered": False,

                    "message":
                        "Request body is required",
                }
            ), 400


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        password = str(
            data.get(
                "password",
                ""
            )
        )


        if not email or not password:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Email and password are required",
                }
            ), 400


        conn = get_db()


        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(TRIM(email)) = ?
            LIMIT 1
            """,
            (email,),
        ).fetchone()


        if not user:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Invalid email or password",
                }
            ), 401


        if not check_password_hash(
            user["password"],
            password
        ):

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Invalid email or password",
                }
            ), 401


        session["user_id"] = int(
            user["id"]
        )

        session["user_name"] = (
            user["name"]
        )

        session["user_email"] = (
            user["email"]
        )


        return jsonify(
            {
                "success": True,

                "message":
                    "Login successful",

                "user":
                    {
                        "id":
                            int(user["id"]),

                        "name":
                            user["name"],

                        "email":
                            user["email"],
                    },
            }
        ), 200


    except Exception as error:

        print(
            "LOGIN ERROR:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Something went wrong during login",
            }
        ), 500


    finally:

        if conn:

            conn.close()
            # =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/api/logout",
    methods=["POST"]
)
def logout():

    session.clear()

    return jsonify(
        {
            "success": True,
            "message": "Logout successful"
        }
    ), 200


# =========================================================
# CURRENT USER
# =========================================================

@app.route(
    "/api/me",
    methods=["GET"]
)
def current_user():

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message": "Not logged in"
            }
        ), 401


    conn = get_db()

    try:

        user = conn.execute(
            """
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()


        if not user:

            session.clear()

            return jsonify(
                {
                    "success": False,
                    "message": "User not found"
                }
            ), 404


        return jsonify(
            {
                "success": True,

                "user":
                    {
                        "id":
                            int(user["id"]),

                        "name":
                            user["name"],

                        "email":
                            user["email"],
                    }
            }
        ), 200


    finally:

        conn.close()


# =========================================================
# GET ALL FLOWERS
# =========================================================

@app.route(
    "/api/flowers",
    methods=["GET"]
)
def get_flowers():

    conn = get_db()

    try:

        flowers = conn.execute(
            """
            SELECT
                id,
                name,
                category,
                description,
                price,
                image,
                stock,
                created_at
            FROM flowers
            ORDER BY id DESC
            """
        ).fetchall()


        result = []


        for flower in flowers:

            result.append(
                {
                    "id":
                        int(flower["id"]),

                    "name":
                        flower["name"],

                    "category":
                        flower["category"],

                    "description":
                        flower["description"],

                    "price":
                        float(
                            flower["price"] or 0
                        ),

                    # FLOWER IMAGE ONLY
                    "image":
                        flower["image"],

                    "stock":
                        int(
                            flower["stock"] or 0
                        ),

                    "created_at":
                        flower["created_at"],
                }
            )


        return jsonify(
            {
                "success": True,

                "count":
                    len(result),

                "flowers":
                    result,
            }
        ), 200


    except Exception as error:

        print(
            "Get Flowers Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to fetch flowers",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# GET SINGLE FLOWER
# =========================================================

@app.route(
    "/api/flowers/<int:flower_id>",
    methods=["GET"]
)
def get_single_flower(flower_id):

    conn = get_db()

    try:

        flower = conn.execute(
            """
            SELECT
                id,
                name,
                category,
                description,
                price,
                image,
                stock,
                created_at
            FROM flowers
            WHERE id = ?
            LIMIT 1
            """,
            (flower_id,),
        ).fetchone()


        if not flower:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Flower not found",
                }
            ), 404


        return jsonify(
            {
                "success": True,

                "flower":
                    {
                        "id":
                            int(flower["id"]),

                        "name":
                            flower["name"],

                        "category":
                            flower["category"],

                        "description":
                            flower["description"],

                        "price":
                            float(
                                flower["price"] or 0
                            ),

                        # FLOWER IMAGE ONLY
                        "image":
                            flower["image"],

                        "stock":
                            int(
                                flower["stock"] or 0
                            ),

                        "created_at":
                            flower["created_at"],
                    }
            }
        ), 200


    finally:

        conn.close()


# =========================================================
# ADD FLOWER TO CART
# =========================================================

@app.route(
    "/api/cart",
    methods=["POST"]
)
def add_to_cart():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify(
            {
                "success": False,
                "message":
                    "Request body is required",
            }
        ), 400


    session_user_id = session.get(
        "user_id"
    )


    if not session_user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login first",
            }
        ), 401


    try:

        flower_id = int(
            data.get("flower_id")
        )

        quantity = int(
            data.get(
                "quantity",
                1
            )
        )

        session_user_id = int(
            session_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid flower ID or quantity",
            }
        ), 400


    if quantity < 1:

        return jsonify(
            {
                "success": False,

                "message":
                    "Quantity must be at least 1",
            }
        ), 400


    conn = get_db()


    try:

        flower = conn.execute(
            """
            SELECT *
            FROM flowers
            WHERE id = ?
            """,
            (flower_id,),
        ).fetchone()


        if not flower:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Flower not found",
                }
            ), 404


        stock = int(
            flower["stock"] or 0
        )


        if stock <= 0:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "This flower is out of stock",
                }
            ), 400


        existing = conn.execute(
            """
            SELECT *
            FROM cart
            WHERE user_id = ?
              AND flower_id = ?
            """,
            (
                session_user_id,
                flower_id,
            ),
        ).fetchone()


        if existing:

            if existing["status"] == "Ordered":

                new_quantity = quantity

            else:

                new_quantity = (
                    int(
                        existing["quantity"]
                    )
                    + quantity
                )


            if new_quantity > stock:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            "Requested quantity exceeds available stock",
                    }
                ), 400


            conn.execute(
                """
                UPDATE cart
                SET quantity = ?,
                    status = 'In Cart'
                WHERE id = ?
                  AND user_id = ?
                """,
                (
                    new_quantity,
                    existing["id"],
                    session_user_id,
                ),
            )


        else:

            if quantity > stock:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            "Requested quantity exceeds available stock",
                    }
                ), 400


            conn.execute(
                """
                INSERT INTO cart
                (
                    user_id,
                    flower_id,
                    quantity,
                    status
                )
                VALUES (?, ?, ?, 'In Cart')
                """,
                (
                    session_user_id,
                    flower_id,
                    quantity,
                ),
            )


        conn.commit()


        return jsonify(
            {
                "success": True,

                "message":
                    "Flower added to cart",
            }
        ), 200


    except Exception as error:

        conn.rollback()


        print(
            "Add Cart Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to add flower to cart",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# GET USER CART
# =========================================================

@app.route(
    "/api/cart/<int:user_id>",
    methods=["GET"]
)
def get_cart(user_id):

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login to view cart",
            }
        ), 401


    try:

        logged_user_id = int(
            logged_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    if logged_user_id != user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "You can view only your own cart",
            }
        ), 403


    conn = get_db()


    try:

        items = conn.execute(
            """
            SELECT

                cart.id,
                cart.user_id,
                cart.flower_id,
                cart.quantity,
                cart.status,
                cart.created_at,

                flowers.name,
                flowers.category,
                flowers.description,
                flowers.price,
                flowers.image,
                flowers.stock

            FROM cart

            INNER JOIN flowers
                ON cart.flower_id = flowers.id

            WHERE cart.user_id = ?

            ORDER BY cart.id DESC
            """,
            (user_id,),
        ).fetchall()


        cart = []

        active_total = 0.0

        active_count = 0

        ordered_count = 0


        for item in items:

            quantity = int(
                item["quantity"] or 0
            )

            price = float(
                item["price"] or 0
            )

            subtotal = (
                price * quantity
            )

            status = (
                item["status"]
                or "In Cart"
            )


            if status == "Ordered":

                ordered_count += quantity

            else:

                active_count += quantity

                active_total += subtotal


            cart.append(
                {
                    "id":
                        int(item["id"]),

                    "user_id":
                        int(item["user_id"]),

                    "flower_id":
                        int(item["flower_id"]),

                    "name":
                        item["name"],

                    "category":
                        item["category"],

                    "description":
                        item["description"],

                    "price":
                        price,

                    "quantity":
                        quantity,

                    "subtotal":
                        subtotal,

                    # FLOWER IMAGE ONLY
                    "image":
                        item["image"],

                    "stock":
                        int(
                            item["stock"] or 0
                        ),

                    "status":
                        status,

                    "created_at":
                        item["created_at"],

                    "can_checkout":
                        status == "In Cart",

                    "can_update":
                        status == "In Cart",

                    "can_remove":
                        True,
                }
            )


        return jsonify(
            {
                "success": True,

                "cart":
                    cart,

                "total":
                    active_total,

                "active_total":
                    active_total,

                "active_count":
                    active_count,

                "ordered_count":
                    ordered_count,

                "count":
                    len(cart),
            }
        ), 200


    finally:

        conn.close()


# =========================================================
# UPDATE CART QUANTITY
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["PUT"]
)
def update_cart_quantity(cart_id):

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify(
            {
                "success": False,

                "message":
                    "Request body is required",
            }
        ), 400


    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login first",
            }
        ), 401


    try:

        quantity = int(
            data.get("quantity")
        )

        logged_user_id = int(
            logged_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid quantity or session",
            }
        ), 400


    if quantity < 1:

        return jsonify(
            {
                "success": False,

                "message":
                    "Quantity must be at least 1",
            }
        ), 400


    conn = get_db()


    try:

        item = conn.execute(
            """
            SELECT

                cart.*,
                flowers.stock,
                flowers.name

            FROM cart

            INNER JOIN flowers
                ON cart.flower_id = flowers.id

            WHERE cart.id = ?
              AND cart.user_id = ?
            """,
            (
                cart_id,
                logged_user_id,
            ),
        ).fetchone()


        if not item:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Cart item not found",
                }
            ), 404


        if item["status"] == "Ordered":

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Ordered item cannot be changed",
                }
            ), 400


        stock = int(
            item["stock"] or 0
        )


        if quantity > stock:

            return jsonify(
                {
                    "success": False,

                    "message":
                        f"Only {stock} items available",
                }
            ), 400


        conn.execute(
            """
            UPDATE cart

            SET quantity = ?

            WHERE id = ?
              AND user_id = ?
              AND status = 'In Cart'
            """,
            (
                quantity,
                cart_id,
                logged_user_id,
            ),
        )


        conn.commit()


        return jsonify(
            {
                "success": True,

                "message":
                    "Cart quantity updated",
            }
        ), 200


    except Exception as error:

        conn.rollback()


        print(
            "Update Cart Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to update cart",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# DELETE SINGLE CART ITEM
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["DELETE"]
)
def remove_cart_item(cart_id):

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login first",
            }
        ), 401


    try:

        logged_user_id = int(
            logged_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    conn = get_db()


    try:

        item = conn.execute(
            """
            SELECT *
            FROM cart

            WHERE id = ?
              AND user_id = ?
            """,
            (
                cart_id,
                logged_user_id,
            ),
        ).fetchone()


        if item is None:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Cart item not found",
                }
            ), 404


        conn.execute(
            """
            DELETE FROM cart

            WHERE id = ?
              AND user_id = ?
            """,
            (
                cart_id,
                logged_user_id,
            ),
        )


        selected_ids = session.get(
            "checkout_cart_ids",
            []
        )


        try:

            selected_ids = [
                int(value)
                for value in selected_ids
            ]

        except (
            TypeError,
            ValueError
        ):

            selected_ids = []


        if cart_id in selected_ids:

            selected_ids.remove(
                cart_id
            )


        session[
            "checkout_cart_ids"
        ] = selected_ids


        conn.commit()


        return jsonify(
            {
                "success": True,

                "message":
                    "Flower removed from cart",
            }
        ), 200


    except Exception as error:

        conn.rollback()


        print(
            "Remove Cart Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to remove cart item",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# CLEAR USER ACTIVE CART
# =========================================================

@app.route(
    "/api/cart/user/<int:user_id>",
    methods=["DELETE"]
)
def clear_user_cart(user_id):

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login first",
            }
        ), 401


    try:

        logged_user_id = int(
            logged_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    if logged_user_id != user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "You can clear only your own cart",
            }
        ), 403


    conn = get_db()


    try:

        conn.execute(
            """
            DELETE FROM cart

            WHERE user_id = ?

              AND status = 'In Cart'
            """,
            (user_id,),
        )


        conn.commit()


        session[
            "checkout_cart_ids"
        ] = []


        return jsonify(
            {
                "success": True,

                "message":
                    "Active cart cleared successfully",
            }
        ), 200


    except Exception as error:

        conn.rollback()


        print(
            "Clear Cart Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to clear cart",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# CHECKOUT - GET SELECTED CART ITEMS
# =========================================================

@app.route(
    "/api/checkout/selected",
    methods=["GET", "POST"]
)
def checkout_selected():

    session_user_id = session.get(
        "user_id"
    )


    if not session_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login before checkout",
            }
        ), 401


    try:

        user_id = int(
            session_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    if request.method == "POST":

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Request body is required",
                }
            ), 400


        cart_ids = data.get(
            "cart_ids",
            []
        )


    else:

        cart_ids = session.get(
            "checkout_cart_ids",
            []
        )


    if not isinstance(
        cart_ids,
        list
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "cart_ids must be a list",
            }
        ), 400


    if len(cart_ids) == 0:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please select at least one flower",
            }
        ), 400


    try:

        cart_ids = [
            int(cart_id)
            for cart_id in cart_ids
        ]


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid cart item ID",
            }
        ), 400


    cart_ids = list(
        dict.fromkeys(
            cart_ids
        )
    )


    if not cart_ids:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please select at least one flower",
            }
        ), 400


    conn = get_db()


    try:

        placeholders = ",".join(
            ["?"] * len(cart_ids)
        )


        query = f"""
            SELECT

                cart.id AS cart_id,
                cart.user_id,
                cart.flower_id,
                cart.quantity,
                cart.status,
                cart.created_at,

                flowers.name,
                flowers.category,
                flowers.description,
                flowers.price,
                flowers.image,
                flowers.stock

            FROM cart

            INNER JOIN flowers
                ON cart.flower_id = flowers.id

            WHERE cart.user_id = ?

              AND cart.id IN ({placeholders})

              AND cart.status = 'In Cart'

            ORDER BY cart.id ASC
        """


        params = [
            user_id
        ] + cart_ids


        items = conn.execute(
            query,
            params
        ).fetchall()


        if not items:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Selected cart items are not available for checkout",
                }
            ), 400


        found_ids = {
            int(item["cart_id"])
            for item in items
        }


        requested_ids = set(
            cart_ids
        )


        if found_ids != requested_ids:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "One or more selected items are unavailable or already ordered",
                }
            ), 400


        selected_items = []

        total = 0.0


        for item in items:

            price = float(
                item["price"] or 0
            )

            quantity = int(
                item["quantity"] or 0
            )

            stock = int(
                item["stock"] or 0
            )


            if quantity < 1:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            f"Invalid quantity for {item['name']}",
                    }
                ), 400


            if stock <= 0:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            f"{item['name']} is out of stock",
                    }
                ), 400


            if quantity > stock:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            f"Only {stock} units of {item['name']} are available",
                    }
                ), 400


            subtotal = (
                price * quantity
            )


            total += subtotal


            selected_items.append(
                {
                    "cart_id":
                        int(item["cart_id"]),

                    "user_id":
                        int(item["user_id"]),

                    "flower_id":
                        int(item["flower_id"]),

                    "name":
                        item["name"],

                    "category":
                        item["category"],

                    "description":
                        item["description"],

                    "price":
                        price,

                    "quantity":
                        quantity,

                    "subtotal":
                        subtotal,

                    # FLOWER IMAGE ONLY
                    "image":
                        item["image"],

                    "stock":
                        stock,

                    "status":
                        item["status"],

                    "created_at":
                        item["created_at"],
                }
            )


        session[
            "checkout_cart_ids"
        ] = cart_ids


        return jsonify(
            {
                "success": True,

                "message":
                    "Selected items loaded successfully",

                "items":
                    selected_items,

                "total":
                    total,

                "selected_count":
                    len(selected_items),

                "selected_quantity":
                    sum(
                        item["quantity"]
                        for item in selected_items
                    ),

                "selected_cart_ids":
                    cart_ids,
            }
        ), 200


    except Exception as error:

        print(
            "Checkout Selected Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to load selected checkout items",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# CREATE ORDER / CHECKOUT
# =========================================================

@app.route(
    "/api/orders",
    methods=["POST"]
)
def create_order():

    session_user_id = session.get(
        "user_id"
    )


    if not session_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login before placing an order",
            }
        ), 401


    try:

        user_id = int(
            session_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify(
            {
                "success": False,

                "message":
                    "Request body is required",
            }
        ), 400


    customer_name = str(
        data.get(
            "customer_name",
            ""
        )
    ).strip()


    phone = str(
        data.get(
            "phone",
            ""
        )
    ).strip()


    address = str(
        data.get(
            "address",
            ""
        )
    ).strip()


    payment = str(
        data.get(
            "payment",
            ""
        )
    ).strip()


    cart_ids = data.get(
        "cart_ids",
        None
    )


    if cart_ids is None:

        cart_ids = session.get(
            "checkout_cart_ids",
            []
        )


    if not customer_name:

        return jsonify(
            {
                "success": False,

                "message":
                    "Customer name is required",
            }
        ), 400


    if len(customer_name) < 2:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please enter a valid customer name",
            }
        ), 400


    if not phone:

        return jsonify(
            {
                "success": False,

                "message":
                    "Phone number is required",
            }
        ), 400


    phone_digits = "".join(
        character
        for character in phone
        if character.isdigit()
    )


    if len(phone_digits) < 10:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please enter a valid phone number",
            }
        ), 400


    if not address:

        return jsonify(
            {
                "success": False,

                "message":
                    "Address is required",
            }
        ), 400


    if not payment:

        return jsonify(
            {
                "success": False,

                "message":
                    "Payment method is required",
            }
        ), 400


    if not isinstance(
        cart_ids,
        list
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "cart_ids must be a list",
            }
        ), 400


    if len(cart_ids) == 0:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please select at least one flower",
            }
        ), 400


    try:

        cart_ids = [
            int(cart_id)
            for cart_id in cart_ids
        ]


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid cart item ID",
            }
        ), 400


    cart_ids = list(
        dict.fromkeys(
            cart_ids
        )
    )


    if not cart_ids:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please select at least one flower",
            }
        ), 400


    conn = get_db()


    try:

        user = conn.execute(
            """
            SELECT
                id,
                name,
                email
            FROM users
            WHERE id = ?
            LIMIT 1
            """,
            (user_id,),
        ).fetchone()


        if not user:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "User not found",
                }
            ), 404


        placeholders = ",".join(
            ["?"] * len(cart_ids)
        )


        query = f"""
            SELECT

                cart.id AS cart_id,
                cart.user_id,
                cart.flower_id,
                cart.quantity,
                cart.status,

                flowers.name,
                flowers.price,
                flowers.stock,
                flowers.image

            FROM cart

            INNER JOIN flowers
                ON cart.flower_id = flowers.id

            WHERE cart.user_id = ?

              AND cart.id IN ({placeholders})

              AND cart.status = 'In Cart'

            ORDER BY cart.id ASC
        """


        params = [
            user_id
        ] + cart_ids


        cart_items = conn.execute(
            query,
            params
        ).fetchall()


        if len(cart_items) != len(cart_ids):

            return jsonify(
                {
                    "success": False,

                    "message":
                        "One or more selected items are unavailable or already ordered",
                }
            ), 400


        total = 0.0


        for item in cart_items:

            stock = int(
                item["stock"] or 0
            )

            quantity = int(
                item["quantity"] or 0
            )


            if quantity < 1:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            f"Invalid quantity for {item['name']}",
                    }
                ), 400


            if stock <= 0:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            f"{item['name']} is out of stock",
                    }
                ), 400


            if quantity > stock:

                return jsonify(
                    {
                        "success": False,

                        "message":
                            f"Only {stock} units of {item['name']} are available",
                    }
                ), 400


            subtotal = (
                float(
                    item["price"] or 0
                )
                * quantity
            )


            total += subtotal


        cursor = conn.execute(
            """
            INSERT INTO orders
            (
                user_id,
                customer_name,
                phone,
                address,
                payment,
                total,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                customer_name,
                phone,
                address,
                payment,
                total,
                "Processing",
            ),
        )


        order_id = cursor.lastrowid


        created_items = []


        for item in cart_items:

            flower_id = int(
                item["flower_id"]
            )

            flower_name = item["name"]

            price = float(
                item["price"] or 0
            )

            quantity = int(
                item["quantity"] or 0
            )

            subtotal = (
                price * quantity
            )


            item_cursor = conn.execute(
                """
                INSERT INTO order_items
                (
                    order_id,
                    flower_id,
                    flower_name,
                    price,
                    quantity,
                    subtotal
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    flower_id,
                    flower_name,
                    price,
                    quantity,
                    subtotal,
                ),
            )


            order_item_id = (
                item_cursor.lastrowid
            )


            stock_update = conn.execute(
                """
                UPDATE flowers

                SET stock = stock - ?

                WHERE id = ?

                  AND stock >= ?
                """,
                (
                    quantity,
                    flower_id,
                    quantity,
                ),
            )


            if stock_update.rowcount != 1:

                raise Exception(
                    f"Stock update failed for {flower_name}"
                )


            cart_update = conn.execute(
                """
                UPDATE cart

                SET status = 'Ordered'

                WHERE id = ?

                  AND user_id = ?

                  AND status = 'In Cart'
                """,
                (
                    int(
                        item["cart_id"]
                    ),
                    user_id,
                ),
            )


            if cart_update.rowcount != 1:

                raise Exception(
                    f"Cart update failed for {flower_name}"
                )


            created_items.append(
                {
                    "id":
                        int(order_item_id),

                    "cart_id":
                        int(item["cart_id"]),

                    "flower_id":
                        flower_id,

                    "name":
                        flower_name,

                    "price":
                        price,

                    "quantity":
                        quantity,

                    "subtotal":
                        subtotal,

                    # FLOWER IMAGE ONLY
                    "image":
                        item["image"],
                }
            )


        conn.commit()


        session.pop(
            "checkout_cart_ids",
            None
        )


        return jsonify(
            {
                "success": True,

                "message":
                    "Selected items ordered successfully",

                "order":
                    {
                        "id":
                            int(order_id),

                        "user_id":
                            user_id,

                        "customer_name":
                            customer_name,

                        "phone":
                            phone,

                        "address":
                            address,

                        "payment":
                            payment,

                        "total":
                            total,

                        "status":
                            "Processing",

                        "items":
                            created_items,
                    },

                "ordered_cart_ids":
                    cart_ids,

                "selected_items_count":
                    len(created_items),

                "ordered_quantity":
                    sum(
                        item["quantity"]
                        for item in created_items
                    ),
            }
        ), 201


    except Exception as error:

        conn.rollback()


        print(
            "Create Order Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to place order. Please try again.",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# GET USER ORDERS
# =========================================================

@app.route(
    "/api/orders/user/<int:user_id>",
    methods=["GET"]
)
def get_user_orders(user_id):

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login to view orders",
            }
        ), 401


    try:

        logged_user_id = int(
            logged_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    if logged_user_id != user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "You can view only your own orders",
            }
        ), 403


    conn = get_db()


    try:

        orders = conn.execute(
            """
            SELECT

                id,
                user_id,
                customer_name,
                phone,
                address,
                payment,
                total,
                status,
                created_at

            FROM orders

            WHERE user_id = ?

            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()


        result = []

        total_ordered_quantity = 0


        for order in orders:

            items = conn.execute(
                """
                SELECT

                    id,
                    order_id,
                    flower_id,
                    flower_name,
                    price,
                    quantity,
                    subtotal

                FROM order_items

                WHERE order_id = ?

                ORDER BY id ASC
                """,
                (
                    order["id"],
                ),
            ).fetchall()


            item_list = []

            order_quantity = 0


            for item in items:

                quantity = int(
                    item["quantity"] or 0
                )


                order_quantity += quantity

                total_ordered_quantity += quantity


                item_list.append(
                    {
                        "id":
                            int(item["id"]),

                        "order_id":
                            int(item["order_id"]),

                        "flower_id":
                            int(item["flower_id"]),

                        "name":
                            item["flower_name"],

                        "price":
                            float(
                                item["price"] or 0
                            ),

                        "quantity":
                            quantity,

                        "subtotal":
                            float(
                                item["subtotal"] or 0
                            ),
                    }
                )


            result.append(
                {
                    "id":
                        int(order["id"]),

                    "user_id":
                        int(order["user_id"]),

                    "customer_name":
                        order["customer_name"],

                    "phone":
                        order["phone"],

                    "address":
                        order["address"],

                    "payment":
                        order["payment"],

                    "total":
                        float(
                            order["total"] or 0
                        ),

                    "status":
                        order["status"],

                    "created_at":
                        order["created_at"],

                    "quantity":
                        order_quantity,

                    "items":
                        item_list,
                }
            )


        return jsonify(
            {
                "success": True,

                "count":
                    len(result),

                "ordered_quantity":
                    total_ordered_quantity,

                "orders":
                    result,
            }
        ), 200


    except Exception as error:

        print(
            "Get User Orders Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to fetch your orders",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# GET ALL ORDERS
# =========================================================

@app.route(
    "/api/orders",
    methods=["GET"]
)
def get_all_orders():

    if not session.get(
        "user_id"
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login to view orders",
            }
        ), 401


    conn = get_db()


    try:

        orders = conn.execute(
            """
            SELECT

                id,
                user_id,
                customer_name,
                phone,
                address,
                payment,
                total,
                status,
                created_at

            FROM orders

            ORDER BY id DESC
            """
        ).fetchall()


        result = []


        for order in orders:

            items = conn.execute(
                """
                SELECT

                    id,
                    order_id,
                    flower_id,
                    flower_name,
                    price,
                    quantity,
                    subtotal

                FROM order_items

                WHERE order_id = ?

                ORDER BY id ASC
                """,
                (
                    order["id"],
                ),
            ).fetchall()


            item_list = []

            order_quantity = 0


            for item in items:

                quantity = int(
                    item["quantity"] or 0
                )


                order_quantity += quantity


                item_list.append(
                    {
                        "id":
                            int(item["id"]),

                        "order_id":
                            int(item["order_id"]),

                        "flower_id":
                            int(item["flower_id"]),

                        "name":
                            item["flower_name"],

                        "price":
                            float(
                                item["price"] or 0
                            ),

                        "quantity":
                            quantity,

                        "subtotal":
                            float(
                                item["subtotal"] or 0
                            ),
                    }
                )


            result.append(
                {
                    "id":
                        int(order["id"]),

                    "user_id":
                        int(order["user_id"]),

                    "customer_name":
                        order["customer_name"],

                    "phone":
                        order["phone"],

                    "address":
                        order["address"],

                    "payment":
                        order["payment"],

                    "total":
                        float(
                            order["total"] or 0
                        ),

                    "status":
                        order["status"],

                    "created_at":
                        order["created_at"],

                    "quantity":
                        order_quantity,

                    "items":
                        item_list,
                }
            )


        return jsonify(
            {
                "success": True,

                "count":
                    len(result),

                "orders":
                    result,
            }
        ), 200


    except Exception as error:

        print(
            "Get All Orders Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to fetch orders",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# DELETE ORDER
# =========================================================

@app.route(
    "/api/orders/<int:order_id>",
    methods=["DELETE"]
)
def delete_order(order_id):

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify(
            {
                "success": False,

                "message":
                    "Please login before deleting an order",
            }
        ), 401


    try:

        logged_user_id = int(
            logged_user_id
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Invalid session",
            }
        ), 401


    conn = get_db()


    try:

        order = conn.execute(
            """
            SELECT *
            FROM orders
            WHERE id = ?
            LIMIT 1
            """,
            (order_id,),
        ).fetchone()


        if not order:

            return jsonify(
                {
                    "success": False,

                    "message":
                        "Order not found",
                }
            ), 404


        if logged_user_id != int(
            order["user_id"]
        ):

            return jsonify(
                {
                    "success": False,

                    "message":
                        "You can delete only your own orders",
                }
            ), 403


        order_items = conn.execute(
            """
            SELECT

                flower_id,
                quantity

            FROM order_items

            WHERE order_id = ?
            """,
            (order_id,),
        ).fetchall()


        # =================================================
        # RESTORE FLOWER STOCK
        # =================================================

        for item in order_items:

            flower_id = int(
                item["flower_id"]
            )

            quantity = int(
                item["quantity"]
            )


            conn.execute(
                """
                UPDATE flowers

                SET stock = stock + ?

                WHERE id = ?
                """,
                (
                    quantity,
                    flower_id,
                ),
            )


        # =================================================
        # DELETE ORDER ITEMS
        # =================================================

        conn.execute(
            """
            DELETE FROM order_items

            WHERE order_id = ?
            """,
            (order_id,),
        )


        # =================================================
        # DELETE ORDER
        # =================================================

        conn.execute(
            """
            DELETE FROM orders

            WHERE id = ?
            """,
            (order_id,),
        )


        # =================================================
        # REMOVE ORDERED CART ITEMS
        # =================================================

        flower_ids = [
            int(item["flower_id"])
            for item in order_items
        ]


        if flower_ids:

            placeholders = ",".join(
                ["?"] * len(flower_ids)
            )


            conn.execute(
                f"""
                DELETE FROM cart

                WHERE user_id = ?

                  AND status = 'Ordered'

                  AND flower_id IN ({placeholders})
                """,
                [
                    logged_user_id
                ] + flower_ids,
            )


        conn.commit()


        return jsonify(
            {
                "success": True,

                "message":
                    "Order deleted successfully and stock restored",
            }
        ), 200


    except Exception as error:

        conn.rollback()


        print(
            "Delete Order Error:",
            error
        )


        return jsonify(
            {
                "success": False,

                "message":
                    "Unable to delete order",
            }
        ), 500


    finally:

        conn.close()


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health_check():

    return jsonify(
        {
            "success": True,

            "message":
                "Blossom Flower Shop backend is working",
        }
    ), 200


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "API endpoint not found",
            }
        ), 404


    template_path = os.path.join(
        BASE_DIR,
        "templates",
        "404.html",
    )


    if os.path.exists(
        template_path
    ):

        return (
            render_template(
                "404.html"
            ),
            404,
        )


    return (
        "Page not found",
        404,
    )


@app.errorhandler(405)
def method_not_allowed(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Method not allowed",
            }
        ), 405


    return (
        "Method not allowed",
        405,
    )


@app.errorhandler(500)
def internal_server_error(error):

    if request.path.startswith(
        "/api/"
    ):

        return jsonify(
            {
                "success": False,

                "message":
                    "Internal server error",
            }
        ), 500


    return (
        "Internal server error",
        500,
    )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000,
        )
    )


    debug_mode = (
        os.environ.get(
            "FLASK_DEBUG",
            "true",
        ).lower()
        == "true"
    )


    print("")

    print(
        "=========================================="
    )

    print(
        "🌸 BLOSSOM FLOWER SHOP"
    )

    print(
        "=========================================="
    )

    print("")


    print("Server:")

    print(
        f"http://127.0.0.1:{port}"
    )


    print("")


    print("Flowers:")

    print(
        f"http://127.0.0.1:{port}/flower"
    )


    print("")


    print("Flower API:")

    print(
        f"http://127.0.0.1:{port}/api/flowers"
    )


    print("")


    print("Cart API:")

    print(
        f"http://127.0.0.1:{port}/api/cart/<user_id>"
    )


    print("")


    print("Selected Checkout API:")

    print(
        f"http://127.0.0.1:{port}/api/checkout/selected"
    )


    print("")


    print("Order API:")

    print(
        f"http://127.0.0.1:{port}/api/orders"
    )


    print("")


    print("Orders:")

    print(
        f"http://127.0.0.1:{port}/orders"
    )


    print("")


    print("Health:")

    print(
        f"http://127.0.0.1:{port}/api/health"
    )


    print("")


    print("Swagger:")

    print(
        f"http://127.0.0.1:{port}/apidocs/"
    )


    print("")


    print("API JSON:")

    print(
        f"http://127.0.0.1:{port}/apispec_1.json"
    )


    print("")

    print(
        "=========================================="
    )

    print("")


    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode,
    )