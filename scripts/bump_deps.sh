#!/bin/bash

set -e

pip install -U "uv>=0.5,<0.6"

# dev
uv pip compile nereid/requirements/requirements_dev_unpinned.txt > nereid/requirements/requirements_dev.txt

# nereid
uv pip compile nereid/requirements/requirements_nereid_unpinned.txt > nereid/requirements/requirements_nereid.txt

# worker
uv pip compile nereid/requirements/requirements_worker_unpinned.txt > nereid/requirements/requirements_worker.txt

# lint
uv pip compile nereid/requirements/requirements_lint_unpinned.txt > nereid/requirements/requirements_lint.txt
