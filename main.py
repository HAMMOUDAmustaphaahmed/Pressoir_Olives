from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, User, TableMetadata, CompanySettings
from functools import wraps
from datetime import datetime

main_bp = Blueprint('main', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.username != 'admin':
            flash('Accès refusé. Admin requis.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_permission = current_user.access_level
            permission_levels = {
                'read_only': 1,
                'read_write': 2,
                'read_write_edit': 3,
                'full': 4
            }
            
            if permission_levels.get(user_permission, 0) < permission_levels.get(permission, 0):
                flash('Permissions insuffisantes pour cette action.', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main_bp.route('/')
@login_required
def dashboard():
    tables = TableMetadata.query.all()
    
    # Récupérer le nombre de graphiques de l'utilisateur actuel
    from models import Chart  # Ajoutez cet import en haut du fichier si nécessaire
    charts_count = Chart.query.filter_by(user_id=current_user.id).count()
    
    # Récupérer les graphiques récents de l'utilisateur actuel
    recent_charts = Chart.query.filter_by(user_id=current_user.id).order_by(Chart.created_at.desc()).limit(4).all()
    
    return render_template('dashboard.html', 
                         tables=tables, 
                         charts_count=charts_count,
                         recent_charts=recent_charts)

@main_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        access_level = request.form.get('access_level')
        
        if User.query.filter_by(username=username).first():
            flash('Nom d\'utilisateur déjà existant', 'danger')
        else:
            user = User(username=username, access_level=access_level)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Utilisateur créé avec succès', 'success')
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main_bp.route('/delete_user/<int:user_id>')
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Vous ne pouvez pas supprimer votre propre compte', 'danger')
    else:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('Utilisateur supprimé avec succès', 'success')
    
    return redirect(url_for('main.manage_users'))

@main_bp.route('/company_settings', methods=['GET', 'POST'])
@login_required
@admin_required
def company_settings():
    settings = CompanySettings.query.first()
    
    if request.method == 'POST':
        if not settings:
            settings = CompanySettings()
        
        settings.name = request.form.get('company_name')
        settings.address = request.form.get('company_address')
        settings.phone = request.form.get('company_phone')
        settings.email = request.form.get('company_email')
        
        db.session.add(settings)
        db.session.commit()
        flash('Paramètres de l\'entreprise mis à jour', 'success')
        return redirect(url_for('main.company_settings'))
    
    current_date = datetime.now()
    return render_template('company_settings.html', settings=settings, now=current_date)