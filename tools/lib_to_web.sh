#!/bin/bash

# Create a backup
mv -f src/lodeg_website/home/lodegML/*.py tools/tmp/migration_backups

# Copy the library
cp -f src/lodegML/*.py src/lodeg_website/home/lodegML

# Run the migration
find src/lodeg_website/home/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/import\(.*migrate\)/from ..lodegML import\1/g" 