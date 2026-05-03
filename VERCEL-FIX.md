# Vercel Deployment Fix

## Issue
Vercel serverless functions are crashing. This is common with Flask apps on Vercel.

## Quick Solution: Deploy as Static Site

Since we already have all the data (84 tools in JSON files), we can deploy as a static site and add the API later.

### Steps:

1. **Simplify vercel.json:**

```json
{
  "version": 2
}
```

2. **Create a simple static data loader:**

The index.html can load JSON files directly from the `/data/tools/` directory.

3. **Or use a different platform:**

### Alternative: Deploy to Render.com (Better for Flask)

1. Go to: https://render.com
2. Sign up with GitHub
3. New → Web Service
4. Connect repository: hardin-ai-search
5. Settings:
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api_contribution.py`
6. Deploy!

Render is better for Flask apps and has a free tier.

### Alternative: Deploy to Railway.app

1. Go to: https://railway.app
2. Sign up with GitHub
3. New Project → Deploy from GitHub
4. Select: hardin-ai-search
5. It auto-detects Python and deploys!

Railway is also great for Flask and has $5 free credit monthly.

### Alternative: Keep it Simple - Static Site

For now, just deploy the frontend as static and run the API locally or on a simple VPS.

The search can work client-side by loading all JSON files and filtering in JavaScript.
