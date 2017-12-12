# LoDEg

Log analytics for the LODE platform.

## The library: lodegML

lodegML is the name of the library on which the project runs. It exposes a facade API through the class LodegSystem. Please refer to the library [documentation](/docs/lodegML_docs/_build/html/index.html).

## Requirements

Make sure you have [python3.X](https://www.python.org/downloads/) installed and update [pip](https://pip.pypa.io/en/stable/installing/) to the latest version.

```
$ pip3 install --user --upgrade pip
```

Next, you can optionally create an isolated environment. This is recommended as it makes it possible to have a different environment for each project (e.g. one for this project), with potentially very different libraries, and different versions:

```
$ pip3 install --user --upgrade virtualenv
$ virtualenv -p `which python3` env
```

This creates a new directory called `env` in the current directory, containing an isolated Python environment based on Python 3\. If you installed multiple versions of Python 3 on your system, you can replace `` `which python3` `` with the path to the Python executable you prefer to use.

Now you must activate this environment. You will need to run this command every time you want to use this environment.

```
$ source ./env/bin/activate
```

Next, use pip to install the required python packages. If you are not using virtualenv, you should add the `--user` option (alternatively you could install the libraries system-wide, but this will probably require administrator rights, e.g. using `sudo pip3` instead of `pip3` on Linux).

```
$ pip3 install --upgrade -r requirements.txt
```

## WebApp

To deploy the WebApp run the following command in the folder lodeg_website:

```
$ python manage.py runserver [port_number]
```

The port number is not mandatory, defaults to 8000.

## Tests

The following tests are provided:

- Unit tests (with [coverage](/docs/testsCoverage/index.html))

  ```
  $ make tests [i,interactive]
  ```

- Library integrity tests (between the WebApp and the standalone library)

  ```
  $ make check
  ```

- Performance tests and benchmarking (todo)

  ```
  $ make tests performance (todo)
  ```

- Logs integrity check (todo)

  ```
    $ make tests integrity (todo)
  ```
