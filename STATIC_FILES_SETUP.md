# Static Files Setup for Vercel

## What Was Fixed

✅ **BASE_DIR** - Already correctly defined (line 17)
✅ **STATIC_ROOT** - Added: `BASE_DIR / 'staticfiles'` (required for collectstatic)
✅ **WhiteNoise** - Added to INSTALLED_APPS and MIDDLEWARE (serves static files on Vercel)
✅ **dj-database-url** - Added support for DATABASE_URL environment variable
✅ **ALLOWED_HOSTS** - Improved handling of empty environment variables

## How Static Files Work on Vercel

### Development (Local)
- Django serves static files from `STATICFILES_DIRS` (your `static/` folder)
- WhiteNoise is active but uses development mode

### Production (Vercel)
- Run `collectstatic` to gather all static files into `STATIC_ROOT` (staticfiles/)
- WhiteNoise serves files from `STATIC_ROOT` directly
- Files are compressed and cached for better performance

## Deployment Steps

### 1. Before Deploying to Vercel

Run collectstatic locally (optional, Vercel can do this):
```bash
python manage.py collectstatic --noinput
```

### 2. Vercel Build Command (Optional)

If you want Vercel to run collectstatic during build, add to `vercel.json`:
```json
{
  "buildCommand": "python manage.py collectstatic --noinput"
}
```

However, WhiteNoise will handle this automatically, so it's usually not needed.

### 3. Verify Static Files

After deployment:
- Visit: `https://your-app.vercel.app/static/css/style.css`
- Should load your CSS file
- If 404, check that `STATIC_ROOT` exists and has files

## Troubleshooting

### Static files return 404
1. Check `STATIC_ROOT` is set correctly
2. Verify WhiteNoise middleware is in the right position (after SecurityMiddleware)
3. Check that `collectstatic` has been run
4. Verify `STATIC_URL = '/static/'` (with leading slash)

### WhiteNoise not working
1. Check middleware order (must be after SecurityMiddleware)
2. Verify `whitenoise` is in `INSTALLED_APPS`
3. Check `STATICFILES_STORAGE` is set correctly
4. Ensure `STATIC_ROOT` exists

### Database connection issues
- If using Vercel Postgres, set `DATABASE_URL` environment variable
- Or set individual `DB_NAME`, `DB_USER`, `DB_PASSWORD`, etc.
- `dj-database-url` will automatically parse `DATABASE_URL`

## Files Changed

1. **settings.py**:
   - Added WhiteNoise to INSTALLED_APPS
   - Added WhiteNoise middleware
   - Added STATIC_ROOT
   - Added STATICFILES_STORAGE
   - Added dj-database-url support
   - Improved ALLOWED_HOSTS handling

2. **requirements.txt**:
   - Added `whitenoise>=6.0.0`
   - Added `dj-database-url>=2.0.0`
   - Added `psycopg2-binary>=2.9.0` (for PostgreSQL)

## Next Steps

1. **Install dependencies locally**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test locally**:
   ```bash
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```

3. **Deploy to Vercel**:
   - Push changes to GitHub
   - Vercel will automatically install dependencies
   - Static files will be served by WhiteNoise

4. **Set environment variables in Vercel**:
   - `ALLOWED_HOSTS`: your-app.vercel.app,*.vercel.app
   - `DEBUG`: False
   - `SECRET_KEY`: [generate new one]
   - `DATABASE_URL`: [if using Vercel Postgres]

