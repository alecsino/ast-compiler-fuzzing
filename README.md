# **Compiler Fuzzing via Guided Value Mutation**

This repository contains the code for a fuzzer developed to identify missed optimizations and performance decreases across different versions of the same compiler. . The fuzzer works by generating mutants of a given seed program, specifically targeting the mutation of constant values, and analyzing the resulting binary differences.

## **Features**

- **Mutation techniques**: The fuzzer supports different mutation techniques, including random value generation, boundary value generation, and modification of input values.
- **Guided fuzzing**: The fuzzer utilizes a feedback loop to guide the mutation process and focus on generating mutants that trigger significant differences in the number of executed instructions.
- **Preprocessing**: The dataset used for the experiments is the GCC tests dataset, and preprocessing steps have been implemented to filter out executable tests and reduce the size of the dataset for faster fuzzing.
- **Compilation and comparison**: The fuzzer compiles the mutated programs using different versions of the same compiler, with optimization flags enabled. It then compares the generated binaries to identify significant differences in performance.


## **Set up**


### **Locally**

#### **Requirements**
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

Make sure to also at least two versions of the same compiler available.
The code has been tested using `gcc` and therefore it is advised to use gcc as well.

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


### **Dockerfile**
We also provide a Docker image with the needed dependencies.

Build it and run it with the following commands

```bash
   $ docker build -t ast-compiler-fuzzing .
   $ docker run -it -v /path/to/ast-compiler-fuzzing:/app ast-compiler-fuzzing
```


## **How to run it**

Make sure the dataset is correctly placed in the input folder. To do so just unzip the provided archive:
```bash
   $ unzip input.zip
```

To run the fuzzer, from the docker set up as above or locally, use

```bash
   $ python ast-compiler-fuzzing/main.py -n <num_cores> -t <threshold> -O <optimization> -c <main_compiler>
```

An example of run with 4 cores, using the -O3 flag, using as the main compiler gcc-12 and stopping at 20 files is:
```bash
   $ python ast-compiler-fuzzing/main.py -n 4 -t 20 -O 3 -c gcc-12
```


##  **Troubleshooting**

Make sure your architecture supports the address sanatizer check with asan using the flag `-fsanatize=address`.

Make sure that all the compilers can be found in the path.
