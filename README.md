Django assessment and data exploration app — a lightweight backend project that demonstrates models, migrations, CSV data ingestion, and simple CRUD workflows.

Badges
Build: none yet

License: MIT

Python: 3.x

Django: 4.x

Overview
Spotter is a small Django web application intended for quick local development and demonstration of backend patterns: database modeling, data import from CSV, CRUD endpoints, and simple data analysis. The repository includes a sample CSV dataset and a SQLite database for fast testing.

Key Features
Django project structure with manage.py and app modules.

Persistent storage using SQLite for development.

CSV sample data included for import and exploration.

Ready to extend into REST APIs, authentication, or production databases.

Tech Stack
Language: Python

Framework: Django

Database: SQLite for development; easily switchable to PostgreSQL for production.

Data: CSV sample file for import and testing

Quick Start
Create and activate virtual environment
bash
python -m venv .venv
# macOS Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
Install dependencies
bash
pip install -r requirements.txt
Apply migrations
bash
python manage.py migrate
Load sample data
If a management command exists, run it. Example placeholder:

bash
python manage.py loaddata fuel-prices-for-be-assessment.csv
If no loader is provided, use the Django shell or a small script to parse the CSV and save rows to models.

Run development server
bash
python manage.py runserver
Open http://127.0.0.1:8000 to view the app.

Project Structure
manage.py — Django management entry point.

db.sqlite3 — development database included for convenience.

fuel-prices-for-be-assessment.csv — sample dataset for import and testing.

[app_name]/ — Django app modules: models, views, urls, migrations.

requirements.txt — Python dependencies.

Example API Documentation
The following examples assume you add a simple REST layer using Django REST Framework or Django views.

List resources
Endpoint: GET /api/items/

Response: JSON array of items with fields id, name, value, timestamp.

Retrieve single resource
Endpoint: GET /api/items/{id}/

Response: JSON object for the requested item.

Create resource
Endpoint: POST /api/items/

Body:

json
{
  "name": "Sample",
  "value": 123.45
}
Response: Created item with id.

Update resource
Endpoint: PUT /api/items/{id}/

Body: full resource JSON.

Response: Updated item.

Delete resource
Endpoint: DELETE /api/items/{id}/

Response: 204 No Content

Data Loader Example
Add a management command load_fuel_data under management/commands to import the CSV:

python
# management/commands/load_fuel_data.py
from django.core.management.base import BaseCommand
import csv
from app.models import FuelRecord

class Command(BaseCommand):
    help = "Load fuel prices from CSV"

    def handle(self, *args, **options):
        with open('fuel-prices-for-be-assessment.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                FuelRecord.objects.create(
                    date=row['date'],
                    region=row['region'],
                    price=float(row['price'])
                )
        self.stdout.write(self.style.SUCCESS('Data loaded'))
Run with:

bash
python manage.py load_fuel_data
