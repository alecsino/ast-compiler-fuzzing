
## **Set up**

### Requirements
Make sure you have `pip` installed. To check if pip is install, run the following snippet 
```bash
    $ pip --version
```

If you do not have `pip`, you can install it with the following commands
```bash 
    $ curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    $ python get-pip.py
```

More details about this script can be found in [pypa/get-pip](https://github.com/pypa/get-pip)’s README.

### Virtual Environment

Make sure you have the virtual environment activated by running
```bash
   $ source env/bin/activate
```

To install the packages run
```bash 
   $ pip install -r requirements.txt
```

Finally, you can deactivate the virtual environment with
```bash
   $ deactivate
```


## **Tests**
To run the tests, from the project directory run

```bash
   pytest .
```

## **Docker**

To facilitate running the tool, we provide a docker image

```bash
   docker build -t ast-compiler-fuzzing .
```


##  **Troubleshooting**

Make sure your architecture supports the address sanatizer check with asan using the flag `-fsanatize=address`.

