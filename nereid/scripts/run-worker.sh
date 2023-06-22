celery --app nereid.bg_worker worker -l INFO -c 4 -O fair -B
