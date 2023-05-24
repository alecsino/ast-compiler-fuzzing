import os
import subprocess
from modules.test import FuzzedTest, Test, Input, Stats

class Compiler:
    """Compiles the tests with the current compiler and with the previous"""
    
    FLAGS = ["-O3", "-fno-unroll-loops", "-w"]

    def __init__(self, args: any):
        self.args = args
        pass

    def is_asan_safe(self, test: Stats, compiler: str):
        output_name = "tmp_asan_" + os.path.splitext(test.file_name)[0]
        dir = os.path.join(os.path.dirname(test.file_path), output_name)
        output_dir = os.path.join(".tmp", output_name)

        while os.path.isfile(dir+".c"):
            output_dir += "_"
        
        with open(dir+".c", "w") as f:
            f.write(test.file_content)

        if compiler == "last":
            compiler = self.args.compiler

        result = subprocess.run([compiler, dir+".c", "-fsanitize=address", "-o", output_dir] + self.FLAGS, stderr=subprocess.PIPE)
        if result.stderr:
            return False
        
        os.remove(dir+".c")

        try:
            result = subprocess.run(["./"+output_dir], stderr=subprocess.PIPE, timeout=10)
        except subprocess.TimeoutExpired:
            print("Timeout expired, probably asan safe")

        if result.stderr:
            return False
        
        os.remove(output_dir)

        return True

    
    def __compile_with(self, test, compiler: str):
        """
        Compiles a test with the specified version of the compiler into assembly
        
        Arguments:
            test {tuple} -- The stats object of the test to compile
            compiler {str} -- The compiler to use

        Returns:
            int -- The number of lines of the assembly file
        """

        output_name = "tmp_" + os.path.splitext(test.file_name)[0]

        dir = os.path.join(os.path.dirname(test.file_path), output_name)
        output_dir = os.path.join(".tmp", output_name)

        while os.path.isfile(dir+".c"):
            output_dir += "_"
        
        with open(dir+".c", "w") as f:
            f.write(test.file_content)

        result = subprocess.run([compiler, dir+".c", "-S", "-o", output_dir+".s"] + self.FLAGS, stderr=subprocess.PIPE)
        if result.stderr:
            with open(os.path.join("err", "err_"+output_name)+".c", "w") as f:
                f.write(test.file_content)
                f.write(result.stderr.decode("utf-8"))
            # print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
            os.remove(dir+".c")
            return 0

        num_lines = 0
        #count number of lines in the assembly file and then delete it - catch error if file does not exist
        try:
            with open(output_dir+".s") as f:
                num_lines = len(f.readlines())
        except FileNotFoundError:
            # print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
            pass
        
        try:
            os.remove(output_dir+".s")
        except OSError as e:
           pass

        os.remove(dir+".c")
        return num_lines
        

    def compile_test(self, tuple):
        """Compiles a test with the current compiler and with the previous
        
        Arguments:
            tuple {tuple} -- The test object to compile, its content and its inputs
        
        Raises:
            FileNotFoundError: If the test does not exist

        Returns:
            FuzzedTest -- The fuzzed test
        """
        
        test, f_content, old_inputs, new_inputs, depth, breadth, old_stats = tuple
        if not os.path.isfile(test.name):
            raise FileNotFoundError("File " + test + " does not exist")
        
        stats = Stats(file_path=test.name, file_name=os.path.basename(test.name), file_content=f_content)
        stats.add_compiler_stat("last", self.__compile_with(stats, self.args.compiler))

        for i in self.args.older_compilers:
            n = self.__compile_with(stats, i)

            if n == 0:
                continue
            
            stats.add_compiler_stat(i, n)

        return FuzzedTest(test=test, stats=stats, old_stats=old_stats, old_inputs=old_inputs, mutated_inputs=new_inputs, depth=depth, breadth=breadth)
