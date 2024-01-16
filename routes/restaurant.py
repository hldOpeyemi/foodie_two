import secrets
from flask import Blueprint, jsonify, make_response, request
from dbhelpers import run_statement, serialize_data;

from constants.columns import client_columns, token_columns, client_signup_columns, restaurant_columns, restaurants_columns, restuarant_signup_columns
from middleware.auth import validate_restaurant_token, validate_token


restaurant_bp = Blueprint('restaurant', __name__)

@restaurant_bp.post("/restaurant-login")
def restaurant_login():
 try:
  email_address = request.json.get('email')
  password = request.json.get('password')

  # print(email_address, password)
  
  result = run_statement('CALL get_restaurant_by_email(?)', [email_address])

  # print("what is this", result)

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
 
@restaurant_bp.get("/restaurants")
# @validate_restaurant_token

def get_all_restaurant():
  
  try:

    result = run_statement('CALL get_all_restaurant')

    all_restaurants = serialize_data(restaurants_columns, result)

    return make_response(jsonify(all_restaurants),  200)
  except:
    return make_response("This is an error", 400)
  

@restaurant_bp.get("/restaurants")
@validate_restaurant_token

def get_restaurant():
  
  try:

    restaurant_id = request.args.get("id")

    result = run_statement('CALL get_restaurant_by_id(?)', [restaurant_id])

    restaurant = serialize_data(restaurants_columns, result)[0]

    return make_response(jsonify(restaurant),  200)
  except:
    return make_response("This is an error", 400)
 

@restaurant_bp.delete("/restaurant-login")
@validate_restaurant_token
def restaurant_logout():
 try:
  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  session_columns = ['restaurant_id', 'restaurant_token']
  
  result = run_statement('CALL get_restaurant_session_by_token(?)', [token])
  
  session = serialize_data(session_columns, result)[0]
  
  # print("Pikin", session)

  result = run_statement('CALL delete_restaurant_session(?)', [session['restaurant_id']])

  # print("Omobaba", session['restaurant_id'])

  return make_response(jsonify("You have successfully logged Out"),  200)
 except:
  return make_response("This is an error", 400)
 
@restaurant_bp.get("/secured")
@validate_restaurant_token
def secured_route():
  print("this is a test")
  try:
    return make_response(jsonify("This is a private route"),  200)
  except:
    return make_response("This is an error", 400)

@restaurant_bp.post("/restaurant")
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

@restaurant_bp.patch("/restaurant")
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
 
@restaurant_bp.delete("/restaurant")
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
 
