from pathlib import Path
import re

from modules.test import Input, Test


_PATTERN_EXEC = r"int\s+main\s*\("
_PATTERN_CONSTANTS_LOCAL_DEF = r"^\s+(?P<type>int|float|double|char|long|short)(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?(?:,|;))+)"
_PATTERN_CONSTANTS_LOCAL_ASS = r"^\s+(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_DEF = r"^(:?\w+\s+)?(?P<type>int|float|double|char|long|short)(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_ASS = r"^(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_SEQ = r"(?P<initial_space>\s*)(?P<input>(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?)(?P<has_next>,|;)(?P<final_space>\s*)"
_POSSIBLE_MATCHES = [re.compile(pattern) for pattern in (_PATTERN_CONSTANTS_LOCAL_DEF, _PATTERN_CONSTANTS_LOCAL_ASS, _PATTERN_CONSTANTS_GLOBAL_DEF, _PATTERN_CONSTANTS_GLOBAL_ASS)]
_FILE_EXTENSION = '**/*.[c cpp]'


class DataLoader:
    """Class for importing and preprocessing tests."""
    
    def __init__(self):
        # Constructor code goes here
        pass
    
    def tests(self, directory: str = "./tests_files") -> list[Test]:
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
        match = re.search(_PATTERN_EXEC, file_contents)
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
              
        r_global_seq = re.compile(_PATTERN_CONSTANTS_GLOBAL_SEQ, re.MULTILINE)
        
        inputs = {}
        processed_file = ""
        
        with file.open(encoding="ISO-8859-1", errors='ignore') as f:
            while original_line := f.readline():
                match_line = None
                for pattern  in _POSSIBLE_MATCHES:
                    
                    if match_line  := pattern.match(original_line) :
                        processed_line = original_line
                        
                        for i, match in enumerate(r_global_seq.finditer(match_line.group('seq')), start=len(inputs)):
                            inputs[i] =  Input(name=match.group('name'), 
                                                type=(match_line.group('type') if not match.group('is_array')  else list[match_line.group('type')]) if match_line.groupdict().get('type') else None, 
                                                value=match.group('value') if match.group('value') else "0", 
                                                len=match.group('size') if match.group('size') else "Infer from object" if match.group('is_array') else None, 
                                                ) 
                            processed_line = re.sub(_PATTERN_CONSTANTS_GLOBAL_SEQ, rf"\g<initial_space>[INPUT_{i}]\g<has_next>\g<final_space>", processed_line, count=1)
                        
                        processed_file += processed_line
                        break
                    
                if not match_line:
                    processed_file += original_line
                    
        return Test(name=str(file), file=processed_file, inputs=inputs)
    
