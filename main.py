from flask import Flask
from flask_cors import CORS
from appcustomer import customer_bp
from apppurchase import purchase_bp
from appproducts import products_bp
from appsale import sale_bp
from appvendor import vendor_bp

app = Flask(__name__)

# ADD THIS LINE
app.json.sort_keys = False

CORS(app)

# Register blueprints
app.register_blueprint(customer_bp, url_prefix='/customer')
app.register_blueprint(purchase_bp, url_prefix='/purchase')
app.register_blueprint(products_bp, url_prefix='/products')
app.register_blueprint(sale_bp, url_prefix='/sales')
app.register_blueprint(vendor_bp, url_prefix='/vendor')
@app.route("/")
def home():
    return "Flask API is running!"
if __name__ == '__main__':
    app.run(debug=True)