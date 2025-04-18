# Austin Orr 11/27/2019
# This approach is the fastest to build and yields reasonably
# small images at ~500mb each. The alpine+install variant of this
# pattern is able to reduce each image to ~250MB but takes considerable
# time to build and is considerably more complex for scipy and pandas.

FROM node:20.19-bullseye AS frontend
WORKDIR /app
COPY ./nereid/nereid/static/frontend .
RUN npm install . && npm run build
CMD ["bash", "-c", "while true; do sleep 1; done"]


FROM python:3.11.12-bullseye AS nereid_install
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /nereid
CMD ["bash", "-c", "while true; do sleep 1; done"]


FROM redis:6.2.17-alpine3.21 AS redis
COPY nereid/redis.conf /redis.conf
CMD ["redis-server", "/redis.conf"]


FROM python:3.11.12-alpine3.21 AS flower
RUN apk add --no-cache ca-certificates tzdata && update-ca-certificates
RUN pip install --no-cache-dir redis==4.6.0 flower==1.0.0 celery==5.3.4
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1
ENV FLOWER_DATA_DIR=/data
ENV PYTHONPATH=${FLOWER_DATA_DIR}
WORKDIR $FLOWER_DATA_DIR
# Add a user with an explicit UID/GID and create necessary directories
ENV IMG_USER=flower
RUN set -eux; \
    addgroup -g 1000 ${IMG_USER}; \
    adduser -u 1000 -G ${IMG_USER} ${IMG_USER} -D; \
    mkdir -p "$FLOWER_DATA_DIR"; \
    chown ${IMG_USER}:${IMG_USER} "$FLOWER_DATA_DIR"
USER ${IMG_USER}
VOLUME $FLOWER_DATA_DIR
# Default port
EXPOSE 5555
CMD ["celery", "flower"]


FROM python:3.11.12-bullseye AS core-env
RUN apt-get update && apt-get install -y build-essential curl
ADD https://astral.sh/uv/0.6.14/install.sh /install.sh
RUN sh /install.sh && rm /install.sh
ENV VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/root/.local/bin/:$PATH
COPY requirements/requirements_worker.txt /requirements_worker.txt
RUN uv venv /opt/venv && \
    uv pip install --no-cache -r /requirements_worker.txt


FROM core-env AS server-env
COPY requirements/requirements_nereid.txt /requirements_nereid.txt
COPY requirements/requirements_server.txt /requirements_server.txt
RUN  uv pip install --no-cache \
    -r /requirements_nereid.txt \
    -r /requirements_server.txt


FROM core-env AS test-env
COPY requirements/requirements_dev.txt /requirements_dev.txt
RUN  uv pip install --no-cache \
    -r /requirements_dev.txt


FROM python:3.11.12-slim-bullseye AS core-runtime
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends graphviz \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /nereid
ENV PYTHONPATH=/nereid
ENV PATH=/opt/venv/bin:$PATH


FROM core-runtime AS celeryworker
# Add a user with an explicit UID/GID and create necessary directories
ENV IMG_USER=celeryworker
RUN addgroup --gid 1000 ${IMG_USER} \
    && adduser --no-create-home --system --disabled-password --uid 1000 --gid 1000 ${IMG_USER}
USER ${IMG_USER}
COPY --from=core-env --chown=${IMG_USER} /opt/venv /opt/venv
COPY --chmod=755 nereid/scripts /
COPY --chown=${IMG_USER}:${IMG_USER} nereid/nereid /nereid/nereid
CMD ["bash", "/run-worker.sh"]


FROM core-runtime AS nereid
COPY --from=server-env /opt/venv /opt/venv
COPY --chmod=755 nereid/scripts /
COPY nereid/nereid /nereid/nereid
COPY --from=frontend /app/dist /nereid/nereid/static/frontend/dist
COPY nereid/gunicorn_conf.py /gunicorn_conf.py
EXPOSE 80
CMD ["bash", "/start.sh"]


FROM core-runtime AS nereid-tests
COPY --from=test-env /opt/venv /opt/venv
# COPY .coveragerc /nereid/.coveragerc
# COPY conftest.py /nereid/conftest.py
COPY pyproject.toml /nereid/pyproject.toml
COPY --chmod=755 nereid/scripts /
## This will make the container wait, doing nothing, but alive
CMD ["bash", "-c", "while true; do sleep 1; done"]


FROM python:3.12-bullseye AS nereid-edge
RUN apt-get update -y \
    && apt-get install -y graphviz build-essential curl \
    && rm -rf /var/lib/apt/lists/*
ADD https://astral.sh/uv/0.6.14/install.sh /install.sh
RUN sh /install.sh && rm /install.sh
ENV PATH=/opt/venv/bin:/root/.local/bin/:$PATH
COPY requirements /
RUN uv venv /opt/venv && \
    uv pip install --no-cache -r /requirements_dev_unpinned.txt
COPY nereid/nereid /nereid/nereid
COPY pyproject.toml /nereid/pyproject.toml
COPY --from=frontend /app/dist /nereid/nereid/static/frontend/dist
COPY --chmod=755 nereid/scripts /
WORKDIR /nereid
ENV PYTHONPATH=/nereid


FROM nereid-edge AS nereid-edge-tests
CMD ["bash", "-c", "while true; do sleep 1; done"]


FROM nereid-edge AS celeryworker-edge
ENV C_FORCE_ROOT=1
CMD /run-worker.sh
