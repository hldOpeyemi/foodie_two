from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, serialize_data

def validate_token(func):
 def wrapper(*args, **kwargs):

  print("Running middle ware")

  token = request.headers.get("token")
  if (token == None or token == ""):
   return make_response(jsonify("Please provide a token"), 403)
  
  result = run_statement('CALL validate_token(?)', [token])

  if (len(result) == 0):
   return make_response(jsonify("invalid token, please login"), 403)
  
  # print("Jollof Rice", result)

  response = func(*args, **kwargs)



  return response
  #Renaming the function name:
 wrapper.__name__ = func.__name__
 return wrapper

def validate_restaurant_token(func):
 def restaurant_wrapper(*args, **kwargs):

  # print("Running middle ware")

  token = request.headers.get("token")
  if (token == None or token == ""):
   return make_response(jsonify("Please provide a token"), 403)
  
  result = run_statement('CALL validate_restaurant_token(?)', [token])

  if (len(result) == 0):
   return make_response(jsonify("invalid token, please login"), 403)
  
  # print("FriedRice", result)

  response = func(*args, **kwargs)


  return response
 restaurant_wrapper.__name__ = func.__name__
 return restaurant_wrapper