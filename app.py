
from flask import Blueprint, request, jsonify
from flask_cors import CORS
import pyodbc
import jwt
import datetime

# Blueprint
vendor_bp = Blueprint("vendor", __name__)
CORS(vendor_bp)

SECRET_KEY = "mysecretkey"

# SQL Server Connection
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SprayerPartsDB;"
    "Trusted_Connection=yes;"
)

# -----------------------------
# Home
# -----------------------------
@vendor_bp.route("/")
def home():
    return "Vendor API Running!"

# -----------------------------
# Login
# -----------------------------
@vendor_bp.route("/login", methods=["POST"])
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

# -----------------------------
# Verify Token
# -----------------------------
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

# -----------------------------
# Get All Vendors
# -----------------------------
@vendor_bp.route("/api/vendors", methods=["GET"])
def get_vendors():

    data, error, status = verify_token(request)
    if error:
        return error, status

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT VendorID,
               VendorName,
               Address,
               ContactPerson,
               PhoneNo,
               GSTNo
        FROM Vendor
        ORDER BY VendorID
    """)

    rows = cursor.fetchall()

    vendors = []

    for row in rows:
        vendors.append({
            "VendorID": row.VendorID,
            "VendorName": row.VendorName,
            "Address": row.Address,
            "ContactPerson": row.ContactPerson,
            "PhoneNo": row.PhoneNo,
            "GSTNo": row.GSTNo
        })

    conn.close()

    return jsonify(vendors)

# -----------------------------
# Get Vendor By ID
# -----------------------------
@vendor_bp.route("/api/vendors/<int:id>", methods=["GET"])
def get_vendor(id):

    data, error, status = verify_token(request)
    if error:
        return error, status

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT VendorID,
               VendorName,
               Address,
               ContactPerson,
               PhoneNo,
               GSTNo
        FROM Vendor
        WHERE VendorID = ?
    """, id)

    row = cursor.fetchone()

    conn.close()

    if not row:
        return jsonify({"message": "Vendor Not Found"}), 404

    return jsonify({
        "VendorID": row.VendorID,
        "VendorName": row.VendorName,
        "Address": row.Address,
        "ContactPerson": row.ContactPerson,
        "PhoneNo": row.PhoneNo,
        "GSTNo": row.GSTNo
    })

# -----------------------------
# Add Vendor
# -----------------------------
@vendor_bp.route("/api/vendors", methods=["POST"])
def add_vendor():

    data, error, status = verify_token(request)
    if error:
        return error, status

    vendor = request.json

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Vendor
        (
            VendorName,
            Address,
            ContactPerson,
            PhoneNo,
            GSTNo
        )
        VALUES (?, ?, ?, ?, ?)
    """,
    vendor["VendorName"],
    vendor["Address"],
    vendor["ContactPerson"],
    vendor["PhoneNo"],
    vendor["GSTNo"])

    conn.commit()
    conn.close()

    return jsonify({"message": "Vendor Added Successfully"}), 201

# -----------------------------
# Update Vendor
# -----------------------------
@vendor_bp.route("/api/vendors/<int:id>", methods=["PUT"])
def update_vendor(id):

    data, error, status = verify_token(request)
    if error:
        return error, status

    vendor = request.json

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE Vendor
        SET VendorName=?,
            Address=?,
            ContactPerson=?,
            PhoneNo=?,
            GSTNo=?
        WHERE VendorID=?
    """,
    vendor["VendorName"],
    vendor["Address"],
    vendor["ContactPerson"],
    vendor["PhoneNo"],
    vendor["GSTNo"],
    id)

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"message": "Vendor Not Found"}), 404

    conn.close()

    return jsonify({"message": "Vendor Updated Successfully"})

# -----------------------------
# Delete Vendor
# -----------------------------
@vendor_bp.route("/api/vendors/<int:id>", methods=["DELETE"])
def delete_vendor(id):

    data, error, status = verify_token(request)
    if error:
        return error, status

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM Vendor WHERE VendorID=?",
        id
    )

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"message": "Vendor Not Found"}), 404

    conn.close()

    return jsonify({"message": "Vendor Deleted Successfully"})

