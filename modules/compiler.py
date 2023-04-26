import os
import subprocess

class Compiler:
    FLAGS = ["-O3", "-fno-unroll-loops"]
    """Compiles the tests with the current compiler and with the previous"""
    def __init__(self, args):
        self.args = args
        pass
    
    def __compile_with(self, test, compiler):
        """Compiles a test with the specified version of the compiler into assembly"""
        #get only the name of the file - removes path and extension
        output_name = os.path.splitext(os.path.basename(test))[0] + ".s"

        output_dir = os.path.join("tmp", output_name)
        try:
            subprocess.run([compiler, test, "-S", "-o", output_dir] + self.FLAGS, check=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # print(f"Compilation of file {test} with compiler {compiler} failed.")
            return 0

        num_lines = 0
        #count number of lines in the assembly file and then delete it - catch error if file does not exist
        try:
            with open(output_dir) as f:
                num_lines = len(f.readlines())
        except FileNotFoundError:
            print(f"Compilation of file {test} with compiler {compiler} failed.")
        
        os.remove(output_dir)
        return num_lines
        

    def compile_test(self, test):
        """Compiles a test with the current compiler and with the previous
        
        Arguments:
            test {Test} -- The test to compile
        
        Raises:
            FileNotFoundError: If the test does not exist

        Returns:
            FuzzedTest -- The fuzzed test
        """
        
        if not os.path.isfile(test.name):
            raise FileNotFoundError("File " + test + " does not exist")

        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        
        stats = {
            "last":  self.__compile_with(test.name, self.args.compiler)
        }

        for i in self.args.older_compilers:
            n = self.__compile_with(test.name, i)

            if n == 0:
                return None
            
            stats[i] = n

        stats["file"] = os.path.basename(test.name)
        return FuzzedTest(test,stats)

