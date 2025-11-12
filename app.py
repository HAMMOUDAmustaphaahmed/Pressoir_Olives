from flask import Flask, render_template, session, g
from flask_login import LoginManager
from config import config
from models import db, User, Season
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
    from seasons import seasons_bp  # Nouveau blueprint

    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tables_bp)
    app.register_blueprint(charts_bp)
    app.register_blueprint(pdf_bp)
    app.register_blueprint(seasons_bp)  # Nouveau blueprint

    
    # Context processor pour rendre la saison active disponible dans tous les templates
    @app.context_processor
    def inject_active_season():
        active_season = Season.query.filter_by(is_active=True).first()
        return dict(active_season=active_season)
    
    # Before request pour vérifier qu'une saison est active
    @app.before_request
    def check_active_season():
        from flask import request, flash, redirect, url_for
        from flask_login import current_user
        
        # Liste des routes qui ne nécessitent pas de saison active
        excluded_routes = [
            'auth.login', 'auth.logout', 
            'seasons.manage_seasons', 'seasons.create_season', 
            'seasons.activate_season', 'static'
        ]
        
        # Ne vérifier que si l'utilisateur est authentifié
        if current_user.is_authenticated:
            # Ne pas vérifier pour les routes exclues
            if request.endpoint not in excluded_routes and not request.endpoint.startswith('static'):
                active_season = Season.query.filter_by(is_active=True).first()
                
                # Si pas de saison active et que ce n'est pas une route de saison
                if not active_season and not request.endpoint.startswith('seasons.'):
                    if current_user.username == 'admin':
                        flash('Aucune saison active. Veuillez créer et activer une saison.', 'warning')
                        return redirect(url_for('seasons.manage_seasons'))
                    else:
                        flash('Aucune saison active. Contactez l\'administrateur.', 'warning')
    
    # Création des tables et données par défaut
    with app.app_context():
        db.create_all()
        
        # Créer l'utilisateur admin par défaut s'il n'existe pas
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(username='admin', access_level='full')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
        
        # Créer une saison par défaut si aucune n'existe
        if Season.query.count() == 0:
            from datetime import datetime
            current_year = datetime.now().year
            default_season = Season(
                name=f"{current_year}-{current_year + 1}",
                start_date=datetime(current_year, 11, 1).date(),
                end_date=datetime(current_year + 1, 4, 30).date(),
                is_active=True
            )
            db.session.add(default_season)
            db.session.commit()
            print(f"Saison par défaut créée: {default_season.name}")
    
    return app

if __name__ == '__main__':
    app = create_app('default')
    app.run(host='0.0.0.0', port=5003, debug=True)