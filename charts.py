from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Chart, TableMetadata, ColumnMetadata, Season
from main import permission_required
from sqlalchemy import text
from sqlalchemy.orm import joinedload

charts_bp = Blueprint('charts', __name__)

def get_active_season():
    """Récupère la saison active"""
    return Season.query.filter_by(is_active=True).first()

@charts_bp.route('/add_chart', methods=['GET', 'POST'])
@login_required
@permission_required('read_write')
def add_chart():
    active_season = get_active_season()
    
    if not active_season:
        flash('Aucune saison active. Veuillez activer une saison d\'abord.', 'danger')
        return redirect(url_for('seasons.manage_seasons'))
    
    # Récupérer uniquement les tables de la saison active
    tables = TableMetadata.query.filter_by(season_id=active_season.id).all()
    
    if request.method == 'POST':
        name = request.form.get('chart_name')
        table_name = request.form.get('table_name')
        x_column = request.form.get('x_column')
        y_column = request.form.get('y_column')
        chart_type = request.form.get('chart_type')
        
        chart = Chart(
            name=name,
            table_name=table_name,
            x_column=x_column,
            y_column=y_column,
            chart_type=chart_type,
            user_id=current_user.id,
            season_id=active_season.id  # Associer à la saison active
        )
        
        db.session.add(chart)
        db.session.commit()
        flash(f'Graphique créé avec succès dans la saison {active_season.name}', 'success')
        return redirect(url_for('charts.view_charts'))
    
    return render_template('add_chart.html', tables=tables, active_season=active_season)

@charts_bp.route('/view_charts')
@login_required
@permission_required('read_only')
def view_charts():
    active_season = get_active_season()
    
    if not active_season:
        flash('Aucune saison active.', 'warning')
        charts = []
    else:
        # Récupérer uniquement les graphiques de la saison active pour l'utilisateur actuel
        charts = Chart.query.filter_by(
            user_id=current_user.id,
            season_id=active_season.id
        ).all()
    
    return render_template('view_charts.html', charts=charts, active_season=active_season)

@charts_bp.route('/chart_data/<int:chart_id>')
@login_required
def chart_data(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    
    # Vérifier que le graphique appartient à l'utilisateur ou que l'utilisateur est admin
    if chart.user_id != current_user.id and current_user.access_level != 'full':
        return jsonify({'error': 'Accès non autorisé'}), 403
    
    # Récupérer les données pour le graphique
    sql = text(f"SELECT `{chart.x_column}`, `{chart.y_column}` FROM `{chart.table_name}`")
    result = db.session.execute(sql)
    
    labels = []
    values = []
    
    for row in result:
        label_value = row[0] if row[0] is not None else "N/A"
        labels.append(str(label_value))
        
        try:
            if row[1] is not None:
                values.append(float(row[1]))
            else:
                values.append(0)
        except (ValueError, TypeError):
            values.append(len(values) + 1)
    
    return jsonify({
        'labels': labels,
        'values': values,
        'chart_type': chart.chart_type,
        'chart_name': chart.name
    })

@charts_bp.route('/get_table_columns/<table_name>')
@login_required
def get_table_columns(table_name):
    active_season = get_active_season()
    
    if not active_season:
        return jsonify([])
    
    # Récupérer la table de la saison active
    table = TableMetadata.query.options(
        joinedload(TableMetadata.columns)
    ).filter_by(
        name=table_name,
        season_id=active_season.id
    ).first()
    
    if not table:
        return jsonify([])
    
    columns = [
        {
            'name': col.name, 
            'display_name': col.display_name, 
            'type': col.type
        } 
        for col in table.columns
    ]
    return jsonify(columns)

@charts_bp.route('/edit_chart/<int:chart_id>', methods=['GET', 'POST'])
@login_required
@permission_required('read_write')
def edit_chart(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    active_season = get_active_season()
    
    # Vérifier que le graphique appartient à l'utilisateur
    if chart.user_id != current_user.id and current_user.access_level != 'full':
        flash('Vous ne pouvez pas modifier ce graphique', 'danger')
        return redirect(url_for('charts.view_charts'))
    
    tables = TableMetadata.query.filter_by(season_id=active_season.id).all()
    
    if request.method == 'POST':
        chart.name = request.form.get('chart_name')
        chart.x_column = request.form.get('x_column')
        chart.y_column = request.form.get('y_column')
        chart.chart_type = request.form.get('chart_type')
        
        db.session.commit()
        flash('Graphique modifié avec succès', 'success')
        return redirect(url_for('charts.view_charts'))
    
    return render_template('edit_chart.html', chart=chart, tables=tables)

@charts_bp.route('/delete_chart/<int:chart_id>')
@login_required
@permission_required('read_write')
def delete_chart(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    
    # Vérifier que l'utilisateur peut supprimer ce graphique
    if chart.user_id != current_user.id and current_user.access_level != 'full':
        flash('Vous ne pouvez pas supprimer ce graphique', 'danger')
        return redirect(url_for('charts.view_charts'))
    
    db.session.delete(chart)
    db.session.commit()
    flash('Graphique supprimé avec succès', 'success')
    return redirect(url_for('charts.view_charts'))