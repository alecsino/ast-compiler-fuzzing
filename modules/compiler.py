import os
import subprocess
from modules.test import FuzzedTest, Test, Input, Stats

class Compiler:
    FLAGS = ["-O3", "-fno-unroll-loops", "-w", "-std=gnu99"]
    """Compiles the tests with the current compiler and with the previous"""
    def __init__(self, args: any):
        self.args = args
        pass
    
    def __compile_with(self, test, compiler: str):
        """Compiles a test with the specified version of the compiler into assembly"""

        output_name = "tmp_" + os.path.splitext(test.file_name)[0]

        dir = os.path.join(os.path.dirname(test.file_path), output_name)
        output_dir = os.path.join("tmp", output_name)

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
            print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
        
        os.remove(output_dir+".s")
        os.remove(dir+".c")
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

        if not os.path.exists('err'):
            os.makedirs('err')
        
        stats = Stats(file_path=test.name, file_name=os.path.basename(test.name), file_content=f_content)
        stats.add_compiler_stat("last", self.__compile_with(stats, self.args.compiler))

        for i in self.args.older_compilers:
            n = self.__compile_with(stats, i)

            if n == 0:
                continue
            
            stats.add_compiler_stat(i, n)

        return FuzzedTest(test, stats)
