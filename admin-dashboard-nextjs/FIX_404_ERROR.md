# Fix 404 Error on Localhost:3010

## Issue
Getting a 404 error when accessing `http://localhost:3010`

## Root Cause
The `next.config.mjs` had `basePath` and `assetPrefix` set to `/admin`, which prefixes all routes. This means:
- Routes were accessible at `http://localhost:3010/admin/...` instead of `http://localhost:3010/...`
- The root route `/` was not accessible

## Solution Applied
Updated `next.config.mjs` to:
- Remove the default `/admin` basePath for local development
- Only use basePath when explicitly set via environment variable
- This allows local development to work normally while still supporting production deployment

## How to Fix

1. **Clear the Next.js cache** (already done):
   ```powershell
   Remove-Item -Recurse -Force .next
   ```

2. **Restart the dev server**:
   - Stop the current server (Ctrl+C in the terminal running it)
   - Start it again:
     ```powershell
     npm run dev
     ```

3. **Access the site**:
   - Home page: `http://localhost:3010`
   - Admin dashboard: `http://localhost:3010/admin`
   - Login: `http://localhost:3010/login`

## For Production Deployment

If you need the `/admin` basePath for production, set it via environment variable:
```env
NEXT_PUBLIC_BASE_PATH=/admin
NEXT_PUBLIC_ASSET_PREFIX=/admin
```

This way, local development works normally, but production can use the basePath when needed.

