
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import pyodbc
import jwt
import datetime

# Blueprint
purchase_bp = Blueprint('purchase', __name__)
CORS(purchase_bp)

SECRET_KEY = "mysecretkey"

# SQL Server Connection
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SprayerPartsDB;"
    "Trusted_Connection=yes;"
)

# Home
@purchase_bp.route('/')
def home():
    return "Purchase API Running!"

# Login
@purchase_bp.route('/login', methods=['POST'])
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

    return jsonify({"message": "Invalid Login"}), 401


# Verify Token
def verify_token(request):

    auth = request.headers.get("Authorization")

    if not auth:
        return None, jsonify({"message": "Token Missing"}), 403

    try:

        token = auth.split(" ")[1]

        data = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        return data, None, None

    except:
        return None, jsonify({"message": "Invalid Token"}), 403


# Get All Purchases
@purchase_bp.route('/api/purchase', methods=['GET'])
def get_purchases():

    data, error, status = verify_token(request)
    if error:
        return error, status

    try:

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                PurchaseID,
                InvoiceNo,
                PurchaseDate,
                Quantity,
                PricePerItem,
                TotalAmount,
                PaymentMode,
                VendorID,
                ProductID
            FROM Purchase
        """)

        rows = cursor.fetchall()
        cols = [col[0] for col in cursor.description]

        result = [dict(zip(cols, row)) for row in rows]

        conn.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get Purchase By ID
@purchase_bp.route('/api/purchase/<int:id>', methods=['GET'])
def get_purchase(id):

    data, error, status = verify_token(request)
    if error:
        return error, status

    try:

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                PurchaseID,
                InvoiceNo,
                PurchaseDate,
                Quantity,
                PricePerItem,
                TotalAmount,
                PaymentMode,
                VendorID,
                ProductID
            FROM Purchase
            WHERE PurchaseID = ?
        """, id)

        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"message": "Purchase Not Found"}), 404

        cols = [col[0] for col in cursor.description]

        result = dict(zip(cols, row))

        conn.close()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Add Purchase
@purchase_bp.route('/api/purchase', methods=['POST'])
def add_purchase():

    data_token, error, status = verify_token(request)
    if error:
        return error, status

    try:

        data = request.json

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Purchase
            (
                InvoiceNo,
                PurchaseDate,
                Quantity,
                PricePerItem,
                TotalAmount,
                PaymentMode,
                VendorID,
                ProductID
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            data.get("InvoiceNo"),
            data.get("PurchaseDate"),
            data.get("Quantity"),
            data.get("PricePerItem"),
            data.get("TotalAmount"),
            data.get("PaymentMode"),
            data.get("VendorID"),
            data.get("ProductID")
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Purchase Added Successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update Purchase
@purchase_bp.route('/api/purchase/<int:id>', methods=['PUT'])
def update_purchase(id):

    data_token, error, status = verify_token(request)
    if error:
        return error, status

    try:

        data = request.json

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Purchase
            SET
                InvoiceNo = ?,
                PurchaseDate = ?,
                Quantity = ?,
                PricePerItem = ?,
                TotalAmount = ?,
                PaymentMode = ?,
                VendorID = ?,
                ProductID = ?
            WHERE PurchaseID = ?
        """,
            data.get("InvoiceNo"),
            data.get("PurchaseDate"),
            data.get("Quantity"),
            data.get("PricePerItem"),
            data.get("TotalAmount"),
            data.get("PaymentMode"),
            data.get("VendorID"),
            data.get("ProductID"),
            id
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Purchase Updated Successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Delete Purchase
@purchase_bp.route('/api/purchase/<int:id>', methods=['DELETE'])
def delete_purchase(id):

    data_token, error, status = verify_token(request)
    if error:
        return error, status

    try:

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM Purchase WHERE PurchaseID = ?",
            id
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Purchase Deleted Successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
