# Debugging 500 Error on Vercel

## Critical Fix Applied

✅ **Fixed vercel.json** - Changed from `wsgi.py` to `api/index.py` handler

## How to Debug the 500 Error

### Step 1: Check Vercel Logs

1. Go to your Vercel Dashboard
2. Select your project
3. Go to **Deployments** tab
4. Click on the latest deployment
5. Click **Functions** tab or **View Function Logs**
6. Look for error messages

OR visit: `https://your-app.vercel.app/_logs`

### Step 2: Check Environment Variables

In Vercel Dashboard → Settings → Environment Variables, ensure you have:

```
ALLOWED_HOSTS = your-app-name.vercel.app,*.vercel.app
DEBUG = False
SECRET_KEY = [your-secret-key]
```

**To get your app name:**
- Look at your Vercel deployment URL
- Example: `grace-bites-abc123.vercel.app`
- Use: `grace-bites-abc123.vercel.app,*.vercel.app`

### Step 3: Common Error Patterns

#### Error: "DisallowedHost" or "Invalid HTTP_HOST header"
**Fix:** Set `ALLOWED_HOSTS` environment variable in Vercel

#### Error: "No module named 'whitenoise'"
**Fix:** Check `requirements.txt` has `whitenoise>=6.0.0`

#### Error: "No module named 'dj_database_url'"
**Fix:** Check `requirements.txt` has `dj-database-url>=2.0.0`

#### Error: "Database connection failed"
**Fix:** 
- SQLite won't work on Vercel
- You need PostgreSQL (see database setup below)
- Or temporarily disable database features

#### Error: "ImportError" or "ModuleNotFoundError"
**Fix:** 
- Check all dependencies in `requirements.txt`
- Make sure all your apps are listed in `INSTALLED_APPS`

### Step 4: Test Locally First

Before deploying, test the handler locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Test Django setup
python manage.py check

# Test static files
python manage.py collectstatic --noinput

# Run local server
python manage.py runserver
```

### Step 5: Minimal Test

Create a simple test to see if the handler works:

1. The handler now logs request information
2. Check Vercel function logs to see what's being received
3. Look for the error message in the logs

## Quick Fixes to Try

### Fix 1: Set ALLOWED_HOSTS (Most Common Issue)

In Vercel Dashboard:
1. Go to Settings → Environment Variables
2. Add: `ALLOWED_HOSTS` = `your-actual-app-name.vercel.app,*.vercel.app`
3. Redeploy

### Fix 2: Temporarily Disable Database

If database is causing issues, you can temporarily make it optional:

The settings.py already handles this - if no DB env vars are set, it uses SQLite (which will fail on Vercel but at least the app will start).

### Fix 3: Check Import Errors

Make sure all these are in `requirements.txt`:
```
Django~=4.2
whitenoise>=6.0.0
dj-database-url>=2.0.0
psycopg2-binary>=2.9.0
```

### Fix 4: Verify Handler Function

The handler function in `api/index.py` should be named `handler` (it is).

## What Changed

1. **vercel.json**: Now correctly points to `api/index.py` instead of `wsgi.py`
2. **Handler function**: Improved error handling and logging
3. **Request format**: Better handling of Vercel's request format

## Next Steps

1. **Redeploy** after fixing vercel.json
2. **Check logs** immediately after deployment
3. **Set environment variables** if not already set
4. **Share the error** from logs if still failing

## Getting Help

If you're still getting 500 errors:

1. Copy the exact error message from Vercel logs
2. Check which line is failing
3. Share:
   - The error message
   - The stack trace
   - Your environment variables (without sensitive values)

The handler now includes better error messages that will show in the response body, so you can see what's failing directly in the browser.

