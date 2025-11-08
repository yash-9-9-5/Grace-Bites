# Vercel Environment Variables Setup

## ⚠️ CRITICAL: Set These Environment Variables in Vercel

Go to your Vercel Dashboard → Your Project → Settings → Environment Variables

### Required for Basic Deployment:

1. **ALLOWED_HOSTS** (CRITICAL - Without this, you'll get 500 errors!)
   ```
   Value: your-app-name.vercel.app,*.vercel.app
   ```
   Replace `your-app-name` with your actual Vercel app name.

2. **SECRET_KEY** (Security - Generate a new one!)
   ```bash
   # Generate a new secret key (run locally):
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Copy the output and set it as `SECRET_KEY` in Vercel.

3. **DEBUG** (Set to False for production)
   ```
   Value: False
   ```

### Optional (But Recommended):

4. **CSRF_TRUSTED_ORIGINS**
   ```
   Value: https://your-app-name.vercel.app
   ```

5. **CSRF_COOKIE_SECURE**
   ```
   Value: True
   ```

### For Database (PostgreSQL - Required for Production):

If you're using PostgreSQL (which you should on Vercel):

6. **DB_NAME**
   ```
   Value: [Your database name]
   ```

7. **DB_USER**
   ```
   Value: [Your database user]
   ```

8. **DB_PASSWORD**
   ```
   Value: [Your database password]
   ```

9. **DB_HOST**
   ```
   Value: [Your database host]
   ```

10. **DB_PORT**
    ```
    Value: 5432
    ```

## Quick Setup Steps:

1. **Get your Vercel domain:**
   - Deploy your app (even if it fails)
   - Check the deployment URL (e.g., `grace-bites-abc123.vercel.app`)

2. **Set environment variables:**
   - Go to Vercel Dashboard
   - Select your project
   - Go to Settings → Environment Variables
   - Add each variable above

3. **Redeploy:**
   - After setting variables, trigger a new deployment
   - Or push a new commit to trigger auto-deployment

## Testing:

After setting environment variables, visit:
- `https://your-app.vercel.app/` - Should load your homepage
- `https://your-app.vercel.app/_logs` - View function logs for errors

## Common Issues:

### Still getting 500 error?
1. Check `ALLOWED_HOSTS` is set correctly
2. Check Vercel logs: `https://your-app.vercel.app/_logs`
3. Verify environment variables are set (not just in code)
4. Make sure you redeployed after setting variables

### Database errors?
- SQLite won't work on Vercel
- You need PostgreSQL (see database setup in DEPLOYMENT_GUIDE.md)

### Import errors?
- Check `requirements.txt` has all dependencies
- Make sure `psycopg2-binary` is added if using PostgreSQL

