from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, serialize_data
import json
import secrets
from middleware.auth import validate_restaurant_token, validate_token
from constants.columns import client_columns, token_columns, client_signup_columns, restaurant_columns, restaurants_columns, restuarant_signup_columns

# Routes Imports
from routes.menu import menu_bp
from routes.client import client_bp

app = Flask(__name__)



# client_columns = ['id', 'first_name', 'last_name', 'image_url', 'username', 'password', 'email_address']
# client_signup_columns = ['id', 'username']
# restaurant_columns = ['id', 'name', 'email_address', 'address', 'phone_number', 'bio','city', 'profile_url', 'banner_url', 'password']
# token_columns = ['client_id', 'token']
# restuarant_signup_columns = ['id', 'name', 'email_address']
# restaurants_columns = ['id', 'name', 'email_address', 'address', 'phone_number', 'bio','city', 'profile_url', 'banner_url']


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
  

@app.get("/api/client")
# @validate_token
# add validate_token if you want the user to sign in first before viewing another user
def get_client():
  # print(request.args.get("client_id"))
  try:

    client_id = request.args.get("id")

    result = run_statement('CALL get_client_by_id(?)', [client_id])

    # print("Fried", client_id)

    return make_response(jsonify(result),  200)
  except:
    return make_response("This is an error", 400)
   
  # print("CHECK THIS", token)


@app.get("/api/clients")
@validate_token
# add validate_token if you want the user to sign in first before viewing another user
def get_all_clients():
  # print(request.args.get("client_id"))
  try:

    result = run_statement('CALL get_all_clients')

    return make_response(jsonify(result),  200)
  except:
    return make_response("This is an error", 400)
   
  
@app.delete("/api/client-login")
@validate_token
def client_logout():
 try:
  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  session_columns = ['client_id', 'token']
  
  result = run_statement('CALL get_session_by_token(?)', [token])

  session = serialize_data(session_columns, result)[0]
  
  print("Pikin", session)

  result = run_statement('CALL delete_session(?)', [session['client_id']])

  print("Omobaba", session['client_id'])

  return make_response(jsonify("You have successfully logged Out"),  200)
 except:
  return make_response("This is an error", 400)


  
@app.post("/api/client")
def client_signup():
 try:
  first_name = request.json.get('first_name')
  last_name = request.json.get('last_name')
  image_url = request.json.get ('image_url')
  username =request.json.get ('username')
  password = request.json.get('password')
  email_address = request.json.get('email_address')
  
  result = run_statement('CALL client_signup(?,?,?,?,?,?)', [first_name, last_name, image_url, username, password, email_address])
  
  # print(result)

  client = serialize_data(client_signup_columns, result)[0]

  # print(client)

  return make_response(jsonify(client),  200)
 except:
  return make_response("This is an error", 400)
 

@app.patch("/api/client")
@validate_token
def client_update():
 try:

  # Creating a empty obj to hold either passed value or None for later updating
  client_data = {}

  # TO DO

  client_data['first_name'] = request.json.get('first_name') if request.json.get('first_name') else None
  client_data['last_name'] = request.json.get('last_name') if request.json.get('last_name') else None
  client_data['email_address'] = request.json.get('email_address') if request.json.get('email_address') else None
  client_data['image_url'] = request.json.get('image_url') if request.json.get('image_url') else None
  client_data['username'] = request.json.get('username') if request.json.get('username') else None
  client_data['password'] = request.json.get('password') if request.json.get('password') else None
  

  # print(client_data)

  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  session_columns = ['client_id', 'token']

  result = run_statement('CALL get_session_by_token(?)', [token])
  
  session = serialize_data(session_columns, result)[0]

  # print(session)
  
  result = run_statement(
   'CALL update_client(?,?,?,?,?,?,?)', 
   [
    session['client_id'],
    client_data['first_name'],
    client_data['last_name'], 
    client_data['email_address'],
    client_data['image_url'],
    client_data['username'],
    client_data['password'] 
  ]
  )
  
  print(result)
  # client = serialize_data(client_columns, result)[0]

  return make_response(jsonify("Client succesfully updated"),  200)
 except:
  return make_response("This is an error", 400)
 
@app.delete("/api/client")
@validate_token
def delete_client():
 try:
  
  password_input = request.json.get('password')
  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  result = run_statement('CALL get_session_by_token(?)', [token])

  session = result[0]
  id = session[0]

  result = run_statement('CALL get_client_by_id(?)',[id])
  
  client=result[0]
  # print(restaurant)
  password = client[5]
  # print(password)
  id = client[0]
  # print(id)

  if (password != password_input):
    return make_response(jsonify("Wrong Password"), 403)
  
  result = run_statement('CALL delete_client(?)', [id])

  return make_response(jsonify("Client Deleted"),  200)
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
 
@app.get("/api/restaurants")
# @validate_restaurant_token

