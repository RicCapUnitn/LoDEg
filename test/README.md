# Tests

To run tests navigate to the top directory and run

```
$ make tests
```

## Test populations

```
$ sudo service mongod start
$ mongoimport --db lodeg --collection web_mockup_population --drop --maintainInsertionOrder --file ./web_population.json
$ mongoimport --db lodeg --collection web_mockup_lessons --drop --maintainInsertionOrder --file ./web_lessons.json
```
