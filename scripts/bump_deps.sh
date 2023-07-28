set -e

cleanup_pip () {

if [ ! -z "$(pip freeze)" ]
then
    echo "cleaning up"
    pip uninstall -y -r <(pip freeze)
fi

}

cleanup_pip

# dev
pip install -r nereid/requirements_dev_unpinned.txt
pip freeze > nereid/requirements_dev.txt


cleanup_pip

# nereid
pip install -r nereid/requirements_nereid_unpinned.txt
pip freeze > nereid/requirements_nereid.txt

cleanup_pip

# worker
pip install -r nereid/requirements_worker_unpinned.txt
pip freeze > nereid/requirements_worker.txt

cleanup_pip

# lint
pip install -r nereid/requirements_lint_unpinned.txt
pip freeze > nereid/requirements_lint.txt

cleanup_pip
