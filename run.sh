#!/bin/bash

set -e

COLUMNS=$(tput co)
wrap () {
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

echo "Starting uWSGI..."
if [[ ! -f uwsgi.ini ]]; then
  cp uwsgi_example.ini uwsgi.ini
fi

uwsgi --ini uwsgi.ini "$@"
