from flask import Flask , request , Blueprint , jsonify
import mysql.connector
import bcrypt
from flask_cors import CORS
import re
import jwt
import datetime

auth_bp = Blueprint('auth',__name__)
# CORS(auth_bp)
Secret_Key = 'mykey123'

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="todolist"
    )

def hashedPass (mypass:str):
    mypass = mypass.encode('utf-8')
    password = bcrypt.hashpw(mypass,bcrypt.gensalt())
    return ((password).decode('utf-8'))

def checkPass (mypass:str,dbpass:str) -> bool:
    mypass = mypass.encode('utf-8')
    dbpass = dbpass.encode('utf-8')
    return bcrypt.checkpw(mypass,dbpass)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    mydb = None
    cursor = None
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400
        
        errors = []
        name = data.get("name")
        
        if not name:
            errors.append("Name is required")
        elif not isinstance(name, str) or len(name) < 2 or len(name) > 50:
            errors.append("Name must be between 2 and 50 characters")
            
        # Email validation
        email = data.get("email")
        if not email:
            errors.append("Email is required")
        elif not isinstance(email, str) or not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            errors.append("Invalid email format")
            
        # Password validation
        password = data.get("password")
        if not password:
            errors.append("Password is required")
        elif not isinstance(password, str) or len(password) < 8:
            errors.append("Password must be at least 8 characters long")
            
        # Return errors if validation fails
        if errors:
            return jsonify({"errors": errors}), 400
            
        # Check if email already exists
        mydb = get_connection()
        cursor = mydb.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM USERS WHERE EMAIL = %s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409
            
        # Hash password and insert user
        hashed_password = hashedPass(password)
        
        cursor.execute(
            "INSERT INTO USERS(USERNAME, EMAIL, password_hash) VALUES(%s, %s, %s)",
            (name, email, hashed_password)
        )
        mydb.commit()
        
        # Get the user ID of the newly created user
        user_id = cursor.lastrowid
        
        # Return success response (without password)
        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }), 201
        
    except mysql.connector.Error as db_error:
        mydb.rollback() if mydb else None
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500
        
    except Exception as e:
        mydb.rollback() if mydb else None
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
        
    finally:
        if cursor:
            cursor.close()
        if mydb:
            mydb.close()

@auth_bp.route('/login',methods=['POST'])
def login():
    mydb=None
    cursor=None
    errors= []
    try:
        mydb = get_connection()
        cursor = mydb.cursor()
        data = request.get_json()
        email = data["email"]
        if email==None:
            errors.append("email is not given")
        password = data["password"]
        if password==None:
            errors.append("password is not given")
        if errors:
            return jsonify({"errors":errors}),400
        cursor.execute("select password_hash from users where email=%s",(email,))
        dbpass = (cursor.fetchone())
        if dbpass == None:
            return {"error":"user doesnt exist"},200
        if checkPass(password,dbpass[0]):
            token = jwt.encode({
                'email' : email,
                'exp' :  datetime.datetime.now() + datetime.timedelta(hours=1)
            } , Secret_Key , algorithm='HS256')
            
            return jsonify({"message":"Login successful","token":token}),200
        else :
            return jsonify({"error":"Password is wrong"})
    except Exception as e:
        return jsonify({"error" : f"Error in login : {e}"}),404
    finally:
        if cursor :
            cursor.close()
        if mydb :
            mydb.close()


@auth_bp.route("/protected",methods=["POST"])
def checkToken():
    token = request.headers.get("Authorization")
    if not token :
        return jsonify({"error":"Token is missing"}),401
    try:
        data = jwt.decode(token,Secret_Key,algorithms='HS256')
        return jsonify({"token":"login successful"}),200
    except jwt.ExpiredSignatureError :
        return jsonify({"error":"Token is expired"}),401
    except jwt.InvalidTokenError :
        return jsonify({"error":"Invalid token"}),401