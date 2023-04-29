import os
import subprocess
from modules.test import FuzzedTest, Test, Input, Stats
class Compiler:
    FLAGS = ["-O3", "-fno-unroll-loops"]
    """Compiles the tests with the current compiler and with the previous"""
    def __init__(self, args: any):
        self.args = args
        pass
    
    def __compile_with(self, test, compiler: str):
        """Compiles a test with the specified version of the compiler into assembly"""
        #get only the name of the file - removes path and extension
        output_name = os.path.splitext(test.file_name)[0]
        output_dir = os.path.join("tmp", output_name)

        while os.path.isfile(output_dir + ".c"):
            output_dir += "_"
        
        with open(output_dir+".c", "w") as f:
            f.write(test.file_content)

        try:
            subprocess.run([compiler, output_dir+".c", "-S", "-o", output_dir+".s"] + self.FLAGS, check=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
            return 0

        num_lines = 0
        #count number of lines in the assembly file and then delete it - catch error if file does not exist
        try:
            with open(output_dir+".s") as f:
                num_lines = len(f.readlines())
        except FileNotFoundError:
            print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
        
        os.remove(output_dir+".s")
        os.remove(output_dir+".c")
        return num_lines
        

    def compile_test(self, tuple):
        """Compiles a test with the current compiler and with the previous
        
        Arguments:
            test {Test} -- The test to compile
        
        Raises:
            FileNotFoundError: If the test does not exist

        Returns:
            FuzzedTest -- The fuzzed test
        """
        test, f_content = tuple
        
        if not os.path.isfile(test.name):
            raise FileNotFoundError("File " + test + " does not exist")

        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        
        stats = Stats(file_path=test.name, file_name=os.path.basename(test.name), file_content=f_content)
        stats.add_compiler_stat("last", self.__compile_with(stats, self.args.compiler))

        for i in self.args.older_compilers:
            n = self.__compile_with(stats, i)

            if n == 0:
                continue
            
            stats.add_compiler_stat(i, n)

        return FuzzedTest(test, stats)
