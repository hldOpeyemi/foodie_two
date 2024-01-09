from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, serialize_data
import json
import secrets

app = Flask(__name__)


def validate_token(func):
 def wrapper(*args, **kwargs):

  print("Running middle ware")

  token = request.headers.get("token")
  if (token == None or token == ""):
   return make_response(jsonify("Please provide a token"), 403)
  
  result = run_statement('CALL validate_token(?)', [token])

  if (len(result) == 0):
   return make_response(jsonify("invalid token, please login"), 403)
  
  print("Jollof Rice", result)

  response = func(*args, **kwargs)


  return response
 return wrapper

def validate_restaurant_token(func):
 def restaurant_wrapper(*args, **kwargs):

  print("Running middle ware")

  token = request.headers.get("token")
  if (token == None or token == ""):
   return make_response(jsonify("Please provide a token"), 403)
  
  result = run_statement('CALL validate_restaurant_token(?)', [token])

  if (len(result) == 0):
   return make_response(jsonify("invalid token, please login"), 403)
  
  print("FriedRice", result)

  response = func(*args, **kwargs)


  return response
 return restaurant_wrapper

client_columns = ['id', 'first_name', 'last_name', 'image_url', 'username','password', 'email_address']
restaurant_columns = ['id', 'name', 'email_address', 'address', 'phone_number', 'bio','city', 'profile_url', 'banner_url', 'password']
token_columns = ['client_id', 'token']

@app.get("/")
def health_check():
  return make_response("API online", 200)

# CLIENT SECTION

@app.post("/api/client-login")
def client_login():
 try:
  email_address = request.json.get('email')
  password = request.json.get('password')
  
  result = run_statement('CALL get_client_by_email(?)', [email_address])
  # print(len(result)) 

  if (len(result)<1):
   return make_response(jsonify("Email not in use"), 401)
  print(result)
  client = serialize_data(client_columns, result)[0]

  if (client["password"] != password):
   return make_response(jsonify("Wrong Password"), 403)
  
  result = run_statement('CALL delete_session(?)', [client["id"]])

  token_string = secrets.token_hex(16)
  print(token_string)
  result = run_statement('CALL post_client_login(?,?)', [client["id"], token_string])

  token = serialize_data(token_columns, result)[0]

  return make_response(jsonify(token),  200)
 
 except:
  return make_response("This is an error", 400)

@app.get("/private")
@validate_token
def private_router():
  print("this is a test")
  try:
    return make_response(jsonify("This is a private route"),  200)
  except:
    return make_response("This is an error", 400)
  
@app.post("/api/client")
def client_signup():
 try:
  first_name = request.json.get('first_name')
  last_name = request.json.get('last_name')
  email_address = request.json.get('email address')
  image_url = request.json.get ('image_url')
  username =request.json.get ('username')
  password = request.json.get('password')
  
  result = run_statement('CALL client_signup(?,?,?,?,?)', [first_name, last_name, email_address, image_url, username, password])
  
  print(result)
  client = serialize_data(client_columns, result)[0]

  return make_response(jsonify(client),  200)
 except:
  return make_response("This is an error", 400)

# RESTAURANT SECTION

@app.post("/api/restaurant-login")
def restaurant_login():
 try:
  email_address = request.json.get('email')
  password = request.json.get('password')

  print(email_address, password)
  
  result = run_statement('CALL get_restaurant_by_email(?)', [email_address])

  print("what is this", result)

  if (len(result)<1):
   return make_response(jsonify("Email not in use"), 401)
  
  restaurant = serialize_data(restaurant_columns, result)[0]

  if (restaurant["password"] != password):
   return make_response(jsonify("Wrong Password"), 403)
  
  result = run_statement('CALL delete_restaurant_session(?)', [restaurant["id"]])

  token_string = secrets.token_hex(16)
  
  result = run_statement('CALL post_restaurant_login(?,?)', [ restaurant["id"], token_string])

  token = serialize_data(token_columns, result)[0]

  return make_response(jsonify(token),  200)
 except:
  return make_response("This is an error", 400)

@app.get("/secured")
@validate_restaurant_token
def secured_route():
  print("this is a test")
  try:
    return make_response(jsonify("This is a private route"),  200)
  except:
    return make_response("This is an error", 400)



app.run(debug=True)