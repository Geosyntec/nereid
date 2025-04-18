#!/bin/bash

set -e

pip install -U "uv>=0.6,<0.7"

# dev
uv pip compile requirements/requirements_dev_unpinned.txt > requirements/requirements_dev.txt

# nereid
uv pip compile requirements/requirements_nereid_unpinned.txt > requirements/requirements_nereid.txt

# worker
uv pip compile requirements/requirements_worker_unpinned.txt > requirements/requirements_worker.txt

# lint
uv pip compile requirements/requirements_lint_unpinned.txt > requirements/requirements_lint.txt
