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
import urllib.request

from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
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
    "blossom_flower_shop_secret_key_2026",
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
    supports_credentials=True,
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
- Dashboard
- Health Check
        """,

        "version": "8.0.0",
    },

    "basePath": "/",

    "schemes": [
        "http",
        "https",
    ],

    "consumes": [
        "application/json",
    ],

    "produces": [
        "application/json",
    ],

    "tags": [
        {
            "name": "Authentication",
            "description":
                "Registration, login, logout and user session",
        },

        {
            "name": "Flowers",
            "description":
                "Flower APIs",
        },

        {
            "name": "Cart",
            "description":
                "Shopping cart APIs",
        },

        {
            "name": "Checkout",
            "description":
                "Selective cart checkout APIs",
        },

        {
            "name": "Orders",
            "description":
                "Checkout and order APIs",
        },

        {
            "name": "Dashboard",
            "description":
                "Dashboard statistics APIs",
        },

        {
            "name": "System",
            "description":
                "System and health APIs",
        },
    ],
}


swagger = Swagger(
    app,
    template=swagger_template,
)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# LOCAL FLOWER IMAGES
# =========================================================

STATIC_IMAGE_DIR = os.path.join(
    BASE_DIR,
    "static",
    "images",
)

os.makedirs(
    STATIC_IMAGE_DIR,
    exist_ok=True,
)


FLOWER_IMAGE_SOURCES = {
    "White Orchid":
        "https://gulmahal.in/wp-content/uploads/2024/12/White-Orchids.webp",

    "White Daisy":
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSZuWjhG7KIur1VeZsQmsAvzWn-gaMmz1qKVzRKimV26AcQr9mY3F-pqYOr&s=10",

    "White Rose":
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTuMVeqo3ZIHDJUlonbb8lg7Yvg4YoaTYnuLWa0DIKoF399wsJf8-XOm35b&s=10",

    "Yellow Sunflower":
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTnfEY0KzMi6VfOH_3OnVeLngGT1KbmboQsZudNFV5P8u2ZG92MkP9koOI4&s=10",

    "Pink Rose":
        "https://blacktulipflowers.in/wp-content/uploads/2026/01/Blush-Pink-Roses-Valentine-Bouquet-4.png",

    "Pink Tulip":
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTQ4bgC-yH50TAMaYytpdTUbQSzd_bJUK7u1hPdXhk4Sw&s=10",

    "White Lily":
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTsybGsp0VZnLWS3RLEba1KLQDJaPKo9zFVH9xpdeXvBJMBplAIgqJngoQ&s=10",
}


FLOWER_LOCAL_FILES = {
    "White Orchid": "white-orchid.webp",
    "White Daisy": "white-daisy.jpg",
    "White Rose": "white-rose.jpg",
    "Yellow Sunflower": "yellow-sunflower.jpg",
    "Pink Rose": "pink-rose.png",
    "Pink Tulip": "pink-tulip.jpg",
    "White Lily": "white-lily.jpg",
}


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

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


# =========================================================
# DATABASE INITIALIZATION
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                stock INTEGER DEFAULT 10
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
                quantity INTEGER DEFAULT 1,
                status TEXT DEFAULT 'In Cart',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(user_id, flower_id),

                FOREIGN KEY(user_id)
                    REFERENCES users(id),

                FOREIGN KEY(flower_id)
                    REFERENCES flowers(id)
            )
            """
        )


        # =================================================
        # CHECK CART COLUMNS
        # =================================================

        cart_columns = conn.execute(
            "PRAGMA table_info(cart)"
        ).fetchall()

        cart_column_names = [
            column["name"]
            for column in cart_columns
        ]


        if "status" not in cart_column_names:

            conn.execute(
                """
                ALTER TABLE cart
                ADD COLUMN status TEXT DEFAULT 'In Cart'
                """
            )


        # =================================================
        # FIX NULL CART STATUS
        # =================================================

        conn.execute(
            """
            UPDATE cart
            SET status = 'In Cart'
            WHERE status IS NULL
               OR TRIM(status) = ''
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

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
                    REFERENCES orders(id)
            )
            """
        )


        # =================================================
        # SAVE DATABASE CHANGES
        # =================================================

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
# DEFAULT FLOWERS
# =========================================================

