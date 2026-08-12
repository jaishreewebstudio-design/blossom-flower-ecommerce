from flask import (
    Flask,
    jsonify,
    request,
    render_template,
    send_from_directory,
    session,
    redirect
)

from flask_cors import CORS
from flasgger import Swagger

import sqlite3
import os

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# SECRET KEY
# =========================================================

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "blossom_flower_shop_secret_key_2026"
)


# =========================================================
# SESSION CONFIGURATION
# =========================================================

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

if os.environ.get("RENDER"):
    app.config["SESSION_COOKIE_SECURE"] = True
else:
    app.config["SESSION_COOKIE_SECURE"] = False


# =========================================================
# CORS
# =========================================================

CORS(
    app,
    supports_credentials=True
)


# =========================================================
# SWAGGER CONFIGURATION
# =========================================================

swagger_template = {

    "swagger": "2.0",

    "info": {
        "title": "Blossom Flower Shop API",

        "description": """
Complete API documentation for Blossom Flower Shop.

Features:

- User Registration
- User Login
- User Session
- Logout
- Forgot Password
- Flowers
- Shopping Cart
- Selective Checkout
- Orders
- Health Check
""",

        "version": "5.0.0"
    },

    "basePath": "/",

    "schemes": [
        "http",
        "https"
    ],

    "consumes": [
        "application/json"
    ],

    "produces": [
        "application/json"
    ],

    "tags": [

        {
            "name": "Authentication",
            "description":
                "Registration, login, logout and user session"
        },

        {
            "name": "Flowers",
            "description":
                "Flower APIs"
        },

        {
            "name": "Cart",
            "description":
                "Shopping cart APIs and selective cart checkout"
        },

        {
            "name": "Orders",
            "description":
                "Checkout and order APIs"
        },

        {
            "name": "System",
            "description":
                "System and health APIs"
        }
    ]
}


swagger = Swagger(
    app,
    template=swagger_template
)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# DATABASE
# =========================================================

