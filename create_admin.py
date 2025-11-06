#!/usr/bin/env python
"""
Django management command to create a superuser automatically
"""
import os
import sys
import django
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

def create_superuser():
    """Create a superuser if it doesn't exist"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()
    
    User = get_user_model()
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print("Superuser already exists!")
        return
    
    # Create superuser with default credentials
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL', 'admin@skinlesion.com')
    password = os.environ.get('ADMIN_PASSWORD', 'AdminPass123!')
    
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    user.is_staff = True
    user.is_superuser = True
    user.save()
    
    print(f"Superuser '{username}' created successfully!")
    print(f"Email: {email}")
    print("Password: AdminPass123!")
    print("\n⚠️  IMPORTANT: Change the password after first login!")

if __name__ == "__main__":
    create_superuser()