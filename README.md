# Feedback Dashboard (Django)

## Run it
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py seed_feedback      # optional sample data
    python manage.py runserver

- Dashboard (no login required): http://127.0.0.1:8000/dashboard/
- Customer form (no login): http://127.0.0.1:8000/feedback/
- Django Administration Panel (superuser login): http://127.0.0.1:8000/admin/

## Add to your existing project
Copy the `feedback/` app, add `"feedback"` to INSTALLED_APPS, include `feedback.urls`
in your root urls, and copy the "Feedback dashboard" block from `config/settings.py`.
If you already have your own feedback model, point `feedback/excel.py` and `views.py` at it.

## Settings (config/settings.py)
- `FEEDBACK_ANALYSIS_XLSX`: the one shared workbook. Export refreshes its "Feedback" sheet in place;
  other sheets (Summary, your own notes or charts) are kept.
- `FEEDBACK_FORM_URL`: public URL shown in the Copy box (defaults to this site's /feedback/).
- Email uses SMTP. `EMAIL_HOST` defaults to `smtp.gmail.com`; override it for another provider.
  Set `EMAIL_PORT` (defaults to `587`), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, and optionally
  `DEFAULT_FROM_EMAIL` as environment variables. For Gmail, use your full Gmail address as
  `EMAIL_HOST_USER` and a Google App Password as `EMAIL_HOST_PASSWORD` (not your account password).
  SMTP authentication credentials are optional for servers that permit unauthenticated sending;
  if provided, set both username and password. `EMAIL_USE_TLS` defaults to `1`; set it to `0`
  when not used. For implicit TLS, set `EMAIL_USE_SSL=1` and `EMAIL_USE_TLS=0`.
  `EMAIL_TIMEOUT` defaults to `10` seconds.
  The send dialog reports success only after the SMTP server accepts the message; connection,
  authentication, and configuration errors are returned in the dialog.
- `FEEDBACK_COMPANY_NAME`: used in the email template.
