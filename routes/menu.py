from flask import Blueprint, jsonify, make_response, request
from dbhelpers import run_statement, serialize_data
from constants.columns import client_columns, token_columns, client_signup_columns, restaurant_columns, restaurants_columns, restuarant_signup_columns, menu_columns

from middleware.auth import validate_restaurant_token, validate_token;

menu_bp = Blueprint('menu', __name__)

@menu_bp.route('/test')
def menu_test():
  return "This is a test"  

@menu_bp.get("/allmenu")
@validate_restaurant_token
# add validate_token if you want the user to sign in first before viewing another user
def get_all_menu():
  # print(request.args.get("client_id"))
  try:

    result = run_statement('CALL get_all_menu')

    return make_response(jsonify(result),  200)
  except:
    return make_response("This is an error", 400)

@menu_bp.get("/menu")

def get_menu_by_id():
 try:

  restaurant_id = request.args.get('restaurant_id')

  result = run_statement('CALL get_menu_item_by_id(?)', [restaurant_id])

  menu = serialize_data(menu_columns, result)

  return make_response(jsonify(menu),  200)
 except:
  return make_response("This is an error", 400)
 

@menu_bp.post("/menu")
@validate_restaurant_token
def add_dish_to_menu():
 try:
  
  token = request.headers.get('token')
  result = run_statement('CALL get_restaurant_session_by_token(?)', [token])

  session = result[0]
  id = session[0] 


  name = request.json.get('name') 
  description = request.json.get('description') 
  image_url = request.json.get('image_url')
  price = request.json.get('price') 
  restaurant_id = request.args.get('restaurant_id') 

  if (restaurant_id == None or restaurant_id == ""):
    return make_response(jsonify("Please provide a restaurant_id"), 403)
  
  print("id", id, type(id), "----", "restaurant_id", restaurant_id, type(restaurant_id))

  if (id != int(restaurant_id)):
   return make_response(jsonify("Wrong Restaurant"), 403)
      
  result = run_statement('CALL add_item_to_menu(?,?,?,?,?)', [name, description, image_url, price, restaurant_id])
  
  new_dish = serialize_data(menu_columns, result)[0]

  return make_response(jsonify(new_dish),  200)
 except:
  return make_response("This is an error", 400)
 

@menu_bp.delete("/menu")
@validate_restaurant_token
def delete_menu_item():
 try:
  menu_id = request.json.get('id')
  token = request.headers.get('token')
  
  result = run_statement('CALL get_restaurant_session_by_token(?)', [token])

  session = result[0]
  id = session[0]

  print("Wura", id)

  restaurant_id = request.args.get("restaurant_id")

  print("Wara", restaurant_id)
  
  print("menu", menu_id)

  result = run_statement('CALL delete_menu_item(?)', [menu_id]) 
  
  return make_response(jsonify("Menu Deleted"),  200)

 except:
  return make_response("This is an error", 400)
 
@menu_bp.patch("/menu")
@validate_restaurant_token
def update_dish():
 try:

  # Creating a empty obj to hold either passed value or None for later updating
  menu_data = {}

  menu_data['id'] = request.json.get('id')
  menu_data['name'] = request.json.get('name') if request.json.get('name') else None
  menu_data['description'] = request.json.get('description') if request.json.get('description') else None
  menu_data['image_url'] = request.json.get('image_url') if request.json.get('image_url') else None
  menu_data['price'] = request.json.get('price') if request.json.get('price') else None

  result = run_statement(
   'CALL update_menu_item(?,?,?,?,?)', 
   [
    menu_data['id'],
    menu_data['name'],
    menu_data['description'],
    menu_data['image_url'],
    menu_data['price']
   ]
  )

  # print(result)
  updated_dish = serialize_data(menu_columns, result)[0]

  # return updated_dish

  return make_response(jsonify("Dish succesfully updated"), 200)
 except:
  return make_response("This is an error", 400)