from flask import Flask , jsonify , request , Blueprint
import mysql.connector
import time
from datetime import datetime
from flask_cors import CORS
import jwt


todo_bp = Blueprint('todo',__name__)
# CORS(todo_bp)
Secret_Key = 'mykey123'

def getconnection ():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="todolist"
    )

@todo_bp.route('/todo',methods=["POST"])
def addTodo():
    try :
        mydb = getconnection()
        cursor = mydb.cursor(dictionary=True)
        token = request.headers.get("Authorization")
        data = jwt.decode(token,Secret_Key,algorithms=["HS256"])
        email = data.get("email")
        cursor.execute("select id from users where email=%s",(email,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error":"user doesnt exist"}),401
        userid  = result.get("id")
        data = request.get_json()
        todo = data["todo"]
        createAt = datetime.now()
        cursor.execute("insert into todos(todo,createdAt,user) values(%s,%s,%s)",(todo,createAt,userid))
        mydb.commit()
        cursor.execute("""SELECT todos.* FROM todos JOIN users ON todos.user = users.id WHERE users.email = %s ORDER BY todos.id DESC LIMIT 1""", (email,))
        singleTodo = cursor.fetchall()
        cursor.close()
        return jsonify({"info":"success","todo":singleTodo}),200 
    except jwt.InvalidTokenError :
        return jsonify({"error":"token is invalid"}),401
    except jwt.ExpiredSignatureError :
        return jsonify({"error":"token is expired"}) 
    except Exception as e :
        return f"Error : {e}",401
    finally :
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()

@todo_bp.route("/all",methods=["POST"])
def displayTodo():
    try :
        mydb = getconnection()
        cursor = mydb.cursor(dictionary=True)
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error":"token doesnt exist"}),401
        token_data = jwt.decode(token,Secret_Key,algorithms=["HS256"])
        email = token_data.get("email")
        cursor.execute("SELECT todos.* FROM todos JOIN users ON todos.user = users.id WHERE users.email=%s;",(email,))
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data),200
    except Exception as e :
        return f"Error : {e}",404
    finally :
        cursor.close()
        mydb.close()

@todo_bp.route('/<int:id>')
def getSingleTodo (id):
    try :
        mydb = getconnection()
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("select * from todos where id=%s",(id,))
        data = cursor.fetchall()
        cursor.close()
        return data,200
    except Exception as e :
        return f"Error : {e}",404
    finally :
        cursor.close()
        mydb.close() # this is not in use

@todo_bp.route('/update',methods=["POST"])
def updateTodo() :
    try :
        email , errors , status = checkToken()
        if errors :
            return errors,status
        mydb = getconnection()
        data = request.get_json()
        id = data["id"]
        updateTodo = data["todo"]
        print(id,updateTodo)
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("""
        UPDATE todos
        JOIN users ON todos.user = users.id
        SET todos.todo = %s
        WHERE todos.id = %s AND users.email = %s
        """, (updateTodo, id, email))
        mydb.commit()
        return "task updated successfully",200
    except Exception as e :
        return f"Error : {e}",404
    finally :
        cursor.close()
        mydb.close()

@todo_bp.route("/delete",methods=["POST"])
def deleteTodo ():
    cursor = None
    mydb = None
    try:
        email , errors , status = checkToken()
        if errors :
            return errors,status
        data = request.get_json()
        id = data["id"]
        mydb = getconnection()
        cursor = mydb.cursor()
        cursor.execute("""
        DELETE todos
        FROM todos
        JOIN users ON todos.user = users.id
        WHERE todos.id = %s AND users.email = %s
        """, (id, email))
        mydb.commit()
        return jsonify({"message":"Delete successfully"}),200
    except Exception as e:
        return f"Error {e}",404
    finally :
        if cursor:
            cursor.close()
        if mydb :
            mydb.close()

def checkToken ():
    try:
        token = request.headers.get("Authorization")
        if not token:
            return None,jsonify({"error":"token not found"}),200
        data = jwt.decode(token,Secret_Key,algorithms=["HS256"])
        email = data.get("email")
        if email :
            return email , None,200
        else :
            return None , jsonify({"error" : "email not found"}),404
    except jwt.ExpiredSignatureError as e :
        return None , jsonify({"error" : "Token expired"}),401
    except jwt.InvalidTokenError as e :
        return None , jsonify({"error": "invalid token"}),401
    except Exception as e :
        return None , jsonify({"error": e}),500

if __name__ == "__main__":
    todo_bp.run(debug=True)