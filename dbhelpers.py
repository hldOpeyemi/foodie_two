import mariadb
import dbcreds

def connect_db():
 try:
   conn = mariadb.connect(
    user=dbcreds.user, 
    password=dbcreds.password,
    host=dbcreds.host, 
    port=dbcreds.port, 
    database=dbcreds.database
   )
   cursor = conn.cursor()
   return cursor
 except mariadb.OperationalError as error:
   print("OPERATIONAL ERROR:", error)
 except Exception as error:
   print("UNEXPECTED ERROR:", error)
   
def execute_statement(cursor, statement, list_of_args=[]):
  try:
    print(list_of_args)
    cursor.execute(statement, list_of_args)
    results = cursor.fetchall()
    return results
  except mariadb.ProgrammingError as error:
    print("PROGRAMMING ERROR:", error)
    return error
  except mariadb.IntegrityError as error:
    print("INTEGRITY ERROR:", error)
    return error
  except mariadb.DataError as error:
    print("DATA ERROR:", error)
    return error
  except Exception as error:
    print("UNEXPECTED ERROR:", error)
    return error
    
def close_connection(cursor):
  try:
    conn = cursor.connection
    cursor.close()
    conn.close()
    print("Disconnected from database")
  except mariadb.OperationalError as error:
    print("OPERATIONAL ERROR:", error)
  except mariadb.InternalError as error:
    print("INTERNAL ERROR:", error)
  except Exception as error:
    print("UNEXPECTED ERROR:", error)
    
def run_statement(statement, list_of_args=[]):
  cursor = connect_db()
  
  if(cursor == None):
    return "Connection Error"
  
  results = execute_statement(cursor, statement, list_of_args)
  close_connection(cursor)
  return results
  
  
def serialize_data(columns, data):
 sql_data_dict = [dict(zip(columns, row)) for row in data]
 return sql_data_dict