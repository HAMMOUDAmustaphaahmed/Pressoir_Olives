from flask import Blueprint, render_template, make_response
from flask_login import login_required, current_user
from models import db, CompanySettings
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io
from main import permission_required
from sqlalchemy import text  # Ajout de l'import text
from datetime import datetime  # Ajout pour la date

pdf_bp = Blueprint('pdf', __name__)

@pdf_bp.route('/generate_invoice/<table_name>/<int:row_id>')
@login_required
@permission_required('read_only')
def generate_invoice(table_name, row_id):
    # Récupérer les données de la ligne avec text()
    sql = text(f"SELECT * FROM `{table_name}` WHERE id = :row_id")
    result = db.session.execute(sql, {'row_id': row_id})
    row_data = {col: val for col, val in zip(result.keys(), result.fetchone())}
    
    # Récupérer les paramètres de l'entreprise
    company_settings = CompanySettings.query.first()
    
    # Créer le PDF en mémoire
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # En-tête avec les informations de l'entreprise
    if company_settings:
        elements.append(Paragraph(company_settings.name, styles['Title']))
        elements.append(Paragraph(company_settings.address, styles['Normal']))
        elements.append(Paragraph(f"Tél: {company_settings.phone}", styles['Normal']))
        elements.append(Paragraph(f"Email: {company_settings.email}", styles['Normal']))
    
    elements.append(Spacer(1, 0.5*inch))
    
    # Titre de la facture
    elements.append(Paragraph("FACTURE", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Date actuelle
    current_date = datetime.now().strftime('%d/%m/%Y')
    elements.append(Paragraph(f"Date: {current_date}", styles['Normal']))
    elements.append(Spacer(1, 0.1*inch))
    
    # Informations du client
    client_info = []
    for key, value in row_data.items():
        if key not in ['id'] and value:
            client_info.append([key.replace('_', ' ').title(), str(value)])
    
    if client_info:
        client_table = Table(client_info, colWidths=[2*inch, 3*inch])
        client_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(client_table)
    
    # Construire le PDF
    doc.build(elements)
    
    # Préparer la réponse
    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=invoice_{table_name}_{row_id}.pdf'
    
    return response


@pdf_bp.route('/print_row/<table_name>/<int:row_id>')
@login_required
@permission_required('read_only')
def print_row(table_name, row_id):
    # Récupérer les métadonnées de la table
    from models import TableMetadata
    from sqlalchemy.orm import joinedload
    
    table = TableMetadata.query.options(joinedload(TableMetadata.columns)).filter_by(name=table_name).first_or_404()
    
    # Récupérer les données de la ligne
    sql = text(f"SELECT * FROM `{table_name}` WHERE id = :row_id")
    result = db.session.execute(sql, {'row_id': row_id})
    columns = [col for col in result.keys()]
    row_data = dict(zip(columns, result.fetchone()))
    company_settings = CompanySettings.query.first()
    return render_template('print_row.html', table=table, row=row_data,company_settings=company_settings)