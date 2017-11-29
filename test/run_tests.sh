echo "\n####################################"
echo "# INTEGRATION TESTS                #"
echo "####################################\n"

./tools/check_migration.sh

echo "\n####################################"
echo "# UNIT TESTS                       #"
echo "####################################\n"

# echo "\n>>> Start the mongo service"
# sudo service mongod start

echo "\n>>> Creating mockup populations"
cd ./test/populations; python sample_population.py
cd ../../
echo "Done"

echo "\n>>> Import mockup populations"
mongoimport --db lodeg --collection mockup_population --drop --maintainInsertionOrder --file ./test/populations/population.json
mongoimport --db lodeg --collection mockup_lessons --drop --maintainInsertionOrder --file ./test/populations/lessons.json

echo "\n>>> Run tests (while computing coverage)"
coverage run --source=./src/lodegML -m unittest discover -v -s ./test/unit

echo "\n####################################"
echo "# CODE COVERAGE                    #"
echo "####################################\n"

coverage report
