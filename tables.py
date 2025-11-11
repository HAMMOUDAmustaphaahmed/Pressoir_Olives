from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, TableMetadata, ColumnMetadata
from main import permission_required
import json
from sqlalchemy import text 
from sqlalchemy.orm import joinedload

tables_bp = Blueprint('tables', __name__)

@tables_bp.route('/create_table', methods=['GET', 'POST'])
@login_required
@permission_required('full')
def create_table():
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
        
        # Vérifier si la table existe déjà
        if TableMetadata.query.filter_by(name=table_name).first():
            flash('Une table avec ce nom existe déjà', 'danger')
            return redirect(url_for('tables.create_table'))
        
        try:
            # Créer la table dans la base de données
            table = TableMetadata(name=table_name, display_name=display_name)
            db.session.add(table)
            db.session.flush()  # Pour obtenir l'ID sans commit
            
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
            
            flash(f'Table "{display_name}" créée avec succès', 'success')
            return redirect(url_for('tables.manage_tables'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error creating table: {e}")  # Debug
            flash(f'Erreur lors de la création de la table: {str(e)}', 'danger')
            return redirect(url_for('tables.create_table'))
    
    return render_template('create_table.html')


def create_physical_table(table_name, columns):
    try:
        # Cette fonction crée la table physique dans MySQL
        column_definitions = []
        for col in columns:
            col_type = get_mysql_type(col['type'])
            column_definitions.append(f"`{col['name']}` {col_type}")
        
        # Ajouter l'ID comme clé primaire
        column_definitions.insert(0, "`id` INT AUTO_INCREMENT PRIMARY KEY")
        
        # Créer la requête SQL avec text()
        sql = text(f"CREATE TABLE `{table_name}` ({', '.join(column_definitions)})")
        
        # Exécuter la requête avec db.session.execute()
        db.session.execute(sql)
        db.session.commit()
        print(f"Table physique '{table_name}' créée avec succès")  # Debug
    except Exception as e:
        print(f"Erreur création table physique: {e}")  # Debug
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
    tables = TableMetadata.query.all()
    return render_template('manage_tables.html', tables=tables)

@tables_bp.route('/table_data/<table_name>')
@login_required
@permission_required('read_only')
def table_data(table_name):
    # Charger la table avec ses colonnes en utilisant joinedload pour éviter le problème N+1
    from sqlalchemy.orm import joinedload
    table = TableMetadata.query.options(joinedload(TableMetadata.columns)).filter_by(name=table_name).first_or_404()
    
    
    # Récupérer les données de la table
    sql = text(f"SELECT * FROM `{table_name}`")
    result = db.session.execute(sql)
    columns = [col for col in result.keys()]
    data = [dict(zip(columns, row)) for row in result]
    
    # Debug: afficher les colonnes de la table physique
    
    return render_template('table_data.html', table=table, columns=columns, data=data)
@tables_bp.route('/add_row/<table_name>', methods=['POST'])
@login_required
@permission_required('read_write')
def add_row(table_name):
    table = TableMetadata.query.filter_by(name=table_name).first_or_404()
    
    try:
        # Construire la requête d'insertion avec tous les champs
        columns = []
        placeholders = []
        params = {}
        
        for col in table.columns:
            field_value = request.form.get(col.name)
            # Si c'est un champ vide, on peut choisir de l'ignorer ou de mettre NULL
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
    table = TableMetadata.query.filter_by(name=table_name).first_or_404()
    
    # Construire la requête de mise à jour
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