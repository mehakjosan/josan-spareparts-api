from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import pyodbc
import jwt
from datetime import datetime

# ✅ FIXED
app = Flask(__name__)

sale_bp = Blueprint("sale", __name__)

# ✅ enable CORS properly
CORS(app)

SECRET_KEY = "mysecretkey"

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost;"
    "Database=SprayerPartsDB;"
    "Trusted_Connection=yes;"
)

# ================= TOKEN VERIFY =================
def verify_token(req):
    auth = req.headers.get("Authorization")

    if not auth:
        return None, jsonify({"message": "Token Missing"}), 403

    try:
        token = auth.split(" ")[1]
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded, None, None

    except Exception as e:
        return None, jsonify({"message": str(e)}), 403


# ================= GET / POST =================
@sale_bp.route("/api/sale", methods=["GET", "POST"])
def handle_sales():

    token_data, error, status = verify_token(request)
    if error:
        return error, status

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:

        if request.method == "GET":

            cursor.execute("""
                SELECT *
                FROM Sale
                ORDER BY SaleID DESC
            """)

            columns = [column[0] for column in cursor.description]

            data = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]

            return jsonify(data)

        elif request.method == "POST":

            data = request.json

            sale_date = datetime.strptime(data["SaleDate"], "%Y-%m-%d")

            cursor.execute("""
                INSERT INTO Sale
                (
                    InvoiceNo,
                    SaleDate,
                    CustomerName,
                    PartName,
                    Quantity,
                    Price,
                    Discount,
                    TotalBill,
                    PaymentMode,
                    DeliveryDetails
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["InvoiceNo"],
                sale_date,
                data["CustomerName"],
                data["PartName"],
                float(data["Quantity"]),
                float(data["Price"]),
                float(data["Discount"]),
                float(data["TotalBill"]),
                data["PaymentMode"],
                data["DeliveryDetails"]
            ))

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Sale Saved Successfully"
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()


# ================= PUT / DELETE =================
@sale_bp.route("/api/sale/<int:id>", methods=["PUT", "DELETE"])
def modify_sale(id):

    token_data, error, status = verify_token(request)
    if error:
        return error, status

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    try:

        if request.method == "PUT":

            data = request.json

            sale_date = datetime.strptime(data["SaleDate"], "%Y-%m-%d")

            cursor.execute("""
                UPDATE Sale
                SET
                    InvoiceNo = ?,
                    SaleDate = ?,
                    CustomerName = ?,
                    PartName = ?,
                    Quantity = ?,
                    Price = ?,
                    Discount = ?,
                    TotalBill = ?,
                    PaymentMode = ?,
                    DeliveryDetails = ?
                WHERE SaleID = ?
            """,
            (
                data["InvoiceNo"],
                sale_date,
                data["CustomerName"],
                data["PartName"],
                float(data["Quantity"]),
                float(data["Price"]),
                float(data["Discount"]),
                float(data["TotalBill"]),
                data["PaymentMode"],
                data["DeliveryDetails"],
                id
            ))

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Sale Updated Successfully"
            })

        elif request.method == "DELETE":

            cursor.execute(
                "DELETE FROM Sale WHERE SaleID = ?",
                (id,)
            )

            conn.commit()

            return jsonify({
                "success": True,
                "message": "Sale Deleted Successfully"
            })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

    finally:
        conn.close()


# ================= REGISTER BLUEPRINT =================
app.register_blueprint(sale_bp, url_prefix="/sales")


# ✅ FIXED MAIN ENTRY
if __name__ == "__main__":
    app.run(debug=True)