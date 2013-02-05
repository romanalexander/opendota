web: gunicorn dotastats.wsgi & python manage.py celeryd -v 1 -B -s celery -E -l INFO --concurrency=1