DEFAULT_FLOWERS = [

    (
        "Red Rose",
        "Rose",
        "Fresh red roses, perfect for love and special occasions.",
        499,
        "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=900&q=85",
        25,
    ),

    (
        "White Lily",
        "Lily",
        "Beautiful fresh white lilies with an elegant fragrance.",
        599,
        "/static/images/white-lily.jpg",
        20,
    ),

    (
        "Pink Tulip",
        "Tulip",
        "Fresh pink tulips that bring beauty and happiness.",
        449,
        "/static/images/pink-tulip.jpg",
        30,
    ),

    (
        "Yellow Sunflower",
        "Sunflower",
        "Bright yellow sunflowers to make every day cheerful.",
        399,
        "/static/images/yellow-sunflower.jpg",
        15,
    ),

    (
        "Pink Rose",
        "Rose",
        "Soft pink roses suitable for gifts and celebrations.",
        549,
        "/static/images/pink-rose.png",
        18,
    ),

    (
        "Orange Lily",
        "Lily",
        "Beautiful orange lilies with vibrant natural colors.",
        649,
        "https://www.thespruce.com/thmb/Am7_uxE6gU8CIj3UiGONPM5Top4=/4200x0/filters:no_upscale():max_bytes(150000):strip_icc()/orange-lily-growing-guide-5209359-hero-d918f048c3424f1499bf54268a36952c.jpg",
        20,
    ),

    (
        "White Rose",
        "Rose",
        "Elegant white roses perfect for peaceful and beautiful occasions.",
        529,
        "/static/images/white-rose.jpg",
        20,
    ),

    (
        "Purple Tulip",
        "Tulip",
        "Beautiful purple tulips with a soft and elegant appearance.",
        479,
        "https://images.unsplash.com/photo-1526397751294-331021109fbd?auto=format&fit=crop&w=900&q=85",
        22,
    ),

    (
        "White Daisy",
        "Daisy",
        "Fresh white daisies that bring a simple and cheerful feeling.",
        349,
        "/static/images/white-daisy.jpg",
        25,
    ),

    (
        "Pink Gerbera",
        "Gerbera",
        "Bright pink gerbera flowers perfect for gifts and celebrations.",
        429,
        "https://images.unsplash.com/photo-1523438885200-e635ba2c371e?auto=format&fit=crop&w=900&q=85",
        20,
    ),

    (
        "White Orchid",
        "Orchid",
        "Elegant white orchids with a premium and graceful appearance.",
        799,
        "/static/images/white-orchid.webp",
        12,
    ),

    (
        "Red Carnation",
        "Carnation",
        "Beautiful fresh red carnations with rich natural colors.",
        399,
        "https://images.unsplash.com/photo-1561181286-d3fee7d55364?auto=format&fit=crop&w=900&q=85",
        20,
    ),

    (
        "Yellow Marigold",
        "Marigold",
        "Bright yellow marigolds suitable for celebrations and decorations.",
        299,
        "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=900&q=85",
        30,
    ),

    (
        "Purple Iris",
        "Iris",
        "Beautiful purple iris flowers with elegant natural petals.",
        579,
        "https://images.unsplash.com/photo-1497250681960-ef046c08a56e?auto=format&fit=crop&w=900&q=85",
        15,
    ),

    (
        "Pink Peony",
        "Peony",
        "Soft pink peonies with beautiful layered petals.",
        699,
        "https://images.unsplash.com/photo-1563241527-3004b7be0ffd?auto=format&fit=crop&w=900&q=85",
        15,
    ),
]


# =========================================================
# INSERT DEFAULT FLOWERS
# =========================================================

def insert_default_flowers():

    conn = get_db()

    try:

        for flower in DEFAULT_FLOWERS:

            existing_flower = conn.execute(
                """
                SELECT id
                FROM flowers
                WHERE name = ?
                LIMIT 1
                """,
                (flower[0],)
            ).fetchone()


            # Insert only if flower does not already exist
            if existing_flower is None:

                conn.execute(
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
                    flower
                )


        conn.commit()

        print(
            "Default flowers inserted successfully."
        )


    except Exception as error:

        conn.rollback()

        print(
            "Default Flower Insert Error:",
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
# INSERT DEFAULT FLOWERS
# =========================================================

insert_default_flowers()


# =========================================================
# UPDATE FLOWER IMAGES
# =========================================================

def update_flower_images():

    conn = get_db()

    try:

        # Keep the database pointed at local static files so the
        # browser never depends on a third-party image host.
        for flower_name, filename in FLOWER_LOCAL_FILES.items():

            conn.execute(
                """
                UPDATE flowers
                SET image = ?
                WHERE name = ?
                """,
                (
                    f"/static/images/{filename}",
                    flower_name,
                )
            )

        conn.commit()

    except Exception as error:

        conn.rollback()
        print("Local Image DB Update Error:", error)
        raise

    finally:

        conn.close()


def sync_local_flower_images():
    """Try to download the user's exact image URLs into static/images.

    If a remote host blocks the request or the deployment has no network,
    the committed SVG fallback remains available, so the flower card never
    becomes a broken image.
    """

    for flower_name, source_url in FLOWER_IMAGE_SOURCES.items():

        filename = FLOWER_LOCAL_FILES[flower_name]
        destination = os.path.join(
            STATIC_IMAGE_DIR,
            filename,
        )

        # The exact image is already committed in static/images.
        # Only download again if the file is missing (for example,
        # after a clean deployment).
        if os.path.exists(destination) and os.path.getsize(destination) > 0:
            continue

        try:

            request = urllib.request.Request(
                source_url,
                headers={
                    "User-Agent":
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 Chrome/151 Safari/537.36",
                },
            )

            with urllib.request.urlopen(
                request,
                timeout=5,
            ) as response:

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    ).lower()
                )

                content = response.read()

            if content and (
                content_type.startswith("image/")
                or source_url.lower().endswith(
                    (".jpg", ".jpeg", ".png", ".webp")
                )
            ):
                # Keep the SVG fallback only when the remote download fails.
                # The exact remote image is stored with its original extension
                # where possible; otherwise use the existing fallback name.
                extension = ".webp"
                if "png" in content_type or source_url.lower().endswith(".png"):
                    extension = ".png"
                elif "jpeg" in content_type or "jpg" in content_type or source_url.lower().endswith((".jpg", ".jpeg")):
                    extension = ".jpg"

                remote_filename = os.path.splitext(filename)[0] + extension
                remote_destination = os.path.join(
                    STATIC_IMAGE_DIR,
                    remote_filename,
                )

                with open(remote_destination, "wb") as image_file:
                    image_file.write(content)

                conn = get_db()
                try:
                    conn.execute(
                        "UPDATE flowers SET image = ? WHERE name = ?",
                        (
                            f"/static/images/{remote_filename}",
                            flower_name,
                        )
                    )
                    conn.commit()
                finally:
                    conn.close()

                print(
                    f"Local image synced: {flower_name}"
                )

        except Exception as error:

            print(
                f"Image download skipped for {flower_name}: {error}"
            )


