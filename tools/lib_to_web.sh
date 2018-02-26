#!/bin/bash

# Create a backup
mv -f src/lodeg_website/home/lodegML/* tools/tmp/migration_backups/

# Copy the library
cp -r -f src/lodegML/* src/lodeg_website/home/lodegML/

# Run the migration
find src/lodeg_website/home/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from \(configure\.configurations\) import\(.*migrate\)/from ...lodegML\.\1 import\2/g"
find src/lodeg_website/home/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from \([\.]\+\)\(.*\) import\(.*migrate\)/from \1lodegML\.\2 import\3/g"
find src/lodeg_website/home/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from \([^\.].*\) import\(.*migrate\)/from ..lodegML\.\1 import\2/g"
find src/lodeg_website/home/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/^import\(.*migrate\)/from ..lodegML import\1/g"
