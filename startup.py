#!/usr/bin/env python
"""
Routarr startup script
Handles database initialization, migrations, and superuser creation
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'routarr.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from django.db import connection


def run_migrations():
    """Run Django migrations"""
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        sys.exit(1)


def create_superuser():
    """Create superuser if it doesn't exist"""
    print("👤 Checking for superuser...")
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'password')
            print("✅ Superuser 'admin' created successfully")
        else:
            print("ℹ️  Superuser 'admin' already exists")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        # Don't exit here, as the app can still run without superuser


def check_database():
    """Check if database is accessible"""
    print("🔍 Checking database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def main():
    """Main startup function"""
    print("🚀 Starting Routarr...")
    
    # Check database connection
    check_database()
    
    # Run migrations
    run_migrations()
    
    # Create superuser
    create_superuser()
    
    print("🎉 Startup completed successfully!")
    print("🌐 Starting Django development server...")
    
    # Start Django development server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == '__main__':
    main() 