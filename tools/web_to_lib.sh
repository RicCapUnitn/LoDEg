#!/bin/bash

# Create a backup
mv -f src/lodegML/*.py tools/migration_backups

# Copy the library
cp -f src/lodeg_website/home/lodegML/*.py src/lodegML

# Run the migration
find src/lodegML -type f -name "*.py" -print0 | xargs -0 sed -i "s/from ..lodegML import\(.*migrate\)/import\1/g" 