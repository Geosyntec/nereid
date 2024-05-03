#!/bin/bash

set -e

cleanup_pip () {

if [ ! -z "$(pip freeze)" ]
then
    echo "cleaning up"
    pip uninstall -y -r <(pip freeze)
    pip install uv
fi

}


# setup env
eval "$(conda shell.bash hook)"
conda activate base
conda remove -n nereid-install --all -y
conda create -n nereid-install python=3.11 -y
conda activate nereid-install
pip install uv


# start building deps
cleanup_pip

# dev
uv pip install -r nereid/requirements/requirements_dev_unpinned.txt
uv pip freeze > nereid/requirements/requirements_dev.txt


cleanup_pip

# nereid
uv pip install -r nereid/requirements/requirements_nereid_unpinned.txt
uv pip freeze > nereid/requirements/requirements_nereid.txt

cleanup_pip

# worker
uv pip install -r nereid/requirements/requirements_worker_unpinned.txt
uv pip freeze > nereid/requirements/requirements_worker.txt

cleanup_pip

# lint
uv pip install -r nereid/requirements/requirements_lint_unpinned.txt
uv pip freeze > nereid/requirements/requirements_lint.txt

cleanup_pip
