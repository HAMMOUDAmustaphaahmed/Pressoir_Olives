from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from models import db, Season, TableMetadata, Chart
from main import admin_required
from datetime import datetime
from sqlalchemy import text

seasons_bp = Blueprint('seasons', __name__)

def get_active_season():
    """Récupère la saison active ou None"""
    return Season.query.filter_by(is_active=True).first()

def set_active_season(season_id):
    """Définit une saison comme active"""
    # Désactiver toutes les saisons
    Season.query.update({'is_active': False})
    
    # Activer la saison sélectionnée
    season = Season.query.get(season_id)
    if season:
        season.is_active = True
        db.session.commit()
        session['active_season_id'] = season_id
        return True
    return False

@seasons_bp.route('/manage_seasons')
@login_required
@admin_required
def manage_seasons():
    """Page de gestion des saisons"""
    seasons = Season.query.order_by(Season.start_date.desc()).all()
    active_season = get_active_season()
    
    # Récupérer les statistiques pour chaque saison
    season_stats = []
    for season in seasons:
        tables_count = TableMetadata.query.filter_by(season_id=season.id).count()
        charts_count = Chart.query.filter_by(season_id=season.id).count()
        season_stats.append({
            'season': season,
            'tables_count': tables_count,
            'charts_count': charts_count
        })
    
    return render_template('manage_seasons.html', 
                         season_stats=season_stats, 
                         active_season=active_season)

@seasons_bp.route('/create_season', methods=['GET', 'POST'])
@login_required
@admin_required
def create_season():
    """Créer une nouvelle saison"""
    if request.method == 'POST':
        name = request.form.get('season_name')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        make_active = request.form.get('make_active') == 'on'
        
        # Validation
        if not name or not start_date_str or not end_date_str:
            flash('Tous les champs sont obligatoires', 'danger')
            return redirect(url_for('seasons.create_season'))
        
        # Vérifier si le nom existe déjà
        if Season.query.filter_by(name=name).first():
            flash('Une saison avec ce nom existe déjà', 'danger')
            return redirect(url_for('seasons.create_season'))
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            if end_date <= start_date:
                flash('La date de fin doit être après la date de début', 'danger')
                return redirect(url_for('seasons.create_season'))
            
            # Créer la saison
            season = Season(
                name=name,
                start_date=start_date,
                end_date=end_date,
                is_active=False
            )
            
            db.session.add(season)
            db.session.commit()
            
            # Si demandé, activer cette saison
            if make_active:
                set_active_season(season.id)
                flash(f'Saison "{name}" créée et activée avec succès', 'success')
            else:
                flash(f'Saison "{name}" créée avec succès', 'success')
            
            return redirect(url_for('seasons.manage_seasons'))
            
        except ValueError:
            flash('Format de date invalide', 'danger')
            return redirect(url_for('seasons.create_season'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création de la saison: {str(e)}', 'danger')
            return redirect(url_for('seasons.create_season'))
    
    return render_template('create_season.html')

@seasons_bp.route('/activate_season/<int:season_id>')
@login_required
@admin_required
def activate_season(season_id):
    """Activer une saison"""
    if set_active_season(season_id):
        season = Season.query.get(season_id)
        flash(f'Saison "{season.name}" activée avec succès', 'success')
    else:
        flash('Erreur lors de l\'activation de la saison', 'danger')
    
    return redirect(url_for('seasons.manage_seasons'))

@seasons_bp.route('/delete_season/<int:season_id>', methods=['POST'])
@login_required
@admin_required
def delete_season(season_id):
    """Supprimer une saison et toutes ses données"""
    try:
        season = Season.query.get_or_404(season_id)
        
        # Vérifier si c'est la saison active
        if season.is_active:
            flash('Impossible de supprimer la saison active. Activez une autre saison d\'abord.', 'danger')
            return redirect(url_for('seasons.manage_seasons'))
        
        # Récupérer toutes les tables de cette saison
        tables = TableMetadata.query.filter_by(season_id=season_id).all()
        
        # Supprimer les tables physiques
        for table in tables:
            try:
                sql = text(f"DROP TABLE IF EXISTS `{table.name}`")
                db.session.execute(sql)
            except Exception as e:
                print(f"Erreur lors de la suppression de la table {table.name}: {e}")
        
        # Supprimer la saison (cascade supprimera les métadonnées)
        season_name = season.name
        db.session.delete(season)
        db.session.commit()
        
        flash(f'Saison "{season_name}" et toutes ses données supprimées avec succès', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la saison: {str(e)}', 'danger')
    
    return redirect(url_for('seasons.manage_seasons'))

@seasons_bp.route('/archive_season/<int:season_id>')
@login_required
@admin_required
def archive_season(season_id):
    """Archiver une saison (désactiver sans supprimer)"""
    season = Season.query.get_or_404(season_id)
    
    if season.is_active:
        flash('Impossible d\'archiver la saison active. Activez une autre saison d\'abord.', 'danger')
    else:
        flash(f'La saison "{season.name}" est déjà archivée', 'info')
    
    return redirect(url_for('seasons.manage_seasons'))

@seasons_bp.route('/duplicate_season/<int:season_id>', methods=['POST'])
@login_required
@admin_required
def duplicate_season(season_id):
    """Dupliquer la structure d'une saison (tables uniquement, pas les données)"""
    try:
        source_season = Season.query.get_or_404(season_id)
        new_season_name = request.form.get('new_season_name')
        
        if not new_season_name:
            flash('Le nom de la nouvelle saison est obligatoire', 'danger')
            return redirect(url_for('seasons.manage_seasons'))
        
        # Vérifier si le nom existe déjà
        if Season.query.filter_by(name=new_season_name).first():
            flash('Une saison avec ce nom existe déjà', 'danger')
            return redirect(url_for('seasons.manage_seasons'))
        
        # Créer la nouvelle saison
        new_season = Season(
            name=new_season_name,
            start_date=datetime.now().date(),
            end_date=datetime.now().date(),
            is_active=False
        )
        db.session.add(new_season)
        db.session.flush()
        
        # Dupliquer les tables
        tables = TableMetadata.query.filter_by(season_id=season_id).all()
        for table in tables:
            new_table = TableMetadata(
                name=table.name,
                display_name=table.display_name,
                season_id=new_season.id
            )
            db.session.add(new_table)
            db.session.flush()
            
            # Dupliquer les colonnes
            for column in table.columns:
                new_column = ColumnMetadata(
                    name=column.name,
                    display_name=column.display_name,
                    type=column.type,
                    table_id=new_table.id
                )
                db.session.add(new_column)
            
            # Créer la table physique
            from tables import create_physical_table
            columns_data = [{'name': col.name, 'type': col.type} for col in table.columns]
            create_physical_table(table.name, columns_data)
        
        db.session.commit()
        flash(f'Saison "{new_season_name}" créée avec la structure de "{source_season.name}"', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la duplication: {str(e)}', 'danger')
    
    return redirect(url_for('seasons.manage_seasons'))