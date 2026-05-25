#!/bin/bash


cd ..

# add -v to be more verbose
python -m unittest discover -s tests -p "test_*.py" -v
cd tests
