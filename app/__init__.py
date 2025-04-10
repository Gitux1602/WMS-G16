from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app import models
    
    # Registrar Blueprints
    from app.routes.auth import auth
    from app.routes.main import main
    from app.routes.conteo_sap import inventario_bp
    from app.routes.inventarios import inv_estado
    from app.routes.articulo_codigo import item
    
    app.register_blueprint(item)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(inv_estado)


    return app