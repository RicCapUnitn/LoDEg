# Tests

To run tests run the following command in the home directory:

	$ python -m unittest discover


## Test populations

	$ sudo service mongod start
	$ mongoimport --db lodeg --collection web_mockup_population --drop --maintainInsertionOrder --file ./web_population.json
	$ mongoimport --db lodeg --collection web_mockup_lessons --drop --maintainInsertionOrder --file ./web_lessons.json
