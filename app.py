from flask import Flask, render_template
from flask_login import LoginManager
from config import config
from models import db, User
import os
from flask_migrate import Migrate

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialisation des extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Configuration de Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Enregistrement des blueprints
    from auth import auth_bp
    from main import main_bp
    from tables import tables_bp
    from charts import charts_bp
    from pdf_export import pdf_bp

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(charts_bp)
    app.register_blueprint(pdf_bp)

    
    # Création des tables et admin par défaut
    with app.app_context():
        db.create_all()
        # Créer l'utilisateur admin par défaut s'il n'existe pas
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', access_level='full')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
    
    return app

if __name__ == '__main__':
    app = create_app('default')
    app.run(host='0.0.0.0', port=5003, debug=True)