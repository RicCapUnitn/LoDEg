#!/bin/bash

echo '#######################################################################################'

if [ "$1" == "i" ] || [ "$1" == "interactive" ]; then
  echo '>>> Select the tests to be run from the following list'
  echo '>>> s to skip, ENTER to run'
  echo '>>> Integration test? s(skip) / ENTER'
  read integration
  echo '>>> Unit test?'
  read unit
  echo '>>> Coverage test?'
  read coverage
fi


echo ">>> Creating mockup populations..."
cd ./test/populations; python sample_population.py
cd ../../
echo '>>> Done!'
echo '#######################################################################################'

echo ">>> Import mockup populations..."
mongoimport --db lodeg --collection mockup_population --drop --maintainInsertionOrder --file ./test/populations/population.json
mongoimport --db lodeg --collection mockup_lessons --drop --maintainInsertionOrder --file ./test/populations/lessons.json
echo '>>> Done!'
echo '#######################################################################################'

if [ "$integration" == "s" ]; then
  echo '>>> SKIP integration test'
else
  echo ">>> INTEGRATION TESTS: running..."
  ./tools/check_migration.sh
  echo '>>> Done!'
  echo '#######################################################################################'
fi

if [ "$unit" == "s" ]; then
  echo '>>> SKIP unit test'
  if [ "$coverage" == "s" ]; then
      echo '>>> SKIP coverage test: unit test required'
    fi
else
  if [ "$coverage" == "s" ]; then
    echo '>>> SKIP coverage test'
    echo ">>> UNIT TEST: running..."
    python -m unittest discover -v -s ./test/unit
  else
    echo ">>> UNIT TEST: running..."
    echo ">>> COVERAGE TEST: running..."
    coverage run --source=./src/lodegML -m unittest discover -v -s ./test/unit
    coverage html -d ./docs/testsCoverage
  fi
  echo '>>> Done!'
  echo '#######################################################################################'
fi

if [ "$coverage" != "s" ]; then
  echo ">>> COVERAGE RESULT:"
  coverage report
fi
