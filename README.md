# 🫒 Pressoir à Olives - Système de Gestion

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange)](https://mysql.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple)](https://getbootstrap.com)

Un système de gestion complet développé avec Flask pour la gestion des dépôts d'olives, production d'huile, et suivi des clients pour les pressoirs d'olives.

## ✨ Fonctionnalités

### 📊 Gestion des Données
- **Création dynamique de tables** avec interface intuitive
- **Gestion des colonnes** (types: string, integer, float, date, boolean)
- **Recherche en temps réel** avec filtre AJAX
- **Édition et suppression** des données avec permissions
- **Import/Export** des données (optionnel)

### 📈 Tableaux de Bord et Graphiques
- **Dashboard interactif** avec statistiques
- **Création de graphiques** (barres, lignes, camemberts, anneaux)
- **Visualisation des données** avec Chart.js
- **Personnalisation** des axes et types de graphiques

### 👥 Gestion des Utilisateurs
- **Système d'authentification** sécurisé
- **Niveaux d'accès** (read_only, read_write, read_write_edit, full)
- **Interface d'administration** pour la gestion des utilisateurs

### 🏢 Gestion Commerciale
- **Suivi des dépôts d'olives** par client
- **Calcul automatique** des quantités et montants
- **Gestion des dates** de dépôt et livraison
- **Suivi des paiements** (payé/reste à payer)

### 🖨️ Fonctionnalités d'Impression
- **Impression des fiches clients** avec mise en page optimisée
- **Informations de l'entreprise** personnalisables
- **Format PDF** généré dynamiquement

## 🛠️ Technologies Utilisées

### Backend
- **Flask** - Framework web Python
- **Flask-Login** - Gestion de l'authentification
- **Flask-SQLAlchemy** - ORM pour la base de données
- **MySQL Connector** - Connexion à MySQL
- **ReportLab** - Génération de PDF

### Frontend
- **Bootstrap 5.3** - Framework CSS
- **jQuery** - Manipulation DOM et AJAX
- **DataTables** - Tables interactives
- **Chart.js** - Création de graphiques
- **Select2** - Sélecteurs avancés
- **Font Awesome** - Icônes

### Base de Données
- **MySQL** - Base de données relationnelle
- **Modèles relationnels** pour tables dynamiques

## 🚀 Installation

### Prérequis
- Python 3.8+
- MySQL 8.0+
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner le repository**
```bash
git clone https://github.com/HAMMOUDAmustaphaahmed/pressoir-olives.git
cd pressoir-olives