from pathlib import Path
import re

from modules.test import Test


_PATTERN = r"int\s+main\s*\("
_FILE_EXTENSION = '**/*.[c cpp]'



class DataLoader:
    """Importer class for importing tests and preprocessing files."""
    
    def __init__(self):
        # Constructor code goes here
        pass
    
    def tests(self, directory: str = "./tests") -> str:
        """Retrieve processed tests files from the directory."""

        test_directory = Path(directory)
        executable_tests = [test_file for test_file in test_directory.glob(_FILE_EXTENSION) if self.is_executable(test_file)]
        tests = [self.promote_constants_to_variables(test_file) for test_file in  executable_tests]
        return tests
    
    def is_executable(self, file: Path) -> str:
        """Check whether the test case is executable or not."""
        
        with file.open(encoding="ISO-8859-1", errors='ignore') as f:
            file_contents = f.read()
        match = re.search(_PATTERN, file_contents)
        return True if match else False
    
    def promote_constants_to_variables(self, file: Path) -> str:
        """Promote constants to variables in the test file."""
        
        # modify the file to promote constants to variables and save it to a new file
        return Test(file=file, inputs={})
    
    