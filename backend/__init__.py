import os
from flask import Flask
from dotenv import load_dotenv
from flask_login import LoginManager
from .database import init_db
from .routes import api_blueprint
from .models import Usuario  # Importar el modelo de usuario

# Cargar variables de entorno
load_dotenv()

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configurar base de datos desde variables de entorno
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
        f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'clave_secreta')  # Necesario para sesiones

    # Inicializar base de datos
    init_db(app)

    # Inicializar Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = "login"

    # Registrar rutas
    app.register_blueprint(api_blueprint)

    return app

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))