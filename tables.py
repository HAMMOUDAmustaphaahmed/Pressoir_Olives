from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, TableMetadata, ColumnMetadata, Season
from main import permission_required
import json
from sqlalchemy import text 
from sqlalchemy.orm import joinedload

tables_bp = Blueprint('tables', __name__)

def get_active_season():
    """Récupère la saison active"""
    return Season.query.filter_by(is_active=True).first()

@tables_bp.route('/create_table', methods=['GET', 'POST'])
@login_required
@permission_required('full')
def create_table():
    active_season = get_active_season()
    
    if not active_season:
        flash('Aucune saison active. Veuillez activer une saison d\'abord.', 'danger')
        return redirect(url_for('seasons.manage_seasons'))
    
    if request.method == 'POST':
        table_name = request.form.get('table_name')
        display_name = request.form.get('display_name')
        columns_json = request.form.get('columns', '[]')
        
        # Vérifier les champs obligatoires
        if not table_name or not display_name:
            flash('Le nom technique et le nom d\'affichage sont obligatoires', 'danger')
            return redirect(url_for('tables.create_table'))
        
        try:
            columns = json.loads(columns_json)
        except json.JSONDecodeError as e:
            flash('Format de colonnes invalide', 'danger')
            return redirect(url_for('tables.create_table'))
        
        # Vérifier qu'il y a au moins une colonne
        if not columns:
            flash('Vous devez ajouter au moins une colonne', 'danger')
            return redirect(url_for('tables.create_table'))
        
        # Vérifier si la table existe déjà DANS CETTE SAISON
        if TableMetadata.query.filter_by(name=table_name, season_id=active_season.id).first():
            flash(f'Une table avec ce nom existe déjà dans la saison {active_season.name}', 'danger')
            return redirect(url_for('tables.create_table'))
        
        try:
            # Créer la table dans la base de données
            table = TableMetadata(
                name=table_name, 
                display_name=display_name,
                season_id=active_season.id  # Associer à la saison active
            )
            db.session.add(table)
            db.session.flush()
            
            # Ajouter les colonnes
            for col in columns:
                column = ColumnMetadata(
                    name=col['name'],
                    display_name=col['display_name'],
                    type=col['type'],
                    table_id=table.id
                )
                db.session.add(column)
            
            db.session.commit()
            
            # Créer la table physique dans la base de données
            create_physical_table(table_name, columns)
            
            flash(f'Table "{display_name}" créée avec succès dans la saison {active_season.name}', 'success')
            return redirect(url_for('tables.manage_tables'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating table: {e}")
            flash(f'Erreur lors de la création de la table: {str(e)}', 'danger')
            return redirect(url_for('tables.create_table'))
    
    return render_template('create_table.html', active_season=active_season)


def create_physical_table(table_name, columns):
    try:
        column_definitions = []
        for col in columns:
            col_type = get_mysql_type(col['type'])
            column_definitions.append(f"`{col['name']}` {col_type}")
        
        column_definitions.insert(0, "`id` INT AUTO_INCREMENT PRIMARY KEY")
        
        sql = text(f"CREATE TABLE IF NOT EXISTS `{table_name}` ({', '.join(column_definitions)})")
        
        db.session.execute(sql)
        db.session.commit()
        print(f"Table physique '{table_name}' créée avec succès")
    except Exception as e:
        print(f"Erreur création table physique: {e}")
        raise e

def get_mysql_type(python_type):
    type_mapping = {
        'string': 'VARCHAR(255)',
        'integer': 'INT',
        'float': 'FLOAT',
        'date': 'DATE',
        'boolean': 'BOOLEAN'
    }
    return type_mapping.get(python_type, 'VARCHAR(255)')

@tables_bp.route('/manage_tables')
@login_required
@permission_required('read_only')
def manage_tables():
    active_season = get_active_season()
    
    if not active_season:
        flash('Aucune saison active.', 'warning')
        tables = []
    else:
        # Récupérer uniquement les tables de la saison active
        tables = TableMetadata.query.filter_by(season_id=active_season.id).all()
    
    return render_template('manage_tables.html', tables=tables, active_season=active_season)

@tables_bp.route('/table_data/<table_name>')
@login_required
@permission_required('read_only')
def table_data(table_name):
    active_season = get_active_season()
    
    if not active_season:
        flash('Aucune saison active.', 'danger')
        return redirect(url_for('tables.manage_tables'))
    
    # Charger la table avec ses colonnes pour la saison active
    table = TableMetadata.query.options(
        joinedload(TableMetadata.columns)
    ).filter_by(
        name=table_name, 
        season_id=active_season.id
    ).first_or_404()
    
    # Récupérer les données de la table
    sql = text(f"SELECT * FROM `{table_name}`")
    result = db.session.execute(sql)
    columns = [col for col in result.keys()]
    data = [dict(zip(columns, row)) for row in result]
    
    return render_template('table_data.html', table=table, columns=columns, data=data)

@tables_bp.route('/add_row/<table_name>', methods=['POST'])
@login_required
@permission_required('read_write')
def add_row(table_name):
    active_season = get_active_season()
    table = TableMetadata.query.filter_by(
        name=table_name, 
        season_id=active_season.id
    ).first_or_404()
    
    try:
        columns = []
        placeholders = []
        params = {}
        
        for col in table.columns:
            field_value = request.form.get(col.name)
            if field_value is not None and field_value != '':
                columns.append(f"`{col.name}`")
                placeholders.append(f":{col.name}")
                params[col.name] = field_value
        
        if columns:
            sql = text(f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({', '.join(placeholders)})")
            db.session.execute(sql, params)
            db.session.commit()
            flash('Ligne ajoutée avec succès', 'success')
        else:
            flash('Aucune donnée à ajouter', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de l\'ajout de la ligne: {str(e)}', 'danger')
    
    return redirect(url_for('tables.table_data', table_name=table_name))


@tables_bp.route('/edit_row/<table_name>/<int:row_id>', methods=['POST'])
@login_required
@permission_required('read_write_edit')
def edit_row(table_name, row_id):
    active_season = get_active_season()
    table = TableMetadata.query.filter_by(
        name=table_name, 
        season_id=active_season.id
    ).first_or_404()
    
    updates = []
    params = {'row_id': row_id}
    
    for col in table.columns:
        if col.name in request.form:
            updates.append(f"`{col.name}` = :{col.name}")
            params[col.name] = request.form[col.name]
    
    if updates:
        sql = text(f"UPDATE `{table_name}` SET {', '.join(updates)} WHERE id = :row_id")
        db.session.execute(sql, params)
        db.session.commit()
        flash('Ligne modifiée avec succès', 'success')
    
    return redirect(url_for('tables.table_data', table_name=table_name))

@tables_bp.route('/delete_row/<table_name>/<int:row_id>')
@login_required
@permission_required('full')
def delete_row(table_name, row_id):
    sql = text(f"DELETE FROM `{table_name}` WHERE id = :row_id")
    db.session.execute(sql, {'row_id': row_id})
    db.session.commit()
    flash('Ligne supprimée avec succès', 'success')
    return redirect(url_for('tables.table_data', table_name=table_name))


@tables_bp.route('/delete_table/<int:table_id>', methods=['POST'])
@login_required
@permission_required('full')
def delete_table(table_id):
    try:
        table = TableMetadata.query.get_or_404(table_id)
        table_name = table.name
        
        # Supprimer d'abord la table physique
        sql = text(f"DROP TABLE IF EXISTS `{table_name}`")
        db.session.execute(sql)
        
        # Puis supprimer les métadonnées
        db.session.delete(table)
        db.session.commit()
        
        flash(f'Table "{table.display_name}" supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression de la table: {str(e)}', 'danger')
    
    return redirect(url_for('tables.manage_tables'))