DATABASE = os.path.join(
    BASE_DIR,
    "flower_shop.db"
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    conn = sqlite3.connect(
        DATABASE
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def init_db():

    conn = get_db()


    # =====================================================
    # USERS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            password TEXT NOT NULL,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =====================================================
    # FLOWERS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS flowers (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            category TEXT NOT NULL,

            description TEXT,

            price REAL NOT NULL,

            image TEXT,

            stock INTEGER DEFAULT 10
        )
    """)


    # =====================================================
    # CART
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS cart (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            flower_id INTEGER NOT NULL,

            quantity INTEGER DEFAULT 1,

            status TEXT DEFAULT 'In Cart',

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(user_id, flower_id)
        )
    """)


    # =====================================================
    # CHECK CART COLUMNS
    # =====================================================

    cart_columns = conn.execute(
        "PRAGMA table_info(cart)"
    ).fetchall()

    cart_column_names = [
        column["name"]
        for column in cart_columns
    ]


    if "status" not in cart_column_names:

        conn.execute("""
            ALTER TABLE cart
            ADD COLUMN status TEXT
            DEFAULT 'In Cart'
        """)


    # =====================================================
    # FIX NULL CART STATUS
    # =====================================================

    conn.execute("""
        UPDATE cart

        SET status = 'In Cart'

        WHERE status IS NULL

        OR status = ''
    """)


    # =====================================================
    # ORDERS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            customer_name TEXT NOT NULL,

            phone TEXT NOT NULL,

            address TEXT NOT NULL,

            payment TEXT NOT NULL,

            total REAL NOT NULL,

            status TEXT DEFAULT 'Processing',

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # =====================================================
    # ORDER ITEMS
    # =====================================================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            order_id INTEGER NOT NULL,

            flower_id INTEGER NOT NULL,

            flower_name TEXT NOT NULL,

            price REAL NOT NULL,

            quantity INTEGER NOT NULL,

            subtotal REAL NOT NULL
        )
    """)


    # =====================================================
    # DEFAULT FLOWERS
    # =====================================================

    count = conn.execute(
        "SELECT COUNT(*) FROM flowers"
    ).fetchone()[0]


    if count == 0:

        flowers = [

            (
                "Red Rose",
                "Rose",
                "Fresh red roses, perfect for love and special occasions.",
                499,
                "https://images.unsplash.com/photo-1496062031456-07b8f162a322",
                25
            ),

            (
                "White Lily",
                "Lily",
                "Beautiful fresh white lilies with an elegant fragrance.",
                599,
                "https://images.unsplash.com/photo-1597848212624-e19f1f68c8b6",
                20
            ),

            (
                "Pink Tulip",
                "Tulip",
                "Fresh pink tulips that bring beauty and happiness.",
                449,
                "https://images.unsplash.com/photo-1520763185298-1b434c919102",
                30
            ),

            (
                "Yellow Sunflower",
                "Sunflower",
                "Bright yellow sunflowers to make every day cheerful.",
                399,
                "https://images.unsplash.com/photo-1597848212624-e19f1f68c8b6",
                15
            ),

            (
                "Pink Rose",
                "Rose",
                "Soft pink roses suitable for gifts and celebrations.",
                549,
                "https://images.unsplash.com/photo-1518709268805-4e9042af9f23",
                18
            ),

            (
                "Orange Lily",
                "Lily",
                "Beautiful orange lilies with vibrant natural colors.",
                649,
                "https://images.unsplash.com/photo-1490750967868-88aa4486c946",
                12
            )
        ]


        conn.executemany("""
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
        """, flowers)


    conn.commit()

    conn.close()


# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# FRONTEND PAGE ROUTES
# =========================================================

@app.route("/")
def index():

    return render_template(
        "register.html"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/home")
def home_page():

    return render_template(
        "home.html"
    )


@app.route("/home.html")
def home_html():

    return render_template(
        "home.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )


@app.route("/login.html")
def login_html():

    return render_template(
        "login.html"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password")
def forgot_password_page():

    return render_template(
        "forgot-password.html"
    )


@app.route("/forgot-password.html")
def forgot_password_html():

    return render_template(
        "forgot-password.html"
    )


# =========================================================
# REGISTER
# =========================================================

@app.route("/register")
def register_page():

    return render_template(
        "register.html"
    )


@app.route("/register.html")
def register_html():

    return render_template(
        "register.html"
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard_page():

    return render_template(
        "dashboard.html"
    )


@app.route("/dashboard.html")
def dashboard_html():

    return render_template(
        "dashboard.html"
    )


# =========================================================
# FLOWERS
# =========================================================

@app.route("/flower")
def flower_page():

    return render_template(
        "flower.html"
    )


@app.route("/flower.html")
def flower_html():

    return render_template(
        "flower.html"
    )


@app.route("/flowers")
def flowers_page():

    return render_template(
        "flower.html"
    )


# =========================================================
# CART
# =========================================================

@app.route("/cart")
def cart_page():

    return render_template(
        "cart.html"
    )


@app.route("/cart.html")
def cart_html():

    return render_template(
        "cart.html"
    )


# =========================================================
# CHECKOUT
# =========================================================

@app.route("/checkout")
def checkout_page():

    return render_template(
        "checkout.html"
    )


@app.route("/checkout.html")
def checkout_html():

    return render_template(
        "checkout.html"
    )


# =========================================================
# ORDERS
# =========================================================

@app.route("/orders")
def orders_page():

    return render_template(
        "orders.html"
    )


@app.route("/orders.html")
def orders_html():

    return render_template(
        "orders.html"
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about_page():

    return render_template(
        "about.html"
    )


@app.route("/about.html")
def about_html():

    return render_template(
        "about.html"
    )


# =========================================================
# CONTACT
# =========================================================

@app.route("/contact")
def contact_page():

    return render_template(
        "contact.html"
    )


@app.route("/contact.html")
def contact_html():

    return render_template(
        "contact.html"
    )


# =========================================================
# STYLE.CSS
# =========================================================

@app.route("/style.css")
def style_css():

    return send_from_directory(
        BASE_DIR,
        "style.css"
    )


# =========================================================
# JAVASCRIPT FILES
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
def home_api():
    """
    API Home
    ---
    tags:
      - System
    responses:
      200:
        description: API is running
    """

    return jsonify({

        "success": True,

        "message":
            "Blossom Flower Shop API is running"

    })


# =========================================================
# REGISTER API
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    """

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


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


    if (
        not name
        or not email
        or not password
    ):

        return jsonify({

            "success": False,

            "message":
                "Name, email and password are required"

        }), 400


    if len(password) < 6:

        return jsonify({

            "success": False,

            "message":
                "Password must be at least 6 characters"

        }), 400


    conn = get_db()


    existing = conn.execute(
        """
        SELECT id
        FROM users
        WHERE LOWER(TRIM(email)) = ?
        LIMIT 1
        """,
        (email,)
    ).fetchone()


    if existing:

        conn.close()

        return jsonify({

            "success": False,

            "registered": True,

            "message":
                "Email already registered. Please login."

        }), 409


    hashed_password = generate_password_hash(
        password
    )


    cursor = conn.execute(
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
            hashed_password
        )
    )


    user_id = cursor.lastrowid


    conn.commit()

    conn.close()


    return jsonify({

        "success": True,

        "registered": True,

        "message":
            "Registration successful. You can now login.",

        "user": {

            "id":
                user_id,

            "name":
                name,

            "email":
                email
        }

    }), 201


