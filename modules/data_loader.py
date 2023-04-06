from pathlib import Path
import re

from modules.test import Test


_PATTERN = r"int\s+main\s*\("
_FILE_EXTENSION = '**/*.[c cpp]'



class DataLoader:
    """Class for importing and preprocessing tests."""
    
    def __init__(self):
        # Constructor code goes here
        pass
    
    def tests(self, directory: str = "./tests") -> list[Test]:
        """Collect the processed tests from the given directory.

        Args:
            directory (str, optional): directory of tests. Defaults to "./tests".

        Returns:
            list[Tests]: list of processed tests.
        """        

        test_directory = Path(directory)
        executable_tests = [test_file for test_file in test_directory.glob(_FILE_EXTENSION) if self._is_executable(test_file)]
        tests = [self._promote_constants_to_variables(test_file) for test_file in  executable_tests]
        return tests
    
    def _is_executable(self, file: Path) -> bool:
        """Check if the file is executable.

        Args:
            file (Path): path to the file.

        Returns:
            bool: whether the file is executable.
        """        
        
        with file.open(encoding="ISO-8859-1", errors='ignore') as f:
            file_contents = f.read()
        match = re.search(_PATTERN, file_contents)
        return True if match else False
    
    def _promote_constants_to_variables(self, file: Path) -> Test:
        """Promote constants to variables in the given file.

        Args:
            file (Path): path to the file.
            to_directory (str): directory to save the modified file.

        Returns:
            Test: the processed test.
        """       
        # modify the file to promote constants to variables and save it to a new file
        return Test(file=file, inputs={})
    
