from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Chart, TableMetadata, ColumnMetadata
from main import permission_required
from sqlalchemy import text
from sqlalchemy.orm import joinedload

charts_bp = Blueprint('charts', __name__)

@charts_bp.route('/add_chart', methods=['GET', 'POST'])
@login_required
@permission_required('read_write')
def add_chart():
    tables = TableMetadata.query.all()
    
        
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
            user_id=current_user.id
        )
        
        db.session.add(chart)
        db.session.commit()
        flash('Graphique créé avec succès', 'success')
        return redirect(url_for('charts.view_charts'))
    
    return render_template('add_chart.html', tables=tables)

@charts_bp.route('/view_charts')
@login_required
@permission_required('read_only')
def view_charts():
    charts = Chart.query.filter_by(user_id=current_user.id).all()
    return render_template('view_charts.html', charts=charts)

@charts_bp.route('/chart_data/<int:chart_id>')
@login_required
def chart_data(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    
    # Récupérer les données pour le graphique avec text()
    sql = text(f"SELECT `{chart.x_column}`, `{chart.y_column}` FROM `{chart.table_name}`")
    result = db.session.execute(sql)
    
    labels = []
    values = []
    
    for row in result:
        # Gérer les valeurs None pour les labels
        label_value = row[0] if row[0] is not None else "N/A"
        labels.append(str(label_value))
        
        # Convertir en float si possible, sinon utiliser l'index comme valeur
        try:
            if row[1] is not None:
                values.append(float(row[1]))
            else:
                values.append(0)
        except (ValueError, TypeError):
            # Si ce n'est pas un nombre, utiliser l'index comme valeur
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
    table = TableMetadata.query.options(joinedload(TableMetadata.columns)).filter_by(name=table_name).first()
    
    if not table:
        return jsonify([])
    
    columns = [{'name': col.name, 'display_name': col.display_name, 'type': col.type} for col in table.columns]
    return jsonify(columns)

@charts_bp.route('/edit_chart/<int:chart_id>', methods=['GET', 'POST'])
@login_required
@permission_required('read_write')
def edit_chart(chart_id):
    chart = Chart.query.get_or_404(chart_id)
    tables = TableMetadata.query.all()
    
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