# =========================================================
# LOGIN API
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login():
    """
    Login user
    ---
    tags:
      - Authentication
    """

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


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

        return jsonify({

            "success": False,

            "message":
                "Email and password are required"

        }), 400


    conn = get_db()


    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE LOWER(TRIM(email)) = ?
        LIMIT 1
        """,
        (email,)
    ).fetchone()


    conn.close()


    if not user:

        return jsonify({

            "success": False,

            "registered": False,

            "message":
                "Please register first. This email is not registered."

        }), 404


    if not check_password_hash(
        user["password"],
        password
    ):

        return jsonify({

            "success": False,

            "registered": True,

            "message":
                "Incorrect password. Please try again."

        }), 401


    session.clear()


    session["user_id"] = user["id"]

    session["user_name"] = user["name"]

    session["user_email"] = user["email"]

    session.permanent = True


    return jsonify({

        "success": True,

        "registered": True,

        "message":
            "Login successful",

        "user": {

            "id":
                user["id"],

            "name":
                user["name"],

            "email":
                user["email"]
        }

    }), 200


# =========================================================
# CURRENT USER
# =========================================================

@app.route(
    "/api/me",
    methods=["GET"]
)
def get_current_user():
    """
    Get currently logged-in user
    ---
    tags:
      - Authentication
    """

    user_id = session.get(
        "user_id"
    )


    if not user_id:

        return jsonify({

            "success": False,

            "logged_in": False,

            "message":
                "User is not logged in"

        }), 401


    return jsonify({

        "success": True,

        "logged_in": True,

        "user": {

            "id":
                session.get(
                    "user_id"
                ),

            "name":
                session.get(
                    "user_name"
                ),

            "email":
                session.get(
                    "user_email"
                )
        }

    })


# =========================================================
# LOGOUT PAGE
# =========================================================

@app.route(
    "/logout",
    methods=["GET"]
)
def logout_page():

    session.clear()

    return redirect("/login")


# =========================================================
# LOGOUT API
# =========================================================

@app.route(
    "/api/logout",
    methods=["GET", "POST"]
)
def logout():

    session.clear()


    if request.method == "GET":

        return redirect("/login")


    return jsonify({

        "success": True,

        "message":
            "Logout successful",

        "redirect":
            "/login"

    }), 200


# =========================================================
# FORGOT PASSWORD API
# =========================================================

@app.route(
    "/api/forgot-password",
    methods=["POST"]
)
def forgot_password():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({

                "success": False,

                "message":
                    "Request body is required"

            }), 400


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip().lower()


        new_password = str(
            data.get(
                "new_password",
                ""
            )
        )


        confirm_password = str(
            data.get(
                "confirm_password",
                ""
            )
        )


        if not email:

            return jsonify({

                "success": False,

                "message":
                    "Email is required"

            }), 400


        if len(new_password) < 6:

            return jsonify({

                "success": False,

                "message":
                    "Password must be at least 6 characters"

            }), 400


        if new_password != confirm_password:

            return jsonify({

                "success": False,

                "message":
                    "Passwords do not match"

            }), 400


        conn = get_db()


        user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(TRIM(email)) = ?
            LIMIT 1
            """,
            (email,)
        ).fetchone()


        if user is None:

            conn.close()

            return jsonify({

                "success": False,

                "message":
                    "This email is not registered. Please register first."

            }), 404


        hashed_password = generate_password_hash(
            new_password
        )


        conn.execute(
            """
            UPDATE users

            SET password = ?

            WHERE id = ?
            """,
            (
                hashed_password,
                user["id"]
            )
        )


        conn.commit()

        conn.close()


        return jsonify({

            "success": True,

            "message":
                "Password reset successful. Please login with your new password."

        }), 200


    except Exception as error:

        print(
            "Forgot Password Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Something went wrong while resetting your password."

        }), 500


# =========================================================
# GET ALL FLOWERS
# =========================================================

