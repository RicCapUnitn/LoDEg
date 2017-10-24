#!/bin/bash

# Move to the parent folder
cd ..

# Migrate
sed -e 's/lodegML/..lodegML/g' *.py > *_test.py
find . -type f -exec sed -i_test.py "s/foo/bar/g" {} \;
find . -type f -name "*.txt" -print0 | xargs -0 sed -i "s/foo/bar/g"

find src/lodegML/ -type f -name "*.py" -print0 | xargs -0 sed -i "s/from ./from ..lodegMl/g"