def get_all_restaurant():
  
  try:

    result = run_statement('CALL get_all_restaurant')

    all_restaurants = serialize_data(restaurants_columns, result)[0]

    return make_response(jsonify(all_restaurants),  200)
  except:
    return make_response("This is an error", 400)
  

@app.get("/api/restaurants")
@validate_restaurant_token

def get_restaurant():
  
  try:

    restaurant_id = request.args.get("id")

    result = run_statement('CALL get_restaurant_by_id(?)', [restaurant_id])

    restaurant = serialize_data(restaurants_columns, result)[0]

    return make_response(jsonify(restaurant),  200)
  except:
    return make_response("This is an error", 400)
 

@app.delete("/api/restaurant-login")
@validate_restaurant_token
def resturant_logout():
 try:
  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  session_columns = ['restaurant_id', 'restaurant_token']
  
  result = run_statement('CALL get_restaurant_session_by_token(?)', [token])
  
  session = serialize_data(session_columns, result)[0]
  
  print("Pikin", session)

  result = run_statement('CALL delete_restaurant_session(?)', [session['restaurant_id']])

  print("Omobaba", session['restaurant_id'])

  return make_response(jsonify("You have successfully logged Out"),  200)
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

@app.post("/api/restaurant")
def restaurant_signup():
 try:
  name = request.json.get('name') 
  email_address = request.json.get('email_address') 
  address = request.json.get('address') 
  phone_number = request.json.get('phone_number') 
  bio = request.json.get('bio') 
  city = request.json.get('city') 
  profile_url = request.json.get('profile_url')
  banner_url = request.json.get('banner_url') 
  password = request.json.get('password') 
  
  result = run_statement('CALL restaurant_signup(?,?,?,?,?,?,?,?,?)', [name, email_address, address, phone_number, bio, city, profile_url, banner_url, password])
  
  # print(result)

  restaurant = serialize_data(restuarant_signup_columns, result)[0]

  # print(client)

  return make_response(jsonify(restaurant),  200)
 except:
  return make_response("This is an error", 400)

@app.patch("/api/restaurant")
@validate_restaurant_token
def restaurant_update():
 try:

  # Creating a empty obj to hold either passed value or None for later updating
  restaurant_data = {}

  # TO DO

  restaurant_data['name'] = request.json.get('name') if request.json.get('name') else None
  restaurant_data['email_address'] = request.json.get('email_address') if request.json.get('email_address') else None
  restaurant_data['address'] = request.json.get('address') if request.json.get('address') else None
  restaurant_data['phone_number'] = request.json.get('phone_number') if request.json.get('phone_number') else None
  restaurant_data['bio'] = request.json.get('bio') if request.json.get('bio') else None
  restaurant_data['city'] = request.json.get('city') if request.json.get('city') else None
  restaurant_data['profile_url'] = request.json.get('profile_url') if request.json.get('profile_url') else None
  restaurant_data['banner_url'] = request.json.get('banner_url') if request.json.get('banner_url') else None
  restaurant_data['password'] = request.json.get('password') if request.json.get('password') else None
  

  # print(client_data)

  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  session_columns = ['restaurant_id', 'restaurant_token']

  result = run_statement('CALL get_restaurant_session_by_token(?)', [token])
  
  session = serialize_data(session_columns, result)[0]

  # print(session)
  
  result = run_statement(
   'CALL update_restaurant(?,?,?,?,?,?,?,?,?,?)', 
   [
    session['restaurant_id'],
    restaurant_data['name'],
    restaurant_data['email_address'],
    restaurant_data['address'],
    restaurant_data['phone_number'],
    restaurant_data['bio'],
    restaurant_data['city'],
    restaurant_data['profile_url'],
    restaurant_data['banner_url'],
    restaurant_data['password']
  ]
  )
  
  print(result)
  # client = serialize_data(client_columns, result)[0]

  return make_response(jsonify("Restaurant succesfully updated"),  200)
 except:
  return make_response("This is an error", 400)
 
@app.delete("/api/restaurant")
@validate_restaurant_token
def delete_resturant():
 try:
  
  password_input = request.json.get('password')
  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  result = run_statement('CALL get_restaurant_session_by_token(?)', [token])

  session = result[0]
  id = session[0]

  result = run_statement('CALL get_restaurant_by_id(?)',[id])
  
  restaurant=result[0]
  # print(restaurant)
  password = restaurant[9]
  # print(password)
  id = restaurant[0]
  # print(id)

  if (password != password_input):
    return make_response(jsonify("Wrong Password"), 403)
  
  result = run_statement('CALL delete_restaurant(?)', [id])

  return make_response(jsonify("Restaurant Deleted"),  200)
 except:
  return make_response("This is an error", 400)
 

app.register_blueprint(client_bp)
app.register_blueprint(menu_bp, url_prefix='/menu')


app.run(debug=True)