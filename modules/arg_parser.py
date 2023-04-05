import argparse
import multiprocessing
import shutil

class ArgParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-c", "--compiler", help="Specify the compiler", default="gcc")
        self.parser.add_argument("-n", "--num_cores", help="Specify the number of cores to use", default=1, type=int)
       
        self.args = self.parser.parse_args()
        
        if not self.__is_valid_compiler(self.args.compiler):
            print(f"Could not find compiler {self.args.compiler}.")
            exit(1)

        if self.args.num_cores < 1 or multiprocessing.cpu_count() < self.args.num_cores:
            print("Invalid number of cores. Using 1 core.")
            self.args.num_cores = 1
        pass

    def __is_valid_compiler(self, compiler):
        return shutil.which(compiler) is not None