#!/bin/bash

set -e

wrap () {
  COLUMNS=$(tput cols || echo 80)
  echo "$@" | fmt -w $((COLUMNS - 5))
}

cd "${0%/*}"

if [[ ! -d venv ]]; then
  echo "First run; creating virtual environment..."
  wrap "Using ${PYTHON_EXE:="$(which python3)"} as the Python interpreter. Set the PYTHON_EXE variable to use a different Python interpreter."
  "$PYTHON_EXE" -m venv venv
  source venv/bin/activate
  pip install -U pip setuptools wheel
  pip install -Ur requirements.txt
  echo
else
  source venv/bin/activate
fi

mkdir -m 700 -p log

echo "Starting Gunicorn..."
if [[ ! -f gunicorn_config.py ]]; then
  cp gunicorn_config_example.py gunicorn_config.py
fi

gunicorn -c gunicorn_config.py -D app:app
