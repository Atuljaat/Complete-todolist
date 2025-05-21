from flask import Flask
from todo import todo_bp
from authenticate import auth_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(todo_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
