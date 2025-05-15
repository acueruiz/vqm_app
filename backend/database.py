from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = None  # inicializamos una variable global para Flask-Migrate

# función para inicializar BBDD, con opción a migrar
def init_db(app):
    global migrate
    db.init_app(app)
    migrate = Migrate(app, db)  # habilita Flask-Migrate