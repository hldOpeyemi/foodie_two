from flask import Flask, request, jsonify, make_response
from dbhelpers import run_statement, serialize_data
import json
import secrets

app = Flask(__name__)

client_columns = ['id', 'first_name', 'last_name', 'image_url', 'username','password', 'email_address']
token_columns = ['client_id', 'token']

@app.get("/")
def health_check():
  return make_response("API online", 200)

@app.post("/api/client-login")
def client_login():
 try:
  email_address = request.json.get('email')
  password = request.json.get('password')
  
  result = run_statement('CALL get_client_by_email(?)', [email_address])
  # print(len(result)) 

  if (len(result)<1):
   return make_response(jsonify("Email not in use"), 401)
  
  user = serialize_data(client_columns, result)[0]

  if (user["password"] != password):
   return make_response(jsonify("Wrong Password"), 403)
  
  result = run_statement('CALL delete_session(?)', [user["id"]])

  token_string = secrets.token_hex(16)
  print(token_string)
  result = run_statement('CALL post_client_login(?,?)', [ user["id"] ,token_string  ])

  token = serialize_data(token_columns, result)[0]

  return make_response(jsonify(token),  200)
 except:
  return make_response("This is an error", 400)









app.run(debug=True)