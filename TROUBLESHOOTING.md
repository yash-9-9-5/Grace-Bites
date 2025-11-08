# Troubleshooting FUNCTION_INVOCATION_FAILED on Vercel

## Quick Diagnostic Steps

### 1. Check Vercel Logs
```bash
# View logs in Vercel dashboard or CLI
vercel logs [deployment-url]
```

Or visit: `https://your-app.vercel.app/_logs`

### 2. Common Error Patterns

#### Error: "Django initialization failed"
**Cause**: Django can't start, usually due to:
- Missing environment variables
- Database connection failure (SQLite won't work!)
- Import errors in settings.py
- Missing dependencies

**Fix**: 
- Check all environment variables are set in Vercel dashboard
- Switch from SQLite to PostgreSQL
- Verify all imports in settings.py work

#### Error: "No module named 'X'"
**Cause**: Missing dependency in requirements.txt

**Fix**: Add missing package to `requirements.txt` and redeploy

#### Error: "Database connection failed"
**Cause**: SQLite database doesn't exist or can't be accessed

**Fix**: 
- **CRITICAL**: SQLite will NOT work on Vercel
- Use PostgreSQL (Vercel Postgres, Supabase, Railway, etc.)
- Update DATABASES setting in settings.py

#### Error: "ALLOWED_HOSTS" or "DisallowedHost"
**Cause**: Vercel domain not in ALLOWED_HOSTS

**Fix**: Add your Vercel domain to ALLOWED_HOSTS:
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
# Set in Vercel: ALLOWED_HOSTS=your-app.vercel.app,*.vercel.app
```

## Testing Locally

Test the serverless function locally:

```bash
# Install Vercel CLI
npm i -g vercel

# Run local dev server
vercel dev
```

This will help catch errors before deployment.

## Environment Variables Checklist

Set these in Vercel Dashboard → Settings → Environment Variables:

- `SECRET_KEY`: Django secret key (generate new one for production!)
- `DEBUG`: `False` (never `True` in production)
- `ALLOWED_HOSTS`: `your-app.vercel.app,*.vercel.app`
- `DJANGO_SETTINGS_MODULE`: `grace_bites_project.settings` (if needed)
- Database credentials (if using external DB):
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_HOST`
  - `DB_PORT`

## Database Migration Steps

Since SQLite won't work, you need PostgreSQL:

1. **Create PostgreSQL database** (choose one):
   - Vercel Postgres (addon)
   - Supabase (free tier)
   - Railway PostgreSQL
   - Neon (serverless Postgres)

2. **Update settings.py**:
```python
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
```

3. **Update requirements.txt**:
```
Django~=4.2
psycopg2-binary~=2.9
```

4. **Run migrations** (on Vercel, this happens automatically if you add a build command)

## Debugging Tips

1. **Enable detailed error messages** (temporarily):
```python
# In settings.py
DEBUG = True  # Only for debugging, remove after!
```

2. **Add logging**:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

3. **Check function logs** in Vercel dashboard for specific error messages

4. **Test incrementally**: Start with a simple "Hello World" view to verify the function works, then add complexity

