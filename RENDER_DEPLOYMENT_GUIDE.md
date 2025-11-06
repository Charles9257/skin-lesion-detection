# 🚀 Render Deployment Guide

## Overview
Your skin lesion detection Django application is now configured for deployment on Render. Follow these steps to deploy your application.

## Prerequisites
- GitHub repository: `Charles9257/skin-lesion-detection` ✅
- Render account (sign up at [render.com](https://render.com))

## Deployment Steps

### 1. Connect GitHub to Render
1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" and select "Web Service"
3. Connect your GitHub account and select `Charles9257/skin-lesion-detection`
4. Choose the `main` branch

### 2. Configure Web Service
Render should automatically detect your configuration from `render.yaml`, but verify these settings:

- **Name**: `skin-lesion-detection`
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn backend.wsgi:application`
- **Plan**: `Free`

### 3. Environment Variables
Render will automatically create these from your `render.yaml`:
- `DJANGO_SECRET_KEY` (auto-generated)
- `DATABASE_URL` (from PostgreSQL database)
- `DEBUG=False`
- `ALLOWED_HOSTS=*`
- `PYTHON_VERSION=3.11.0`

### 4. Database Setup
Render will automatically create a PostgreSQL database and connect it via `DATABASE_URL`.

### 5. Deploy
1. Click "Create Web Service"
2. Render will:
   - Clone your repository
   - Run `build.sh` to install dependencies
   - Run database migrations
   - Collect static files
   - Start your Django application

## Post-Deployment

### 1. Create Superuser
Once deployed, you'll need to create an admin user:
1. Go to your Render dashboard
2. Find your web service and click on it
3. Go to the "Shell" tab
4. Run: `python manage.py createsuperuser`
5. Follow the prompts to create your admin account

### 2. Test Your Application
- Visit your Render app URL (e.g., `https://skin-lesion-detection.onrender.com`)
- Test the API endpoints
- Access the admin panel at `/admin/`

### 3. Upload AI Model
Your AI model files need to be available for predictions:
1. Use the Django admin to upload any required model files
2. Or include them in your git repository (if not too large)

## Configuration Files Created

### `render.yaml`
- Defines the web service configuration
- Sets up PostgreSQL database
- Configures environment variables

### `build.sh`
- Installs Python dependencies
- Runs database migrations
- Collects static files

### `Procfile`
- Specifies the command to start your web server

### Updated `requirements.txt`
- Added `dj-database-url` for PostgreSQL support
- Added `psycopg2-binary` for PostgreSQL driver
- Added `whitenoise` for static file serving

### Updated Django Settings
- Database configuration with `DATABASE_URL` support
- Whitenoise middleware for static files
- Production-ready configuration

## Troubleshooting

### Common Issues:
1. **Build Fails**: Check the build logs in Render dashboard
2. **Database Connection**: Ensure `DATABASE_URL` is set correctly
3. **Static Files**: Whitenoise should handle this automatically
4. **Model Loading**: Ensure AI model files are accessible

### Useful Commands (via Render Shell):
```bash
# Check database status
python manage.py dbshell

# Run migrations manually
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

## Next Steps
1. Deploy to Render using the steps above
2. Test all functionality
3. Set up monitoring and logging
4. Consider setting up a custom domain
5. Configure backup strategies for your database

## Support
- Render Documentation: [docs.render.com](https://docs.render.com)
- Django Deployment Guide: [docs.djangoproject.com](https://docs.djangoproject.com/en/stable/howto/deployment/)

Your application is ready for deployment! 🎉