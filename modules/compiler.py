import os
import subprocess
from modules.test import FuzzedTest, Stats

class Compiler:
    """Compiles the tests with the current compiler and with the previous"""
    
    FLAGS = ["-O3", "-fno-unroll-loops", "-w"]

    def __init__(self, args: any):
        self.args = args
        pass

    def _return_unused_name(self, name: str, dir: str) -> str:
        """Returns an unused name in the directory"""
        while os.path.isfile(os.path.join(dir, name)):
            name += "_"
        return name

    def _run_and_remove(self, flags: list[str], path:str = "", timeout: int = 3) -> dict[str, any]:

        run_result = {
            "error_message": False,
            "timeout": False
        }

        if not path:
            #first item of flags
            path = flags[0]

        result = None

        try:
            result = subprocess.run(flags, stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=timeout)
        except subprocess.TimeoutExpired:
            run_result["timeout"] = True
        except Exception as e:
            print(e)
        
        if result and result.stderr:
            run_result["error_message"] = result.stderr.decode("utf-8")
        
        os.remove(path)
        return run_result

        


    def is_asan_safe(self, test: Stats, compiler: str) -> bool:
        output_name = self._return_unused_name("tmp_asan_" + test.file_name, os.path.dirname(test.file_path))
        c_dir = os.path.join(os.path.dirname(test.file_path), output_name)
        asan_dir = os.path.join(".tmp", output_name)

        with open(c_dir, "w") as f:
            f.write(test.file_content)

        if compiler == "last":
            compiler = self.args.compiler

        result = self._run_and_remove([compiler, c_dir, "-fsanitize=address", "-o", asan_dir] + self.FLAGS, c_dir)
        if result["error_message"] or result["timeout"]:
            # Could not compile with asan, probably a problem of the architecture
            test.asan_tested = False
            test.error_message = "timeout" if result["timeout"] else result["error_message"]
            return True


        result = self._run_and_remove(["./"+asan_dir])
        test.asan_tested = True
        test.error_message = "timeout" if result["timeout"] else None

        if result["error_message"]:
            test.error_message = result["error_message"]
            return False

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

        output_name = self._return_unused_name("tmp_" + test.file_name, os.path.dirname(test.file_path))
        c_dir = os.path.join(os.path.dirname(test.file_path), output_name)
        s_dir = os.path.join(".tmp", output_name.replace(".c", ".s"))

        with open(c_dir, "w") as f:
            f.write(test.file_content)

        result = self._run_and_remove([compiler, c_dir, "-S", "-o", s_dir] + self.FLAGS, c_dir)
        if result["timeout"]: #Compilation timeouted - probably the file is too big
            try:
                os.remove(s_dir)
            except OSError as e:
                pass
            return 0
        
        # Log compilation errors
        if result["error_message"]:
            with open(os.path.join("err", "err_"+output_name), "w") as f:
                f.write(test.file_content)
                f.write(result["error_message"])
            return 0

        num_lines = 0
        #count number of lines in the assembly file and then delete it - catch error if file does not exist
        try:
            with open(s_dir) as f:
                  for line in f.readlines():
                    line = line.strip()
                    if line.startswith('#') or line.startswith('.'):
                        continue  # Skip comment lines and directives
                    num_lines += 1
        except (FileNotFoundError, OSError):
            # print(f"Compilation of file {test.file_name} with compiler {compiler} failed.")
            return 0

        try:
            os.remove(s_dir)
        except OSError as e:
           pass

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