# =========================================================
# FRONTEND PAGE ROUTES
# =========================================================

@app.route("/")
def index():

    return render_template(
        "register.html"
    )


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


@app.route("/checkout")
def checkout_page():

    cart_ids_text = request.args.get(
        "cart_ids",
        "",
    ).strip()


    if cart_ids_text:

        try:

            selected_ids = [
                int(value.strip())
                for value in cart_ids_text.split(",")
                if value.strip()
            ]


            selected_ids = list(
                dict.fromkeys(
                    selected_ids
                )
            )


            session[
                "checkout_cart_ids"
            ] = selected_ids


        except ValueError:

            session.pop(
                "checkout_cart_ids",
                None,
            )

    else:

        session.pop(
            "checkout_cart_ids",
            None,
        )


    return render_template(
        "checkout.html"
    )


@app.route("/checkout.html")
def checkout_html():

    return checkout_page()


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
# STATIC FILE ROUTES
# =========================================================

@app.route("/style.css")
def style_css():

    return send_from_directory(
        BASE_DIR,
        "style.css",
    )


@app.route("/js/<path:filename>")
def javascript_files(filename):

    return send_from_directory(
        os.path.join(
            BASE_DIR,
            "js"
        ),
        filename,
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

    return jsonify(
        {
            "success": True,
            "message":
                "Blossom Flower Shop API is running",
        }
    )


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


    try:

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
                hashed_password,
            ),
        )


        user_id = cursor.lastrowid

        conn.commit()


        return jsonify(
            {
                "success": True,
                "registered": True,
                "message":
                    "Registration successful. You can now login.",

                "user": {
                    "id": user_id,
                    "name": name,
                    "email": email,
                },
            }
        ), 201


    except sqlite3.IntegrityError:

        conn.rollback()

        return jsonify(
            {
                "success": False,
                "message":
                    "Email is already registered.",
            }
        ), 409


    except Exception as error:

        conn.rollback()

        print(
            "Register Error:",
            error
        )

        return jsonify(
            {
                "success": False,
                "message":
                    "Unable to register user",
            }
        ), 500


    finally:

        conn.close()


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

        return jsonify(
            {
                "success": False,
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


    try:

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(TRIM(email)) = ?
            LIMIT 1
            """,
            (email,),
        ).fetchone()

    finally:

        conn.close()


    if not user:

        return jsonify(
            {
                "success": False,
                "registered": False,
                "message":
                    "Please register first. This email is not registered.",
            }
        ), 404


    if not check_password_hash(
        user["password"],
        password,
    ):

        return jsonify(
            {
                "success": False,
                "registered": True,
                "message":
                    "Incorrect password. Please try again.",
            }
        ), 401


    session.clear()


    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    session["checkout_cart_ids"] = []

    session.permanent = True


    return jsonify(
        {
            "success": True,
            "registered": True,
            "message":
                "Login successful",

            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
            },
        }
    ), 200


# =========================================================
# CURRENT USER API
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

        return jsonify(
            {
                "success": False,
                "logged_in": False,
                "message":
                    "User is not logged in",
            }
        ), 401


    return jsonify(
        {
            "success": True,
            "logged_in": True,

            "user": {
                "id":
                    session.get("user_id"),

                "name":
                    session.get("user_name"),

                "email":
                    session.get("user_email"),
            },
        }
    ), 200


# =========================================================
# LOGOUT PAGE
# =========================================================

@app.route(
    "/logout",
    methods=["GET"]
)
def logout_page():

    session.clear()

    return redirect(
        "/login"
    )


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

        return redirect(
            "/login"
        )


    return jsonify(
        {
            "success": True,
            "message":
                "Logout successful",
            "redirect":
                "/login",
        }
    ), 200


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

            return jsonify(
                {
                    "success": False,
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

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Email is required",
                }
            ), 400


        if len(new_password) < 6:

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Password must be at least 6 characters",
                }
            ), 400


        if new_password != confirm_password:

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Passwords do not match",
                }
            ), 400


        conn = get_db()


        try:

            user = conn.execute(
                """
                SELECT id
                FROM users
                WHERE LOWER(TRIM(email)) = ?
                LIMIT 1
                """,
                (email,),
            ).fetchone()


            if user is None:

                return jsonify(
                    {
                        "success": False,
                        "message":
                            "This email is not registered. Please register first.",
                    }
                ), 404


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
                    user["id"],
                ),
            )


            conn.commit()


        except Exception:

            conn.rollback()

            raise


        finally:

            conn.close()


        return jsonify(
            {
                "success": True,
                "message":
                    "Password reset successful. Please login with your new password.",
            }
        ), 200


    except Exception as error:

        print(
            "Forgot Password Error:",
            error
        )


        return jsonify(
            {
                "success": False,
                "message":
                    "Something went wrong while resetting your password.",
            }
        ), 500


# =========================================================
# DASHBOARD API
# =========================================================

@app.route(
    "/api/dashboard",
    methods=["GET"]
)
def dashboard_api():
    """
    Get dashboard statistics for logged-in user.

    Dashboard:
    - Total Flowers
    - Cart Quantity
    - Ordered Quantity
    - Total Orders
    - Cart Rows

    ---
    tags:
      - Dashboard
    """

    # =====================================================
    # CHECK LOGIN
    # =====================================================

    user_id = session.get(
        "user_id"
    )


    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login to view dashboard"
            }
        ), 401


    # =====================================================
    # VALIDATE USER ID
    # =====================================================

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,
                "message":
                    "Invalid session"
            }
        ), 401


    # =====================================================
    # DATABASE
    # =====================================================

    conn = get_db()


    try:

        # =================================================
        # TOTAL FLOWERS
        # =================================================

        total_flowers = conn.execute(
            """
            SELECT COUNT(*)
            FROM flowers
            """
        ).fetchone()[0]


        # =================================================
        # CART QUANTITY
        # =================================================

        cart_quantity = conn.execute(
            """
            SELECT COALESCE(
                SUM(quantity),
                0
            )
            FROM cart
            WHERE user_id = ?
              AND status = 'In Cart'
            """,
            (user_id,)
        ).fetchone()[0]


        # =================================================
        # ORDERED QUANTITY
        # =================================================

        ordered_quantity = conn.execute(
            """
            SELECT COALESCE(
                SUM(order_items.quantity),
                0
            )
            FROM order_items

            INNER JOIN orders
                ON order_items.order_id = orders.id

            WHERE orders.user_id = ?
            """,
            (user_id,)
        ).fetchone()[0]


        # =================================================
        # TOTAL ORDERS
        # =================================================

        total_orders = conn.execute(
            """
            SELECT COUNT(*)
            FROM orders
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()[0]


        # =================================================
        # CART ROWS
        # =================================================

        cart_rows = conn.execute(
            """
            SELECT COUNT(*)
            FROM cart
            WHERE user_id = ?
              AND status = 'In Cart'
            """,
            (user_id,)
        ).fetchone()[0]


        # =================================================
        # RETURN DASHBOARD DATA
        # =================================================

        return jsonify({

            "success": True,

            "message":
                "Dashboard loaded successfully",

            "counts": {

                "flowers":
                    int(total_flowers or 0),

                "cart":
                    int(cart_quantity or 0),

                "orders":
                    int(ordered_quantity or 0)
            },

            "stats": {

                "total_flowers":
                    int(total_flowers or 0),

                "cart_items":
                    int(cart_quantity or 0),

                "ordered_items":
                    int(ordered_quantity or 0),

                "total_orders":
                    int(total_orders or 0),

                "cart_rows":
                    int(cart_rows or 0)
            }

        }), 200


    except Exception as error:

        print(
            "Dashboard Error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unable to load dashboard statistics"
        }), 500


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
    """
    Get all flowers
    ---
    tags:
      - Flowers
    """

    conn = get_db()


    try:

        flowers = conn.execute(
            """
            SELECT *
            FROM flowers
            ORDER BY id DESC
            """
        ).fetchall()


        flower_list = []


        for flower in flowers:

            flower_list.append(
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
                        float(flower["price"]),

                    "image":
                        flower["image"],

                    "stock":
                        int(flower["stock"] or 0),
                }
            )


        return jsonify(
            {
                "success": True,
                "message":
                    "Flowers fetched successfully",
                "flowers":
                    flower_list,
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
def get_flower(flower_id):
    """
    Get single flower
    ---
    tags:
      - Flowers
    """

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


        if flower is None:

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

                "flower": {
                    "id":
                        int(flower["id"]),

                    "name":
                        flower["name"],

                    "category":
                        flower["category"],

                    "description":
                        flower["description"],

                    "price":
                        float(flower["price"]),

                    "image":
                        flower["image"],

                    "stock":
                        int(flower["stock"] or 0),
                },
            }
        ), 200


    finally:

        conn.close()


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

        return jsonify(
            {
                "success": False,
                "message":
                    "Request body is required",
            }
        ), 400


    # =====================================================
    # GET USER ID FROM SESSION
    # =====================================================

    session_user_id = session.get(
        "user_id"
    )


    if not session_user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login before adding items to cart",
            }
        ), 401


    # =====================================================
    # VALIDATE DATA
    # =====================================================

    try:

        session_user_id = int(
            session_user_id
        )

        flower_id = int(
            data.get("flower_id")
        )

        quantity = int(
            data.get(
                "quantity",
                1
            )
        )


    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,
                "message":
                    "Invalid flower or quantity",
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
            SELECT id, quantity, status
            FROM cart
            WHERE user_id = ?
              AND flower_id = ?
            LIMIT 1
            """,
            (
                session_user_id,
                flower_id,
            )
        ).fetchone()

        if existing:

            current_status = (
                existing["status"]
                if existing["status"]
                else "In Cart"
            )

            current_quantity = int(
                existing["quantity"] or 0
            )

            # =================================================
            # IF ITEM WAS ALREADY CHECKED OUT
            # =================================================

            if current_status != "In Cart":

                if quantity > stock:

                    return jsonify(
                        {
                            "success": False,
                            "message": (
                                f"Only {stock} item(s) "
                                f"available in stock"
                            ),
                        }
                    ), 400

                conn.execute(
                    """
                    UPDATE cart
                    SET quantity = ?,
                        status = 'In Cart'
                    WHERE user_id = ?
                      AND flower_id = ?
                    """,
                    (
                        quantity,
                        session_user_id,
                        flower_id,
                    )
                )

                conn.commit()

                return jsonify(
                    {
                        "success": True,
                        "message": (
                            f"{flower['name']} "
                            "added to cart successfully"
                        ),
                    }
                ), 200

            # =================================================
            # EXISTING ACTIVE CART ITEM
            # =================================================

            new_quantity = (
                current_quantity + quantity
            )

            if new_quantity > stock:

                return jsonify(
                    {
                        "success": False,
                        "message": (
                            f"Only {stock} item(s) "
                            f"available in stock"
                        ),
                    }
                ), 400

            conn.execute(
                """
                UPDATE cart
                SET quantity = ?,
                    status = 'In Cart'
                WHERE user_id = ?
                  AND flower_id = ?
                """,
                (
                    new_quantity,
                    session_user_id,
                    flower_id,
                )
            )

        else:

            # =================================================
            # NEW CART ITEM
            # =================================================

            if quantity > stock:

                return jsonify(
                    {
                        "success": False,
                        "message": (
                            f"Only {stock} item(s) "
                            f"available in stock"
                        ),
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
                )
            )

        # =====================================================
        # SAVE CART
        # =====================================================

        conn.commit()

        # =====================================================
        # GET UPDATED CART COUNT
        # =====================================================

        cart_count = conn.execute(
            """
            SELECT COALESCE(
                SUM(quantity),
                0
            )
            FROM cart
            WHERE user_id = ?
              AND status = 'In Cart'
            """,
            (
                session_user_id,
            )
        ).fetchone()[0]

        return jsonify(
            {
                "success": True,
                "message": (
                    f"{flower['name']} "
                    "added to cart successfully"
                ),
                "cart_count": int(
                    cart_count or 0
                ),
            }
        ), 200

    except Exception as error:

        conn.rollback()

        print(
            "Add To Cart Error:",
            error
        )

        return jsonify(
            {
                "success": False,
                "message": "Unable to add flower to cart",
            }
        ), 500

    finally:

        conn.close()


# =========================================================
# GET CART
# =========================================================

@app.route(
    "/api/cart",
    methods=["GET"]
)
def get_cart():
    """
    Get current user's cart
    ---
    tags:
      - Cart
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message": "Please login first",
            }
        ), 401

    try:

        user_id = int(user_id)

    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,
                "message": "Invalid session",
            }
        ), 401

    conn = get_db()

    try:

        rows = conn.execute(
            """
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
              AND cart.status = 'In Cart'

            ORDER BY cart.id DESC
            """,
            (
                user_id,
            )
        ).fetchall()

        cart_items = []

        total_amount = 0
        total_quantity = 0

        for row in rows:

            quantity = int(
                row["quantity"] or 0
            )

            price = float(
                row["price"] or 0
            )

            subtotal = (
                price * quantity
            )

            total_amount += subtotal
            total_quantity += quantity

            cart_items.append(
                {
                    "cart_id":
                        int(row["cart_id"]),

                    "id":
                        int(row["cart_id"]),

                    "user_id":
                        int(row["user_id"]),

                    "flower_id":
                        int(row["flower_id"]),

                    "name":
                        row["name"],

                    "category":
                        row["category"],

                    "description":
                        row["description"],

                    "price":
                        price,

                    "image":
                        row["image"],

                    "stock":
                        int(
                            row["stock"] or 0
                        ),

                    "quantity":
                        quantity,

                    "subtotal":
                        round(
                            subtotal,
                            2
                        ),

                    "status":
                        row["status"],

                    "created_at":
                        row["created_at"],
                }
            )

        # =================================================
        # ORDERED ITEMS FOR THE SAME USER
        # =================================================

        ordered_rows = conn.execute(
            """
            SELECT
                order_items.id AS item_id,
                order_items.order_id,
                order_items.flower_id,
                order_items.flower_name AS name,
                order_items.price,
                order_items.quantity,
                order_items.subtotal,
                orders.created_at,
                flowers.description,
                flowers.image
            FROM order_items
            INNER JOIN orders
                ON order_items.order_id = orders.id
            LEFT JOIN flowers
                ON order_items.flower_id = flowers.id
            WHERE orders.user_id = ?
            ORDER BY orders.id DESC, order_items.id ASC
            """,
            (user_id,)
        ).fetchall()

        ordered_items = []

        for row in ordered_rows:
            ordered_items.append(
                {
                    "id": int(row["item_id"]),
                    "cart_id": int(row["item_id"]),
                    "order_id": int(row["order_id"]),
                    "flower_id": int(row["flower_id"]),
                    "name": row["name"],
                    "description": row["description"] or "Beautiful fresh flower.",
                    "price": float(row["price"] or 0),
                    "image": row["image"] or "/static/images/white-daisy.jpg",
                    "quantity": int(row["quantity"] or 0),
                    "subtotal": float(row["subtotal"] or 0),
                    "status": "Ordered",
                    "created_at": row["created_at"],
                }
            )

        return jsonify(
            {
                "success": True,
                "message":
                    "Cart fetched successfully",

                "cart":
                    cart_items,

                "items":
                    cart_items,

                "ordered":
                    ordered_items,

                "total_items":
                    len(cart_items),

                "total_quantity":
                    total_quantity,

                "total_amount":
                    round(
                        total_amount,
                        2
                    ),
            }
        ), 200

    except Exception as error:

        print(
            "Get Cart Error:",
            error
        )

        return jsonify(
            {
                "success": False,
                "message":
                    "Unable to fetch cart",
            }
        ), 500

    finally:

        conn.close()


