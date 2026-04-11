web: python manage.py collectstatic --noinput && python manage.py migrate && gunicorn streetwear_store.wsgi:application --bind 0.0.0.0:$PORT
