

The file 'main.yml' lives in 'bb/.github/workflows/main.yml':

```yml
name: Python CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    # repository code
    - name: Checkout code
      uses: actions/checkout@v3

    # set up
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    # dependencies, if any
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f bb/workbook/ch03/ci/requirements.txt ]; then pip install -r requirements.txt; fi

    # PYTHONPATH (include script's parent directory, if needed)
    - name: Set PYTHONPATH
      run: echo "PYTHONPATH=$PYTHONPATH:$(pwd)/bb/workbook/ch03/ci" >> $GITHUB_ENV

    # unit tests using Python's unittest
    - name: Run tests
      run: |
        python -m unittest discover -s bb/workbook/ch03/ci -p 'test_*.py'
```