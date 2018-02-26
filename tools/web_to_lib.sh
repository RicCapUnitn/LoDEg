#!/bin/bash

# Create a backup
mv -f src/lodegML/* tools/tmp/migration_backups/

# Copy the library
cp -r -f src/lodeg_website/home/lodegML/* src/lodegML/

# Run the migration
find src/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from \.\.\.lodegML\.\(configure\.configurations\) import\(.*migrate\)/from \1 import\2/g"
find src/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from \.\.lodegML\.\(.*\) import\(.*migrate\)/from \1 import\2/g"
find src/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from \.\.lodegML import\(.*migrate\)/import\1/g"
