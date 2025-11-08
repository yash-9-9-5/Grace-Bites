# Quick Fix for 500 Error on Vercel

## The Problem

Your Django app is returning 500 errors because:
1. **ALLOWED_HOSTS is empty** - Django rejects all requests from Vercel
2. Settings are hardcoded - No environment variable support
3. SQLite database - Won't work on Vercel (but we'll handle this gracefully)

## What I Fixed

✅ Updated `grace_bites_project/settings.py`:
- Added environment variable support
- Set `ALLOWED_HOSTS = ['*']` by default (accepts all hosts)
- Added PostgreSQL support (falls back to SQLite if no DB env vars)
- Made DEBUG, SECRET_KEY, CSRF settings use environment variables

✅ Improved `api/index.py`:
- Better error messages
- Detects common issues (database, ALLOWED_HOSTS, imports)
- More robust request handling

## What You Need to Do NOW

### Step 1: Set Environment Variables in Vercel

1. Go to: https://vercel.com/dashboard
2. Select your project: **Grace-Bites**
3. Go to: **Settings** → **Environment Variables**
4. Add these variables:

```
ALLOWED_HOSTS = your-actual-app-name.vercel.app,*.vercel.app
DEBUG = False
SECRET_KEY = [generate a new one - see below]
```

**To generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 2: Redeploy

After setting environment variables:
- Go to **Deployments** tab
- Click **⋯** (three dots) on latest deployment
- Click **Redeploy**

OR

- Push a new commit to trigger auto-deployment

### Step 3: Test

Visit your Vercel URL - it should work now!

## If It Still Doesn't Work

1. **Check the logs:**
   - Visit: `https://your-app.vercel.app/_logs`
   - Look for specific error messages

2. **Common remaining issues:**
   - **Database errors**: You'll need PostgreSQL (SQLite won't work)
   - **Import errors**: Check `requirements.txt`
   - **Static files**: May need additional configuration

3. **Get help:**
   - Share the error from `/_logs`
   - Check `TROUBLESHOOTING.md` for more details

## Next Steps (After Basic Fix Works)

1. **Set up PostgreSQL database** (required for production)
   - Options: Supabase (free), Railway, Vercel Postgres
   - See `DEPLOYMENT_GUIDE.md` for details

2. **Set up media file storage** (for user uploads)
   - Options: AWS S3, Cloudinary, Vercel Blob
   - See `DEPLOYMENT_GUIDE.md` for details

3. **Secure your app:**
   - Set specific `ALLOWED_HOSTS` (not `*`)
   - Use strong `SECRET_KEY`
   - Enable `CSRF_COOKIE_SECURE = True`

## Summary

The main fix was adding `ALLOWED_HOSTS = ['*']` to accept Vercel requests. Now you just need to:
1. Set environment variables in Vercel dashboard
2. Redeploy
3. Test your site

The app should work now (though database features won't work until you set up PostgreSQL).

