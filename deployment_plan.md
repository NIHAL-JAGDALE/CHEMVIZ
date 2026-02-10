# Deployment Implementation Plan

This plan outlines the steps to deploy the **Chemical Equipment Parameter Visualizer** live. We will use **Render** for the Django backend and **Vercel** for the React frontend, as they offer excellent free tiers and easy integration.

## 🛠️ Step 1: Backend Preparation (Django)

We need to make the backend "Production Ready" by handling environment variables, static files, and database transitions.

### 1.1 Update Dependencies
Add production-specific packages to `backend/requirements.txt`:
- `gunicorn`: A production-level HTTP server.
- `whitenoise`: To serve static files (CSS/JS/Images) in production.
- `dj-database-url`: To easily connect to a PostgreSQL database on Render.
- `python-dotenv`: To manage environment variables.
- `pysqlite3-binary`: Often required on some platforms if the system SQLite is outdated (or just use PostgreSQL).

### 1.2 Modify `settings.py`
- Use `python-dotenv` to load a `.env` file.
- Replace `SECRET_KEY` with an environment variable.
- Set `DEBUG = False` based on environment.
- Add production URLs to `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`.
- Configure `dj-database-url` for the database connection.
- Set up `WhiteNoise` in `MIDDLEWARE`.

### 1.3 Create `Procfile`
Create a `Procfile` in the `backend/` directory to tell Render how to run the server:
```
web: gunicorn equipment_api.wsgi:application
```

## 🌐 Step 2: Frontend Preparation (React)

### 2.1 Environment Variables
Modify `web-frontend/src/services/api.js` to use an environment variable for the backend URL:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

### 2.2 SPA Routing Fix
Vercel/Netlify need a configuration to redirect all traffic to `index.html` for React Router to work. Create `web-frontend/public/_redirects` or `vercel.json`.

## 🚀 Step 3: Going Live

### 3.1 Deploy Backend (Render)
1.  Push code to GitHub.
2.  Create a "Web Service" on [Render.com](https://render.com).
3.  Link your GitHub repo.
4.  Set Environment Variables:
    - `SECRET_KEY`: (Random string)
    - `DATABASE_URL`: (Automatically provided if you create a Render PostgreSQL)
    - `ALLOWED_HOSTS`: `your-app-name.onrender.com`
    - `CORS_ALLOWED_ORIGINS`: `https://your-frontend.vercel.app`

### 3.2 Deploy Frontend (Vercel)
1.  Create a new project on [Vercel](https://vercel.com).
2.  Link the same GitHub repo.
3.  Set its "Root Directory" to `web-frontend`.
4.  Set Environment Variable:
    - `REACT_APP_API_URL`: `https://your-app-name.onrender.com/api`
5.  Deploy!
