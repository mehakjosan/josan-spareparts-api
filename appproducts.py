from flask import Blueprint, request, jsonify
from flask_cors import CORS
import pyodbc
import jwt
import datetime

products_bp = Blueprint("products", __name__)
CORS(products_bp)

SECRET_KEY = "mysecretkey"

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SprayerPartsDB;"
    "Trusted_Connection=yes;"
)

# ================= LOGIN =================

@products_bp.route("/login", methods=["POST"])
def login():

    data = request.json

    if data["username"] == "admin" and data["password"] == "123":

        token = jwt.encode(
            {
                "user": data["username"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


# ================= VERIFY TOKEN =================

def verify_token(request):

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None, jsonify({"message": "Token missing"}), 403

    try:

        parts = auth_header.split(" ")

        if len(parts) != 2:
            return None, jsonify({"message": "Invalid token format"}), 403

        token = parts[1]

        data = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        return data, None, None

    except Exception:
        return None, jsonify({"message": "Invalid or expired token"}), 403


# ================= HOME =================

@products_bp.route("/")
def home():
    return "Products API Running!"


# ================= GET ALL PRODUCTS =================

@products_bp.route("/api/products", methods=["GET"])
def get_products():

    data_token, error, status = verify_token(request)

    if error:
        return error, status

    try:

        with pyodbc.connect(conn_str) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                ProductID,
                PartName,
                Description,
                UnitMeasure,
                UnitPrice,
                Tax,
                Category,
                Quantity,
                [Vendor ID]
                FROM Products
            """)

            rows = cursor.fetchall()

            result = []

            for row in rows:

                result.append({

                    "ProductID": row[0],
                    "PartName": row[1],
                    "Description": row[2],
                    "UnitMeasure": row[3],
                    "UnitPrice": row[4],
                    "Tax": row[5],
                    "Category": row[6],
                    "Quantity": row[7],
                    "VendorID": row[8]

                })

        return jsonify(result)

    except Exception as e:

        return jsonify({"error": str(e)}), 500


# ================= GET PRODUCT BY ID =================

@products_bp.route("/api/products/<int:id>", methods=["GET"])
def get_product(id):

    data_token, error, status = verify_token(request)

    if error:
        return error, status

    try:

        with pyodbc.connect(conn_str) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                ProductID,
                PartName,
                Description,
                UnitMeasure,
                UnitPrice,
                Tax,
                Category,
                Quantity,
                [Vendor ID]
                FROM Products
                WHERE ProductID=?
            """, id)

            row = cursor.fetchone()

            if not row:
                return jsonify({"message": "Product not found"}), 404

            return jsonify({

                "ProductID": row[0],
                "PartName": row[1],
                "Description": row[2],
                "UnitMeasure": row[3],
                "UnitPrice": row[4],
                "Tax": row[5],
                "Category": row[6],
                "Quantity": row[7],
                "VendorID": row[8]

            })

    except Exception as e:

        return jsonify({"error": str(e)}), 500


# ================= ADD PRODUCT =================

@products_bp.route("/api/products", methods=["POST"])
def add_product():

    data_token, error, status = verify_token(request)

    if error:
        return error, status

    try:

        data = request.json

        with pyodbc.connect(conn_str) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Products
                (
                    PartName,
                    Description,
                    UnitMeasure,
                    UnitPrice,
                    Tax,
                    Category,
                    Quantity,
                    [Vendor ID]
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,

            data["PartName"],
            data["Description"],
            data["UnitMeasure"],
            data["UnitPrice"],
            data["Tax"],
            data["Category"],
            data["Quantity"],
            data["VendorID"]

            )

            conn.commit()

        return jsonify({"message": "Product added successfully"})

    except Exception as e:

        return jsonify({"error": str(e)}), 500


# ================= UPDATE PRODUCT =================

@products_bp.route("/api/products/<int:id>", methods=["PUT"])
def update_product(id):

    data_token, error, status = verify_token(request)

    if error:
        return error, status

    try:

        data = request.json

        with pyodbc.connect(conn_str) as conn:

            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Products
                SET
                    PartName=?,
                    Description=?,
                    UnitMeasure=?,
                    UnitPrice=?,
                    Tax=?,
                    Category=?,
                    Quantity=?,
                    [Vendor ID]=?
                WHERE ProductID=?
            """,

            data["PartName"],
            data["Description"],
            data["UnitMeasure"],
            data["UnitPrice"],
            data["Tax"],
            data["Category"],
            data["Quantity"],
            data["VendorID"],
            id

            )

            conn.commit()

        return jsonify({"message": "Product updated successfully"})

    except Exception as e:

        return jsonify({"error": str(e)}), 500


# ================= DELETE PRODUCT =================

@products_bp.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):

    data_token, error, status = verify_token(request)

    if error:
        return error, status

    try:

        with pyodbc.connect(conn_str) as conn:

            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM Products WHERE ProductID=?",
                id
            )

            conn.commit()

        return jsonify({"message": "Product deleted successfully"})

    except Exception as e:

        return jsonify({"error": str(e)}), 500