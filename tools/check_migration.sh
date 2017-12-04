# Migrate a temp library
cp -f src/lodegML/*.py tools/tmp/migration_backups
find tools/tmp/migration_backups -type f -name "*.py" -print0 | xargs -0 sed -i "s/import\(.*migrate\)/from ..lodegML import\1/g"

# Compute md5 for the lib dir
find tools/tmp/migration_backups -maxdepth 1 -type f -name "*.py" -exec md5sum {} \; |cut -c-32 |sort > tools/tmp/webmd5.txt

# Compute md5 for the web temporary migrated dir
find src/lodeg_website/home/lodegML -maxdepth 1 -type f -name "*.py" -exec md5sum {} \; |cut -c-32 |sort > tools/tmp/libmd5.txt

# Check differences
diff -s tools/tmp/libmd5.txt tools/tmp/webmd5.txt
