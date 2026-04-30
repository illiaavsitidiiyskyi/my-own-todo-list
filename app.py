from flask import Flask
from models import init_db

# Імпортація Blueprint
from auth.routes import auth_bp
from todo.routes import todo_bp

app = Flask(__name__)
app.secret_key = 'my-todo-secret-key-12345'
init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(todo_bp)

if __name__ == '__main__':
    app.run(debug=True)