web: python manage.py runserver 0.0.0.0:$PORT --noreload --insecure & python manage.py celeryd -v 1 -B -s celery -E -l INFO --concurrency=1
