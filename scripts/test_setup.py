#!/usr/bin/env python
"""
Test script to verify database connection and basic functionality
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def test_database_connection():
    """Test database connection"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models():
    """Test model imports and basic functionality"""
    try:
        from api.models import ImageUpload
        from users.models import CustomUser
        from feedback.models import DemographicProfile, UserStudySession
        
        print("✅ All models imported successfully!")
        
        # Test model creation (dry run)
        user_count = CustomUser.objects.count()
        print(f"✅ Users table accessible. Current count: {user_count}")
        
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def run_migrations():
    """Run database migrations"""
    try:
        print("Running database migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("DATABASE AND MODEL TESTING")
    print("=" * 60)
    
    # Test 1: Database connection
    print("\n1. Testing database connection...")
    db_ok = test_database_connection()
    
    if not db_ok:
        print("\n⚠️  Database connection failed. Trying to run migrations...")
        migration_ok = run_migrations()
        if migration_ok:
            db_ok = test_database_connection()
    
    # Test 2: Model functionality
    print("\n2. Testing models...")
    models_ok = test_models()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Database Connection: {'✅ PASS' if db_ok else '❌ FAIL'}")
    print(f"Model Functionality: {'✅ PASS' if models_ok else '❌ FAIL'}")
    
    if db_ok and models_ok:
        print("\n🎉 All tests passed! Your system is ready for development.")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        
        if not db_ok:
            print("\nDatabase troubleshooting:")
            print("1. Ensure MySQL is running")
            print("2. Check database credentials in .env file")
            print("3. Verify database 'skin_lesion_db' exists")
            
        if not models_ok:
            print("\nModel troubleshooting:")
            print("1. Run 'python manage.py makemigrations'")
            print("2. Run 'python manage.py migrate'")
            print("3. Check for syntax errors in model files")

if __name__ == "__main__":
    main()