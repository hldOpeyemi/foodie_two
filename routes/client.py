import secrets
from flask import Blueprint, jsonify, make_response, request
from dbhelpers import run_statement, serialize_data;

from constants.columns import client_columns, token_columns, client_signup_columns, restaurant_columns, restaurants_columns, restuarant_signup_columns
from middleware.auth import validate_token


client_bp = Blueprint('client', __name__)

@client_bp.post("/client-login")
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

@client_bp.get("/client")
# @validate_token
# add validate_token if you want the user to sign in first before viewing another user
def get_client():
  # print(request.args.get("client_id"))
  try:

    client_id = request.args.get("id")

    result = run_statement('CALL get_client_by_id(?)', [client_id])

    client=serialize_data(client_columns, result)[0]

    # print("Fried", client_id)

    return make_response(jsonify(client),  200)
  except:
    return make_response("This is an error", 400)
   
  # print("CHECK THIS", token)

@client_bp.get("/clients")
@validate_token
# add validate_token if you want the user to sign in first before viewing another user
def get_all_clients():
  # print(request.args.get("client_id"))
  try:

    result = run_statement('CALL get_all_clients')

    return make_response(jsonify(result),  200)
  except:
    return make_response("This is an error", 400)
  

@client_bp.delete("/client-login")
@validate_token
def client_logout():
 try:
  token = request.headers.get('token')
  # print("CHECK THIS", token)
  
  session_columns = ['client_id', 'token']
  
  result = run_statement('CALL get_session_by_token(?)', [token])

  session = serialize_data(session_columns, result)[0]
  
  # print("Pikin", session)

  result = run_statement('CALL delete_session(?)', [session['client_id']])

  # print("Omobaba", session['client_id'])

  return make_response(jsonify("You have successfully logged Out"),  200)
 except:
  return make_response("This is an error", 400)
 
@client_bp.post("/client")
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
 

@client_bp.patch("/client")
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
 
@client_bp.delete("/client")
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