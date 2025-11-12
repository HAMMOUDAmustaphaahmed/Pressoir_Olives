from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Season(db.Model):
    """Modèle pour gérer les saisons de production"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)  # Ex: "2024-2025"
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=False)  # Une seule saison active à la fois
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    tables = db.relationship('TableMetadata', backref='season', lazy=True, cascade="all, delete-orphan")
    charts = db.relationship('Chart', backref='season', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Season {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    access_level = db.Column(db.String(50), default='read_only')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class TableMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)
    
    columns = db.relationship('ColumnMetadata', backref='table', lazy=True, cascade="all, delete-orphan")
    
    # Contrainte unique : nom de table unique par saison
    __table_args__ = (db.UniqueConstraint('name', 'season_id', name='unique_table_per_season'),)

class ColumnMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('table_metadata.id'), nullable=False)

class Chart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(100), nullable=False)
    x_column = db.Column(db.String(100), nullable=False)
    y_column = db.Column(db.String(100), nullable=False)
    chart_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'), nullable=False)

class CompanySettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    logo = db.Column(db.String(300), nullable=True)