@app.route(
    "/api/flowers",
    methods=["GET"]
)
def get_flowers():
    """
    Get all flowers
    ---
    tags:
      - Flowers
    """

    try:

        conn = get_db()


        flowers = conn.execute(
            """
            SELECT *
            FROM flowers
            ORDER BY id DESC
            """
        ).fetchall()


        conn.close()


        flower_list = []


        for flower in flowers:

            flower_list.append({

                "id":
                    flower["id"],

                "name":
                    flower["name"],

                "category":
                    flower["category"],

                "description":
                    flower["description"],

                "price":
                    flower["price"],

                "image":
                    flower["image"],

                "stock":
                    flower["stock"]

            })


        return jsonify({

            "success": True,

            "message":
                "Flowers fetched successfully",

            "flowers":
                flower_list

        }), 200


    except Exception as error:

        print(
            "Get Flowers Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to fetch flowers"

        }), 500


# =========================================================
# GET SINGLE FLOWER
# =========================================================

@app.route(
    "/api/flowers/<int:flower_id>",
    methods=["GET"]
)
def get_flower(flower_id):
    """
    Get single flower
    ---
    tags:
      - Flowers
    """

    conn = get_db()


    flower = conn.execute(
        """
        SELECT *
        FROM flowers
        WHERE id = ?
        """,
        (flower_id,)
    ).fetchone()


    conn.close()


    if flower is None:

        return jsonify({

            "success": False,

            "message":
                "Flower not found"

        }), 404


    return jsonify({

        "success": True,

        "flower": {

            "id":
                flower["id"],

            "name":
                flower["name"],

            "category":
                flower["category"],

            "description":
                flower["description"],

            "price":
                flower["price"],

            "image":
                flower["image"],

            "stock":
                flower["stock"]

        }

    }), 200


# =========================================================
# ADD TO CART
# =========================================================

