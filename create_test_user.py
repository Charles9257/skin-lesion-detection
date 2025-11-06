#!/usr/bin/env python
"""
Quick user creation script for testing dashboard login
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_test_user():
    User = get_user_model()
    
    # Create test user
    username = 'demo'
    email = 'demo@example.com'
    password = 'demo123456'
    
    if User.objects.filter(username=username).exists():
        print(f"✅ User '{username}' already exists")
        user = User.objects.get(username=username)
    else:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Demo',
            last_name='User'
        )
        print(f"✅ Created new user: {username}")
    
    print(f"📧 Email: {user.email}")
    print(f"🔑 Password: {password}")
    print(f"🌐 Login URL: http://127.0.0.1:8001/users/auth/")
    print(f"📊 Dashboard URL: http://127.0.0.1:8001/users/dashboard/")
    
    # Create admin user if needed
    admin_username = 'admin'
    if not User.objects.filter(username=admin_username).exists():
        admin = User.objects.create_superuser(
            username=admin_username,
            email='admin@example.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"✅ Created admin user: {admin_username}")
        print(f"🔐 Admin password: admin123")
        print(f"⚙️ Admin URL: http://127.0.0.1:8001/admin/")
    else:
        print(f"✅ Admin user '{admin_username}' already exists")

if __name__ == '__main__':
    create_test_user()