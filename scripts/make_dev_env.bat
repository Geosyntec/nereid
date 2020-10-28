call conda activate base
call conda env remove -n nereid_dev
call conda create -n nereid_dev python=3.8 jupyter
call conda activate nereid_dev
call pip install ^
  -r nereid\requirements.txt ^
  -r nereid\requirements_tests.txt
call conda activate base