@app.route(
    "/api/cart",
    methods=["POST"]
)
def add_to_cart():
    """
    Add flower to cart
    ---
    tags:
      - Cart
    """

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


    # -----------------------------------------------------
    # USER
    # -----------------------------------------------------

    session_user_id = session.get(
        "user_id"
    )


    if not session_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login before adding items to cart"

        }), 401


    try:

        session_user_id = int(
            session_user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid session"

        }), 401


    flower_id = data.get(
        "flower_id"
    )


    quantity = data.get(
        "quantity",
        1
    )


    try:

        flower_id = int(
            flower_id
        )

        quantity = int(
            quantity
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid flower or quantity"

        }), 400


    if quantity < 1:

        return jsonify({

            "success": False,

            "message":
                "Quantity must be at least 1"

        }), 400


    conn = get_db()


    try:

        flower = conn.execute(
            """
            SELECT *
            FROM flowers
            WHERE id = ?
            """,
            (flower_id,)
        ).fetchone()


        if not flower:

            return jsonify({

                "success": False,

                "message":
                    "Flower not found"

            }), 404


        if flower["stock"] <= 0:

            return jsonify({

                "success": False,

                "message":
                    "This flower is out of stock"

            }), 400


        existing = conn.execute(
            """
            SELECT *
            FROM cart

            WHERE user_id = ?

            AND flower_id = ?
            """,
            (
                session_user_id,
                flower_id
            )
        ).fetchone()


        if existing:

            if existing["status"] == "Ordered":

                new_quantity = quantity

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
                        session_user_id
                    )
                )

            else:

                new_quantity = (
                    int(existing["quantity"])
                    + quantity
                )


                if new_quantity > flower["stock"]:

                    return jsonify({

                        "success": False,

                        "message":
                            "Requested quantity exceeds available stock"

                    }), 400


                conn.execute(
                    """
                    UPDATE cart

                    SET quantity = ?

                    WHERE id = ?

                    AND user_id = ?
                    """,
                    (
                        new_quantity,
                        existing["id"],
                        session_user_id
                    )
                )

        else:

            if quantity > flower["stock"]:

                return jsonify({

                    "success": False,

                    "message":
                        "Requested quantity exceeds available stock"

                }), 400


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
                    quantity
                )
            )


        conn.commit()


        return jsonify({

            "success": True,

            "message":
                "Flower added to cart"

        }), 200


    except Exception as error:

        conn.rollback()

        print(
            "Add Cart Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to add flower to cart"

        }), 500


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
    """
    Get user cart
    ---
    tags:
      - Cart
    """

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login to view cart"

        }), 401


    try:

        logged_user_id = int(
            logged_user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid session"

        }), 401


    if logged_user_id != int(user_id):

        return jsonify({

            "success": False,

            "message":
                "You can view only your own cart"

        }), 403


    conn = get_db()


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

            flowers.price,

            flowers.image,

            flowers.stock

        FROM cart

        JOIN flowers

            ON cart.flower_id = flowers.id

        WHERE cart.user_id = ?

        ORDER BY cart.id DESC
        """,
        (user_id,)
    ).fetchall()


    conn.close()


    cart = []

    active_total = 0.0

    active_count = 0

    ordered_count = 0


    for item in items:

        quantity = int(
            item["quantity"]
        )


        price = float(
            item["price"]
        )


        subtotal = (
            price * quantity
        )


        status = (
            item["status"]
            or "In Cart"
        )


        if status == "Ordered":

            ordered_count += 1

        else:

            active_count += 1

            active_total += subtotal


        cart.append({

            "id":
                item["id"],

            "user_id":
                item["user_id"],

            "flower_id":
                item["flower_id"],

            "name":
                item["name"],

            "price":
                price,

            "quantity":
                quantity,

            "subtotal":
                subtotal,

            "image":
                item["image"],

            "stock":
                item["stock"],

            "status":
                status,

            "created_at":
                item["created_at"],

            "can_checkout":
                status == "In Cart"

        })


    return jsonify({

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
            len(cart)

    }), 200


# =========================================================
# UPDATE CART QUANTITY
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["PUT"]
)
def update_cart_quantity(cart_id):
    """
    Update cart quantity
    ---
    tags:
      - Cart
    """

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login first"

        }), 401


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

        return jsonify({

            "success": False,

            "message":
                "Invalid quantity or session"

        }), 400


    if quantity < 1:

        return jsonify({

            "success": False,

            "message":
                "Quantity must be at least 1"

        }), 400


    conn = get_db()


    try:

        item = conn.execute(
            """
            SELECT

                cart.*,

                flowers.stock,

                flowers.name

            FROM cart

            JOIN flowers

                ON cart.flower_id =
                   flowers.id

            WHERE cart.id = ?

            AND cart.user_id = ?
            """,
            (
                cart_id,
                logged_user_id
            )
        ).fetchone()


        if not item:

            return jsonify({

                "success": False,

                "message":
                    "Cart item not found"

            }), 404


        if item["status"] == "Ordered":

            return jsonify({

                "success": False,

                "message":
                    "Ordered item cannot be changed"

            }), 400


        if quantity > item["stock"]:

            return jsonify({

                "success": False,

                "message":
                    f"Only {item['stock']} items available"

            }), 400


        conn.execute(
            """
            UPDATE cart

            SET quantity = ?

            WHERE id = ?

            AND user_id = ?
            """,
            (
                quantity,
                cart_id,
                logged_user_id
            )
        )


        conn.commit()


        return jsonify({

            "success": True,

            "message":
                "Cart quantity updated"

        }), 200


    except Exception as error:

        conn.rollback()

        print(
            "Update Cart Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to update cart"

        }), 500


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
    """
    Delete cart item
    ---
    tags:
      - Cart
    """

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login first"

        }), 401


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
                logged_user_id
            )
        ).fetchone()


        if item is None:

            return jsonify({

                "success": False,

                "message":
                    "Cart item not found"

            }), 404


        conn.execute(
            """
            DELETE FROM cart

            WHERE id = ?

            AND user_id = ?
            """,
            (
                cart_id,
                logged_user_id
            )
        )


        conn.commit()


        return jsonify({

            "success": True,

            "message":
                "Flower removed from cart"

        }), 200


    except Exception as error:

        conn.rollback()

        print(
            "Remove Cart Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to remove cart item"

        }), 500


    finally:

        conn.close()


# =========================================================
# CLEAR USER CART
# =========================================================

@app.route(
    "/api/cart/user/<int:user_id>",
    methods=["DELETE"]
)
def clear_user_cart(user_id):
    """
    Clear user's active cart
    ---
    tags:
      - Cart
    """

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login first"

        }), 401


    if int(logged_user_id) != int(user_id):

        return jsonify({

            "success": False,

            "message":
                "You can clear only your own cart"

        }), 403


    conn = get_db()


    try:

        conn.execute(
            """
            DELETE FROM cart

            WHERE user_id = ?

            AND status = 'In Cart'
            """,
            (user_id,)
        )


        conn.commit()


        return jsonify({

            "success": True,

            "message":
                "Active cart cleared successfully"

        }), 200


    except Exception as error:

        conn.rollback()

        print(
            "Clear Cart Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to clear cart"

        }), 500


    finally:

        conn.close()


# =========================================================
# CHECK SELECTED CART ITEMS
# =========================================================

@app.route(
    "/api/checkout/selected",
    methods=["POST"]
)
def checkout_selected():
    """
    Get ONLY selected cart items for checkout.
    No other cart item is included.
    ---
    tags:
      - Cart
    """

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


    user_id = session.get(
        "user_id"
    )


    if not user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login before checkout"

        }), 401


    cart_ids = data.get(
        "cart_ids",
        []
    )


    if not isinstance(
        cart_ids,
        list
    ):

        return jsonify({

            "success": False,

            "message":
                "cart_ids must be a list"

        }), 400


    if len(cart_ids) == 0:

        return jsonify({

            "success": False,

            "message":
                "Please select at least one flower"

        }), 400


    try:

        cart_ids = [
            int(cart_id)
            for cart_id in cart_ids
        ]

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid cart item ID"

        }), 400


    cart_ids = list(
        dict.fromkeys(
            cart_ids
        )
    )


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

                flowers.name,

                flowers.price,

                flowers.image,

                flowers.stock

            FROM cart

            JOIN flowers

                ON cart.flower_id =
                   flowers.id

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

            return jsonify({

                "success": False,

                "message":
                    "Selected items are not available for checkout"

            }), 400


        found_ids = {
            item["cart_id"]
            for item in items
        }


        if len(found_ids) != len(cart_ids):

            return jsonify({

                "success": False,

                "message":
                    "One or more selected items are unavailable or already ordered"

            }), 400


        selected_items = []

        total = 0.0


        for item in items:

            price = float(
                item["price"]
            )

            quantity = int(
                item["quantity"]
            )

            subtotal = (
                price * quantity
            )


            if item["stock"] <= 0:

                return jsonify({

                    "success": False,

                    "message":
                        f"{item['name']} is out of stock"

                }), 400


            if quantity > item["stock"]:

                return jsonify({

                    "success": False,

                    "message":
                        f"Not enough stock for {item['name']}"

                }), 400


            total += subtotal


            selected_items.append({

                "cart_id":
                    item["cart_id"],

                "flower_id":
                    item["flower_id"],

                "name":
                    item["name"],

                "price":
                    price,

                "quantity":
                    quantity,

                "subtotal":
                    subtotal,

                "image":
                    item["image"],

                "stock":
                    item["stock"]

            })


        return jsonify({

            "success": True,

            "items":
                selected_items,

            "total":
                total,

            "selected_count":
                len(selected_items)

        }), 200


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
    """
    Create order ONLY from selected cart items.
    ---
    tags:
      - Orders
    """

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "Request body is required"

        }), 400


    # =====================================================
    # LOGIN CHECK
    # =====================================================

    session_user_id = session.get(
        "user_id"
    )


    if not session_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login before placing an order"

        }), 401


    try:

        session_user_id = int(
            session_user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid session"

        }), 401


    user_id = session_user_id


    # =====================================================
    # CUSTOMER DETAILS
    # =====================================================

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


    # =====================================================
    # SELECTED CART IDS
    # =====================================================

    cart_ids = data.get(
        "cart_ids",
        []
    )


    # =====================================================
    # VALIDATION
    # =====================================================

    if (
        not customer_name
        or not phone
        or not address
        or not payment
    ):

        return jsonify({

            "success": False,

            "message":
                "All customer details are required"

        }), 400


    if len(customer_name) < 2:

        return jsonify({

            "success": False,

            "message":
                "Please enter a valid customer name"

        }), 400


    if len(phone) < 10:

        return jsonify({

            "success": False,

            "message":
                "Please enter a valid phone number"

        }), 400


    if not isinstance(
        cart_ids,
        list
    ):

        return jsonify({

            "success": False,

            "message":
                "cart_ids must be a list"

        }), 400


    if len(cart_ids) == 0:

        return jsonify({

            "success": False,

            "message":
                "Please select at least one flower"

        }), 400


    try:

        cart_ids = [
            int(cart_id)
            for cart_id in cart_ids
        ]

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid cart item ID"

        }), 400


    cart_ids = list(
        dict.fromkeys(
            cart_ids
        )
    )


    conn = get_db()


    try:

        # =================================================
        # CHECK USER
        # =================================================

        user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            """,
            (user_id,)
        ).fetchone()


        if not user:

            return jsonify({

                "success": False,

                "message":
                    "User not found"

            }), 404


        # =================================================
        # GET ONLY SELECTED ITEMS
        # =================================================

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

                flowers.stock

            FROM cart

            JOIN flowers

                ON cart.flower_id =
                   flowers.id

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


        # =================================================
        # IMPORTANT:
        # ONLY SELECTED ITEMS MUST BE FOUND
        # =================================================

        if len(cart_items) != len(cart_ids):

            return jsonify({

                "success": False,

                "message":
                    "One or more selected items are unavailable or already ordered"

            }), 400


        # =================================================
        # CHECK STOCK
        # =================================================

        for item in cart_items:

            if item["stock"] <= 0:

                return jsonify({

                    "success": False,

                    "message":
                        f"{item['name']} is out of stock"

                }), 400


            if item["quantity"] > item["stock"]:

                return jsonify({

                    "success": False,

                    "message":
                        f"Not enough stock for {item['name']}"

                }), 400


        # =================================================
        # CALCULATE SELECTED TOTAL ONLY
        # =================================================

        total = 0.0


        for item in cart_items:

            total += (
                float(item["price"])
                * int(item["quantity"])
            )


        # =================================================
        # CREATE ORDER
        # =================================================

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
                "Processing"
            )
        )


        order_id = cursor.lastrowid


        # =================================================
        # INSERT ONLY SELECTED ORDER ITEMS
        # =================================================

        for item in cart_items:

            subtotal = (
                float(item["price"])
                * int(item["quantity"])
            )


            conn.execute(
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
                    item["flower_id"],
                    item["name"],
                    item["price"],
                    item["quantity"],
                    subtotal
                )
            )


            # =================================================
            # REDUCE STOCK ONLY FOR SELECTED ITEM
            # =================================================

            stock_update = conn.execute(
                """
                UPDATE flowers

                SET stock = stock - ?

                WHERE id = ?

                AND stock >= ?
                """,
                (
                    item["quantity"],
                    item["flower_id"],
                    item["quantity"]
                )
            )


            if stock_update.rowcount != 1:

                raise Exception(
                    f"Stock update failed for {item['name']}"
                )


            # =================================================
            # MARK ONLY SELECTED CART ITEM AS ORDERED
            # =================================================

            cart_update = conn.execute(
                """
                UPDATE cart

                SET status = 'Ordered'

                WHERE id = ?

                AND user_id = ?

                AND status = 'In Cart'
                """,
                (
                    item["cart_id"],
                    user_id
                )
            )


            if cart_update.rowcount != 1:

                raise Exception(
                    f"Cart update failed for {item['name']}"
                )


        # =================================================
        # COMMIT
        # =================================================

        conn.commit()


        # =================================================
        # GET CREATED ORDER
        # =================================================

        order = conn.execute(
            """
            SELECT *
            FROM orders
            WHERE id = ?
            """,
            (order_id,)
        ).fetchone()


        # =================================================
        # RETURN ORDER ITEMS
        # =================================================

        created_items = conn.execute(
            """
            SELECT *

            FROM order_items

            WHERE order_id = ?

            ORDER BY id ASC
            """,
            (order_id,)
        ).fetchall()


        items_result = []


        for item in created_items:

            items_result.append({

                "id":
                    item["id"],

                "flower_id":
                    item["flower_id"],

                "name":
                    item["flower_name"],

                "price":
                    item["price"],

                "quantity":
                    item["quantity"],

                "subtotal":
                    item["subtotal"]

            })


        return jsonify({

            "success": True,

            "message":
                "Selected items ordered successfully",

            "order": {

                "id":
                    order["id"],

                "user_id":
                    order["user_id"],

                "customer_name":
                    order["customer_name"],

                "phone":
                    order["phone"],

                "address":
                    order["address"],

                "payment":
                    order["payment"],

                "total":
                    order["total"],

                "status":
                    order["status"],

                "created_at":
                    order["created_at"],

                "items":
                    items_result

            },

            "ordered_cart_ids":
                cart_ids,

            "selected_items_count":
                len(cart_items)

        }), 201


    except Exception as error:

        conn.rollback()

        print(
            "Create Order Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to place order. Please try again."

        }), 500


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
    """
    Get user's orders
    ---
    tags:
      - Orders
    """

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login to view orders"

        }), 401


    try:

        logged_user_id = int(
            logged_user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify({

            "success": False,

            "message":
                "Invalid session"

        }), 401


    if logged_user_id != int(user_id):

        return jsonify({

            "success": False,

            "message":
                "You can view only your own orders"

        }), 403


    conn = get_db()


    try:

        orders = conn.execute(
            """
            SELECT *

            FROM orders

            WHERE user_id = ?

            ORDER BY id DESC
            """,
            (user_id,)
        ).fetchall()


        result = []


        for order in orders:

            items = conn.execute(
                """
                SELECT *

                FROM order_items

                WHERE order_id = ?

                ORDER BY id ASC
                """,
                (order["id"],)
            ).fetchall()


            item_list = []


            for item in items:

                item_list.append({

                    "id":
                        item["id"],

                    "flower_id":
                        item["flower_id"],

                    "name":
                        item["flower_name"],

                    "price":
                        item["price"],

                    "quantity":
                        item["quantity"],

                    "subtotal":
                        item["subtotal"]

                })


            result.append({

                "id":
                    order["id"],

                "user_id":
                    order["user_id"],

                "customer_name":
                    order["customer_name"],

                "phone":
                    order["phone"],

                "address":
                    order["address"],

                "payment":
                    order["payment"],

                "total":
                    order["total"],

                "status":
                    order["status"],

                "created_at":
                    order["created_at"],

                "items":
                    item_list

            })


        return jsonify({

            "success": True,

            "count":
                len(result),

            "orders":
                result

        }), 200


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
    """
    Get all orders
    ---
    tags:
      - Orders
    """

    conn = get_db()


    try:

        orders = conn.execute(
            """
            SELECT *

            FROM orders

            ORDER BY id DESC
            """
        ).fetchall()


        result = []


        for order in orders:

            items = conn.execute(
                """
                SELECT *

                FROM order_items

                WHERE order_id = ?

                ORDER BY id ASC
                """,
                (order["id"],)
            ).fetchall()


            item_list = []


            for item in items:

                item_list.append({

                    "id":
                        item["id"],

                    "flower_id":
                        item["flower_id"],

                    "name":
                        item["flower_name"],

                    "price":
                        item["price"],

                    "quantity":
                        item["quantity"],

                    "subtotal":
                        item["subtotal"]

                })


            result.append({

                "id":
                    order["id"],

                "user_id":
                    order["user_id"],

                "customer_name":
                    order["customer_name"],

                "phone":
                    order["phone"],

                "address":
                    order["address"],

                "payment":
                    order["payment"],

                "total":
                    order["total"],

                "status":
                    order["status"],

                "created_at":
                    order["created_at"],

                "items":
                    item_list

            })


        return jsonify({

            "success": True,

            "count":
                len(result),

            "orders":
                result

        }), 200


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
    """
    Delete user's own order
    ---
    tags:
      - Orders
    """

    logged_user_id = session.get(
        "user_id"
    )


    if not logged_user_id:

        return jsonify({

            "success": False,

            "message":
                "Please login before deleting an order"

        }), 401


    conn = get_db()


    try:

        order = conn.execute(
            """
            SELECT *

            FROM orders

            WHERE id = ?
            """,
            (order_id,)
        ).fetchone()


        if not order:

            return jsonify({

                "success": False,

                "message":
                    "Order not found"

            }), 404


        if int(logged_user_id) != int(
            order["user_id"]
        ):

            return jsonify({

                "success": False,

                "message":
                    "You can delete only your own orders"

            }), 403


        conn.execute(
            """
            DELETE FROM order_items

            WHERE order_id = ?
            """,
            (order_id,)
        )


        conn.execute(
            """
            DELETE FROM orders

            WHERE id = ?
            """,
            (order_id,)
        )


        conn.commit()


        return jsonify({

            "success": True,

            "message":
                "Order deleted successfully"

        }), 200


    except Exception as error:

        conn.rollback()

        print(
            "Delete Order Error:",
            error
        )


        return jsonify({

            "success": False,

            "message":
                "Unable to delete order"

        }), 500


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
    """
    Check backend health
    ---
    tags:
      - System
    """

    return jsonify({

        "success": True,

        "message":
            "Blossom Flower Shop backend is working"

    }), 200


# =========================================================
# ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return jsonify({

        "success": False,

        "message":
            "Page or API endpoint not found"

    }), 404


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    print("")
    print("==========================================")
    print("🌸 BLOSSOM FLOWER SHOP")
    print("==========================================")
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
    print("==========================================")
    print("")


    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )