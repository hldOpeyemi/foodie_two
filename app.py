from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, serialize_data
import json
import secrets
from middleware.auth import validate_restaurant_token, validate_token
from constants.columns import client_columns, token_columns, client_signup_columns, restaurant_columns, restaurants_columns, restuarant_signup_columns

# Routes Imports
from routes.menu import menu_bp
from routes.client import client_bp
from routes.restaurant import restaurant_bp

app = Flask(__name__)


@app.get("/")
def health_check():
  return make_response("API online", 200)

# CLIENT SECTION

@app.get("/private")
@validate_token
def private_router():
  print("this is a test")
  try:
    return make_response(jsonify("This is a private route"),  200)
  except:
    return make_response("This is an error", 400)
  


app.register_blueprint(client_bp, url_prefix='/api')
app.register_blueprint(menu_bp, url_prefix='/api')
app.register_blueprint(restaurant_bp, url_prefix='/api')


app.run(debug=True)