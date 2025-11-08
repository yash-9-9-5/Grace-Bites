# Vercel Deployment Guide for Grace Bites Django Application

## Important Considerations

### ⚠️ Critical Issues with Current Setup

1. **SQLite Database**: Your app uses SQLite (`db.sqlite3`), which is a file-based database. This **WILL NOT WORK** on Vercel because:
   - Vercel serverless functions are stateless
   - Each function invocation may run on a different container
   - File system changes are not persisted between invocations
   - SQLite requires a persistent file system

2. **Media Files**: Your `media/` folder contains user uploads. These need to be stored in:
   - AWS S3
   - Cloudinary
   - Vercel Blob Storage
   - Or another cloud storage service

3. **Static Files**: Need to be properly configured for production

## Required Changes Before Deployment

### 1. Update Settings for Production

You'll need to update `grace_bites_project/settings.py`:

```python
import os

# Production settings
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Use PostgreSQL instead of SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files for Vercel
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'
```

### 2. Set Environment Variables in Vercel

In your Vercel dashboard, add these environment variables:
- `SECRET_KEY`: Your Django secret key
- `DEBUG`: `False` for production
- `ALLOWED_HOSTS`: Your Vercel domain (e.g., `your-app.vercel.app`)
- Database credentials (if using external DB)

### 3. Database Options

**Option A: Vercel Postgres** (Recommended)
- Add Vercel Postgres addon
- Use connection string from environment variables

**Option B: External Database**
- Use services like:
  - Supabase (free tier available)
  - Railway PostgreSQL
  - AWS RDS
  - Neon (serverless Postgres)

### 4. Media Storage

Configure Django to use cloud storage:

```python
# Install: pip install django-storages boto3
INSTALLED_APPS = [
    # ... existing apps
    'storages',
]

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
```

## Deployment Steps

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **For production**:
   ```bash
   vercel --prod
   ```

## Alternative: Better Platforms for Django

Consider these alternatives that are better suited for Django:

1. **Railway** - Easy Django deployment, includes PostgreSQL
2. **Render** - Free tier, good Django support
3. **Fly.io** - Docker-based, great for Django
4. **Heroku** - Classic choice (paid now)
5. **DigitalOcean App Platform** - Simple deployment

These platforms handle Django's requirements (database, file storage, static files) much better than Vercel.

