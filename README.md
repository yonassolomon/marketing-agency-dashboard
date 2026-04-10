# Marketing agency — client campaign manager

Django 4.x app with username/password auth, SQLite, and per-user data for clients, campaigns, notes, and tasks.

## Prerequisites

- Python 3.10+ recommended
- pip

## Setup and run

1. **Open a terminal** in the project folder (the directory that contains `manage.py`).

2. **Create and activate a virtual environment** (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**

   ```powershell
   pip install -r requirements.txt
   ```

4. **Apply database migrations** (creates `db.sqlite3`):

   ```powershell
   python manage.py migrate
   ```

5. **Create an admin user** (optional — for `/admin/` only):

   ```powershell
   python manage.py createsuperuser
   ```

6. **Run the development server:**

   ```powershell
   python manage.py runserver
   ```

7. **Use the app:** open [http://127.0.0.1:8000/](http://127.0.0.1:8000/). You will be redirected to log in. Use **Register** to create an account, or log in if you already have one.

## URLs

| Path | Purpose |
|------|---------|
| `/` | Dashboard (after login) |
| `/register/` | New account |
| `/login/` | Login |
| `/logout/` | Logout (POST) |
| `/clients/add/` | New client |
| `/clients/<id>/` | Client detail (campaigns, notes, tasks) |

## Security note

`SECRET_KEY` in `marketing_agency/settings.py` is a development default. Before any real deployment, set a unique secret via environment variable and set `DEBUG = False`.

## Project layout

- `marketing_agency/` — project settings and root `urls.py`
- `agency/` — app: `models.py`, `views.py`, `urls.py`, `forms.py`, `templates/agency/`