# =========================================================
# BACKWARD-COMPATIBLE CART URL
# =========================================================

@app.route(
    "/api/cart/<int:requested_user_id>",
    methods=["GET"]
)
def get_cart_legacy(requested_user_id):
    # The logged-in session is always authoritative.
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "success": False,
            "message": "Please login first",
        }), 401

    if int(user_id) != int(requested_user_id):
        return jsonify({
            "success": False,
            "message": "You can only access your own cart",
        }), 403

    return get_cart()


# =========================================================
# UPDATE CART QUANTITY
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["PUT"]
)
def update_cart(cart_id):
    """
    Update cart quantity
    ---
    tags:
      - Cart
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message": "Please login first",
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

    try:

        quantity = int(
            data.get(
                "quantity"
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,
                "message":
                    "Invalid quantity",
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

        cart_item = conn.execute(
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
              AND cart.status = 'In Cart'
            """,
            (
                cart_id,
                user_id,
            )
        ).fetchone()

        if not cart_item:

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Cart item not found",
                }
            ), 404

        stock = int(
            cart_item["stock"] or 0
        )

        if quantity > stock:

            return jsonify(
                {
                    "success": False,
                    "message": (
                        f"Only {stock} item(s) "
                        "available in stock"
                    ),
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
                user_id,
            )
        )

        conn.commit()

        return jsonify(
            {
                "success": True,
                "message":
                    "Cart quantity updated successfully",
                "quantity":
                    quantity,
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
# DELETE CART ITEM
# =========================================================

@app.route(
    "/api/cart/<int:cart_id>",
    methods=["DELETE"]
)
def delete_cart_item(cart_id):
    """
    Remove item from cart
    ---
    tags:
      - Cart
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login first",
            }
        ), 401

    conn = get_db()

    try:

        cart_item = conn.execute(
            """
            SELECT id
            FROM cart
            WHERE id = ?
              AND user_id = ?
              AND status = 'In Cart'
            """,
            (
                cart_id,
                user_id,
            )
        ).fetchone()

        if not cart_item:

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
                user_id,
            )
        )

        conn.commit()

        return jsonify(
            {
                "success": True,
                "message":
                    "Item removed from cart",
            }
        ), 200

    except Exception as error:

        conn.rollback()

        print(
            "Delete Cart Error:",
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
# CLEAR CART
# =========================================================

@app.route(
    "/api/cart/clear",
    methods=["DELETE", "POST"]
)
def clear_cart():
    """
    Clear current user's active cart
    ---
    tags:
      - Cart
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login first",
            }
        ), 401

    conn = get_db()

    try:

        conn.execute(
            """
            DELETE FROM cart
            WHERE user_id = ?
              AND status = 'In Cart'
            """,
            (
                user_id,
            )
        )

        conn.commit()

        return jsonify(
            {
                "success": True,
                "message":
                    "Cart cleared successfully",
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
# SELECTIVE CHECKOUT DATA
# =========================================================

@app.route(
    "/api/checkout",
    methods=["GET"]
)
@app.route(
    "/api/checkout/selected",
    methods=["GET"]
)
def get_checkout():
    """
    Get selected cart items for checkout
    ---
    tags:
      - Checkout
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login first",
            }
        ), 401

    selected_ids = session.get(
        "checkout_cart_ids",
        []
    )

    try:

        selected_ids = [
            int(item)
            for item in selected_ids
        ]

    except (
        TypeError,
        ValueError
    ):

        selected_ids = []

    conn = get_db()

    try:

        if selected_ids:

            placeholders = ",".join(
                ["?"] * len(selected_ids)
            )

            query = f"""
                SELECT
                    cart.id AS cart_id,
                    cart.flower_id,
                    cart.quantity,

                    flowers.name,
                    flowers.price,
                    flowers.image,
                    flowers.stock

                FROM cart

                INNER JOIN flowers
                    ON cart.flower_id = flowers.id

                WHERE cart.user_id = ?
                  AND cart.status = 'In Cart'
                  AND cart.id IN ({placeholders})

                ORDER BY cart.id DESC
            """

            params = [
                user_id,
                *selected_ids
            ]

            rows = conn.execute(
                query,
                params
            ).fetchall()

        else:

            rows = conn.execute(
                """
                SELECT
                    cart.id AS cart_id,
                    cart.flower_id,
                    cart.quantity,

                    flowers.name,
                    flowers.price,
                    flowers.image,
                    flowers.stock

                FROM cart

                INNER JOIN flowers
                    ON cart.flower_id = flowers.id

                WHERE cart.user_id = ?
                  AND cart.status = 'In Cart'

                ORDER BY cart.id DESC
                """,
                (
                    user_id,
                )
            ).fetchall()

        items = []

        total = 0

        for row in rows:

            quantity = int(
                row["quantity"] or 0
            )

            price = float(
                row["price"] or 0
            )

            subtotal = (
                price * quantity
            )

            total += subtotal

            items.append(
                {
                    "cart_id":
                        int(row["cart_id"]),

                    "flower_id":
                        int(row["flower_id"]),

                    "name":
                        row["name"],

                    "price":
                        price,

                    "image":
                        row["image"],

                    "stock":
                        int(
                            row["stock"] or 0
                        ),

                    "quantity":
                        quantity,

                    "subtotal":
                        round(
                            subtotal,
                            2
                        ),
                }
            )

        return jsonify(
            {
                "success": True,
                "items": items,
                "total":
                    round(
                        total,
                        2
                    ),
                "selected_cart_ids":
                    selected_ids,
            }
        ), 200

    except Exception as error:

        print(
            "Checkout Error:",
            error
        )

        return jsonify(
            {
                "success": False,
                "message":
                    "Unable to load checkout",
            }
        ), 500

    finally:

        conn.close()


# =========================================================
# CREATE ORDER
# =========================================================

@app.route(
    "/api/orders",
    methods=["POST"]
)
def create_order():
    """
    Create order from selected cart items
    ---
    tags:
      - Orders
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login before placing order",
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

    if not phone:

        return jsonify(
            {
                "success": False,
                "message":
                    "Phone number is required",
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

    # =====================================================
    # USE SESSION SELECTION IF CART IDS NOT PROVIDED
    # =====================================================

    if not cart_ids:

        cart_ids = session.get(
            "checkout_cart_ids",
            []
        )

    try:

        cart_ids = [
            int(item)
            for item in cart_ids
        ]

        cart_ids = list(
            dict.fromkeys(
                cart_ids
            )
        )

    except (
        TypeError,
        ValueError
    ):

        return jsonify(
            {
                "success": False,
                "message":
                    "Invalid cart selection",
            }
        ), 400

    if not cart_ids:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please select at least one item",
            }
        ), 400

    conn = get_db()

    try:

        placeholders = ",".join(
            ["?"] * len(cart_ids)
        )

        rows = conn.execute(
            f"""
            SELECT
                cart.id AS cart_id,
                cart.flower_id,
                cart.quantity,

                flowers.name,
                flowers.price,
                flowers.stock

            FROM cart

            INNER JOIN flowers
                ON cart.flower_id = flowers.id

            WHERE cart.user_id = ?
              AND cart.status = 'In Cart'
              AND cart.id IN ({placeholders})
            """,
            [
                user_id,
                *cart_ids
            ]
        ).fetchall()

        if not rows:

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Selected cart items not found",
                }
            ), 404

        # =================================================
        # VERIFY ALL SELECTED IDS EXIST
        # =================================================

        found_ids = {
            int(row["cart_id"])
            for row in rows
        }

        missing_ids = [
            item
            for item in cart_ids
            if item not in found_ids
        ]

        if missing_ids:

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Some selected cart items are no longer available",
                }
            ), 400

        # =================================================
        # CHECK STOCK
        # =================================================

        total = 0

        for row in rows:

            quantity = int(
                row["quantity"] or 0
            )

            stock = int(
                row["stock"] or 0
            )

            if quantity > stock:

                return jsonify(
                    {
                        "success": False,
                        "message": (
                            f"Insufficient stock for "
                            f"{row['name']}. "
                            f"Available stock: {stock}"
                        ),
                    }
                ), 400

            price = float(
                row["price"] or 0
            )

            total += (
                price * quantity
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
            VALUES (?, ?, ?, ?, ?, ?, 'Processing')
            """,
            (
                user_id,
                customer_name,
                phone,
                address,
                payment,
                round(total, 2),
            )
        )

        order_id = cursor.lastrowid

        # =================================================
        # CREATE ORDER ITEMS
        # =================================================

        for row in rows:

            quantity = int(
                row["quantity"] or 0
            )

            price = float(
                row["price"] or 0
            )

            subtotal = (
                price * quantity
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
                    row["flower_id"],
                    row["name"],
                    price,
                    quantity,
                    round(
                        subtotal,
                        2
                    ),
                )
            )

            # =================================================
            # REDUCE FLOWER STOCK
            # =================================================

            conn.execute(
                """
                UPDATE flowers
                SET stock = stock - ?
                WHERE id = ?
                """,
                (
                    quantity,
                    row["flower_id"],
                )
            )

        # =================================================
        # REMOVE SELECTED ITEMS FROM ACTIVE CART
        # =================================================

        conn.execute(
            f"""
            DELETE FROM cart
            WHERE user_id = ?
              AND id IN ({placeholders})
            """,
            [
                user_id,
                *cart_ids
            ]
        )

        # =================================================
        # SAVE ORDER
        # =================================================

        conn.commit()

        # =================================================
        # CLEAR CHECKOUT SESSION
        # =================================================

        session["checkout_cart_ids"] = []

        return jsonify(
            {
                "success": True,
                "message":
                    "Order placed successfully",
                "order": {
                    "id":
                        int(order_id),

                    "user_id":
                        int(user_id),

                    "customer_name":
                        customer_name,

                    "phone":
                        phone,

                    "address":
                        address,

                    "payment":
                        payment,

                    "total":
                        round(
                            total,
                            2
                        ),

                    "status":
                        "Processing",
                },
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
                    "Unable to place order",
            }
        ), 500

    finally:

        conn.close()


# =========================================================
# GET ORDERS
# =========================================================

@app.route(
    "/api/orders",
    methods=["GET"]
)
def get_orders():
    """
    Get current user's orders
    ---
    tags:
      - Orders
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login first",
            }
        ), 401

    conn = get_db()

    try:

        orders = conn.execute(
            """
            SELECT *
            FROM orders
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (
                user_id,
            )
        ).fetchall()

        order_list = []

        for order in orders:

            items = conn.execute(
                """
                SELECT
                    order_items.*,
                    flowers.image AS flower_image
                FROM order_items
                LEFT JOIN flowers
                    ON order_items.flower_id = flowers.id
                WHERE order_items.order_id = ?
                ORDER BY order_items.id ASC
                """,
                (
                    order["id"],
                )
            ).fetchall()

            item_list = []

            for item in items:

                item_list.append(
                    {
                        "id":
                            int(item["id"]),

                        "flower_id":
                            int(item["flower_id"]),

                        "flower_name":
                            item["flower_name"],

                        "name":
                            item["flower_name"],

                        "image":
                            item["flower_image"] or "/static/images/white-daisy.jpg",

                        "price":
                            float(
                                item["price"]
                                or 0
                            ),

                        "quantity":
                            int(
                                item["quantity"]
                                or 0
                            ),

                        "subtotal":
                            float(
                                item["subtotal"]
                                or 0
                            ),
                    }
                )

            order_list.append(
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
                            order["total"]
                            or 0
                        ),

                    "status":
                        order["status"],

                    "created_at":
                        order["created_at"],

                    "items":
                        item_list,
                }
            )

        return jsonify(
            {
                "success": True,
                "message":
                    "Orders fetched successfully",
                "orders":
                    order_list,
            }
        ), 200

    except Exception as error:

        print(
            "Get Orders Error:",
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
# GET SINGLE ORDER
# =========================================================

@app.route(
    "/api/orders/<int:order_id>",
    methods=["GET"]
)
def get_order(order_id):
    """
    Get single order
    ---
    tags:
      - Orders
    """

    user_id = session.get(
        "user_id"
    )

    if not user_id:

        return jsonify(
            {
                "success": False,
                "message":
                    "Please login first",
            }
        ), 401

    conn = get_db()

    try:

        order = conn.execute(
            """
            SELECT *
            FROM orders
            WHERE id = ?
              AND user_id = ?
            LIMIT 1
            """,
            (
                order_id,
                user_id,
            )
        ).fetchone()

        if not order:

            return jsonify(
                {
                    "success": False,
                    "message":
                        "Order not found",
                }
            ), 404

        items = conn.execute(
            """
            SELECT *
            FROM order_items
            WHERE order_id = ?
            ORDER BY id ASC
            """,
            (
                order_id,
            )
        ).fetchall()

        item_list = []

        for item in items:

            item_list.append(
                {
                    "id":
                        int(item["id"]),

                    "flower_id":
                        int(item["flower_id"]),

                    "flower_name":
                        item["flower_name"],

                    "price":
                        float(
                            item["price"]
                            or 0
                        ),

                    "quantity":
                        int(
                            item["quantity"]
                            or 0
                        ),

                    "subtotal":
                        float(
                            item["subtotal"]
                            or 0
                        ),
                }
            )

        return jsonify(
            {
                "success": True,
                "order": {
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
                            order["total"]
                            or 0
                        ),

                    "status":
                        order["status"],

                    "created_at":
                        order["created_at"],

                    "items":
                        item_list,
                },
            }
        ), 200

    except Exception as error:

        print(
            "Get Order Error:",
            error
        )

        return jsonify(
            {
                "success": False,
                "message":
                    "Unable to fetch order",
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
    """
    Health check
    ---
    tags:
      - System
    """

    try:

        conn = get_db()

        conn.execute(
            "SELECT 1"
        ).fetchone()

        conn.close()

        return jsonify(
            {
                "success": True,
                "status": "healthy",
                "message":
                    "Blossom Flower Shop API is healthy",
            }
        ), 200

    except Exception as error:

        print(
            "Health Check Error:",
            error
        )

        return jsonify(
            {
                "success": False,
                "status": "unhealthy",
                "message":
                    "Database connection failed",
            }
        ), 500


# =========================================================
# SWAGGER JSON
# =========================================================

@app.route(
    "/swagger.json",
    methods=["GET"]
)
def swagger_json():

    return jsonify(
        swagger.get_apispecs()
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    if request.path.startswith("/api/"):

        return jsonify(
            {
                "success": False,
                "message":
                    "API endpoint not found",
            }
        ), 404

    return (
        "Page not found",
        404
    )


@app.errorhandler(500)
def internal_server_error(error):

    if request.path.startswith("/api/"):

        return jsonify(
            {
                "success": False,
                "message":
                    "Internal server error",
            }
        ), 500

    return (
        "Internal server error",
        500
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )