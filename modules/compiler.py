import os
import subprocess
from modules.test import FuzzedTest, Stats

class Compiler:
    """Compiles the tests with the current compiler and with the previous"""

    def __init__(self, args: any):
        self.args = args
        self.FLAGS = args.flags
        pass

    def is_asan_safe(self, test: Stats, compiler: str) -> bool:
        output_name = "tmp_asan_" + os.path.splitext(test.file_name)[0]
        dir = os.path.join(os.path.dirname(test.file_path), output_name)

        while os.path.isfile(dir+".c"):
            dir += "_"
            output_name += "_"

        output_dir = os.path.join(".tmp", output_name)

        with open(dir+".c", "w") as f:
            f.write(test.file_content)

        if compiler == "last":
            compiler = self.args.compiler

        result = subprocess.run([compiler, dir+".c", "-fsanitize=address", "-o", output_dir] + self.FLAGS, stderr=subprocess.PIPE)
        if result.stderr:
            # Could not compile with asan, probably a problem of the architecture
            test.asan_tested = False
            test.error_message = result.stderr.decode("utf-8")
            return True
        
        os.remove(dir+".c")

        try:
            result = subprocess.run(["./"+output_dir], stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=10)
        except subprocess.TimeoutExpired:
            test.error_message = "Timeout expired, probably asan safe"
            # print("Timeout expired, probably asan safe")
            pass

        test.asan_tested = True

        if result.stderr:
            # print(result.stderr.decode("utf-8"))
            test.error_message = result.stderr.decode("utf-8")
            os.remove(output_dir)
            return False
        
        os.remove(output_dir)

        return True

    
    def __compile_with(self, test, compiler: str) -> int:
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

        while os.path.isfile(dir+".c"):
            dir += "_"
            output_name += "_"

        output_dir = os.path.join(".tmp", output_name)

        with open(dir+".c", "w") as f:
            f.write(test.file_content)

        try:
            result = subprocess.run([compiler, dir+".c", "-S", "-o", output_dir+".s"] + self.FLAGS, stderr=subprocess.PIPE, timeout=5)
        except subprocess.TimeoutExpired:
            os.remove(dir+".c")

            try:
                os.remove(output_dir+".s")
            except OSError as e:
                pass
            
            return 0
        
        
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
                  for line in f.readlines():
                    line = line.strip()
                    if line.startswith('#') or line.startswith('.'):
                        continue  # Skip comment lines and directives
                    num_lines += 1

        except (FileNotFoundError, OSError):
            # print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
            pass

        try:
            os.remove(output_dir+".s")
        except OSError as e:
           pass

        os.remove(dir+".c")
        return num_lines
        

    def compile_test(self, tuple) -> FuzzedTest:
        """Compiles a test with the current compiler and with the previous
        
        Arguments:
            tuple {tuple} -- The test object to compile, its content and its inputs
        
        Raises:
            FileNotFoundError: If the test does not exist

        Returns:
            FuzzedTest -- The fuzzed test
        """
        
        test, f_content, new_inputs  = tuple
        if not os.path.isfile(test.name):
            raise FileNotFoundError("File " + test + " does not exist")
        
        stats = Stats(file_path=test.name, file_name=os.path.basename(test.name), file_content=f_content)
        stats.add_compiler_stat("last", self.__compile_with(stats, self.args.compiler))

        for i in self.args.older_compilers:
            n = self.__compile_with(stats, i)

            if n == 0:
                continue
            
            stats.add_compiler_stat(i, n)
        
        stats.set_max() # Used to set the max_rateo variable

        return FuzzedTest(test=test, stats=stats, mutated_inputs=new_inputs)
