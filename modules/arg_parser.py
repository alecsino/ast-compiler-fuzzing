import argparse
import multiprocessing
import shutil
import subprocess

class ArgParser:
    """ This class is used to parse the command line arguments. """
    DEFAULT_COMPILER = "gcc"

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-c", "--compiler", help="Specify the compiler", default=self.DEFAULT_COMPILER)
        self.parser.add_argument("-n", "--num_cores", help="Specify the number of cores to use", default=1, type=int)
        self.parser.add_argument("-t", "--threshold", help="Specify the threshold for the fuzzer", default=10, type=int)
       
        self.args = self.parser.parse_args()
        
        if not "gcc" in self.args.compiler and not "clang" in self.args.compiler:
            print(f"Invalid compiler. Compatible compilers are gcc and clang.")
            exit(1)
        
        self.args.compiler_type = "gcc" if "gcc" in self.args.compiler else "clang"

        if not self.__is_valid_compiler(self.args.compiler):
            print(f"Could not find compiler {self.args.compiler}.")
            exit(1)

        self.args.compiler_version = self.__get_compiler_version(self.args.compiler)
        self.args.older_compilers = self.__get_older_compilers(self.args.compiler_version)

        if self.args.num_cores < 1 or multiprocessing.cpu_count() < self.args.num_cores:
            print("Invalid number of cores. Using 1 core.")
            self.args.num_cores = 1
        pass

    def __is_valid_compiler(self, compiler):
        """ Checks if the compiler is valid by if the binary is in the PATH or exists. """
        return shutil.which(compiler) is not None

    def __get_compiler_version(self, compiler):
        """ Gets the compiler version by running the compiler with the --version flag. """
        result = subprocess.run([compiler, "--version"], capture_output=True, text=True)
        result = result.stdout.split(".")[0][-2:].strip()
        #check if result is int
        if result.isdigit():
            return int(result)
        else:
            print("Could not get compiler version.")
            exit(1)

    def __get_older_compilers(self, compiler_version):
        """ Gets the older compilers by checking compiler 1 to compiler_version - 1. """
        older_compilers = []
        for i in range(1, compiler_version):
            if self.__is_valid_compiler(f"{self.args.compiler_type}-{i}"):
                older_compilers.append(f"{self.args.compiler_type}-{i}")
        
        return older_compilers
    