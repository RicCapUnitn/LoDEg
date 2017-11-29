echo "\n####################################"
echo "# INTEGRATION TESTS                #"
echo "####################################\n"

./tools/check_migration.sh

echo "\n####################################"
echo "# UNIT TESTS                       #"
echo "####################################\n"

python -m unittest discover -s ./test/unit
