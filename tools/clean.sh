# Remove all exports/imports in the src	folder
rm -f src/lodegML/*.json
rm -f src/lodegML/*.p
rm -f test/unit/test_output/*
rm -rf htmlcov
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
find . | grep -E "(.coverage)" | xargs rm -rf
find tools/tmp/* ! -name '.*' ! -type d -exec rm -- {} +
