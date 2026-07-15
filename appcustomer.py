from flask import Blueprint, request, jsonify
from flask_cors import CORS
import pyodbc
import jwt
import datetime

# ✅ Blueprint
customer_bp = Blueprint('customer', __name__)
CORS(customer_bp)

SECRET_KEY = 'mysecretkey'

# ✅ DB connection
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SprayerPartsDB;"
    "Trusted_Connection=yes;"
)

# 🏠 HOME
@customer_bp.route('/')
def home():
    return "🔥 Customer API Running!"


# 🔐 LOGIN
@customer_bp.route('/login', methods=['POST'])
def login():
    data = request.json

    if data['username'] == "admin" and data['password'] == "123":
        token = jwt.encode({
            'user': data['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401


# 🔒 VERIFY TOKEN
def verify_token(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return None, jsonify({'message': 'Token missing'}), 403

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2:
            return None, jsonify({'message': 'Invalid token format'}), 403

        token = parts[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        return data, None, None

    except Exception:
        return None, jsonify({'message': 'Invalid or expired token'}), 403


# ✅ GET ALL CUSTOMERS
@customer_bp.route('/api/customers', methods=['GET'])
def get_customers():
    data, error, status = verify_token(request)
    if error:
        return error, status

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tblCustomer")

            rows = cursor.fetchall()
            cols = [col[0] for col in cursor.description]
            result = [dict(zip(cols, row)) for row in rows]

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ GET CUSTOMER BY ID
@customer_bp.route('/api/customers/<int:id>', methods=['GET'])
def get_customer(id):
    data, error, status = verify_token(request)
    if error:
        return error, status

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tblCustomer WHERE CustomerID=?", id)

            row = cursor.fetchone()
            if not row:
                return jsonify({"message": "Customer not found"}), 404

            cols = [col[0] for col in cursor.description]
            return jsonify(dict(zip(cols, row)))

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ ADD CUSTOMER
@customer_bp.route('/api/customers', methods=['POST'])
def add_customer():
    data_token, error, status = verify_token(request)
    if error:
        return error, status

    try:
        data = request.json

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tblCustomer
                (CustomerName, Address, ContactNo, Email, GSTNo, CustomerType)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
            data['CustomerName'],
            data['Address'],
            data['ContactNo'],
            data['Email'],
            data['GSTNo'],
            data['CustomerType']
            )

            conn.commit()

        return jsonify({"message": "Customer added"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ✅ UPDATE CUSTOMER
@customer_bp.route('/api/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data_token, error, status = verify_token(request)
    if error:
        return error, status

    try:
        data = request.json

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE tblCustomer SET
                CustomerName=?, Address=?, ContactNo=?, Email=?, GSTNo=?, CustomerType=?
                WHERE CustomerID=?
            """,
            data['CustomerName'],
            data['Address'],
            data['ContactNo'],
            data['Email'],
            data['GSTNo'],
            data['CustomerType'],
            id
            )

            conn.commit()

        return jsonify({"message": "Customer updated"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


# ✅ DELETE CUSTOMER
@customer_bp.route('/api/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    data_token, error, status = verify_token(request)
    if error:
        return error, status

    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tblCustomer WHERE CustomerID=?", id)
            conn.commit()

        return jsonify({"message": "Customer deleted"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    # ✅ IMPORT CUSTOMERS FROM EXCEL
@customer_bp.route('/api/import-customers', methods=['POST'])
def import_customers():

    data_token, error, status = verify_token(request)

    if error:
        return error, status

    try:
        customers = request.json

        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()

            count = 0

            for row in customers:

                cursor.execute("""
                    INSERT INTO tblCustomer
                    (
                        CustomerName,
                        Address,
                        ContactNo,
                        Email,
                        GSTNo,
                        CustomerType
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                row.get("CustomerName", ""),
                row.get("Address", ""),
                row.get("ContactNo", ""),
                row.get("Email", ""),
                row.get("GSTNo", ""),
                row.get("CustomerType", "")
                )

                count += 1

            conn.commit()

        return jsonify({
            "message": f"{count} Customers Imported Successfully"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500