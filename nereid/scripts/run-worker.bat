set FORKED_BY_MULTIPROCESSING=1
cd ..\nereid
celery worker --app nereid.bg_worker -l info -c 4 -O fair