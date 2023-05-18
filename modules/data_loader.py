from pathlib import Path
import re
import difflib
import os

from modules.test import Input, Test, Stats


_PATTERN_EXEC = r"int\s+main\s*\("
_PATTERN_CONSTANTS_LOCAL_DEF = r"^\s+(?P<type>int|float|double|char|long|short)(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?(?:,|;))+)"
_PATTERN_CONSTANTS_LOCAL_ASS = r"^\s+(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_DEF = r"^(:?\w+\b(?<!\btypedef)\s+)?(?P<type>int|float|double|char|long|short)(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_ASS = r"^(?P<seq>(?:\s+(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_SEQ = r"(?P<initial_space>\s*)(?P<input>(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*(?P<value>.*)\s*)?)(?P<has_next>,|;)(?P<final_space>\s*)"
_POSSIBLE_MATCHES = [(re.compile(pattern), is_global, is_declared)  for pattern, is_global, is_declared in ((_PATTERN_CONSTANTS_LOCAL_DEF, 1, 1), (_PATTERN_CONSTANTS_LOCAL_ASS, 1, 0), (_PATTERN_CONSTANTS_GLOBAL_DEF, 0, 1), (_PATTERN_CONSTANTS_GLOBAL_ASS, 0, 0))]
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
            in_struct = False
            while original_line := f.readline():
                match_line = None
                
                if  re.compile(r".*struct.*").match(original_line) :
                    in_struct = True
                if  re.compile(r"^}.*").match(original_line) and in_struct:
                    in_struct = False
                

                for pattern, scope, is_declared  in _POSSIBLE_MATCHES:
                    if not in_struct and (match_line  := pattern.match(original_line)) :
                        processed_line = original_line
                        for i, match in enumerate(r_global_seq.finditer(match_line.group('seq')), start=len(inputs)):
                            inputs[i] =  Input(
                                                name=match.group('name'), 
                                                type=(match_line.group('type') if not match.group('is_array')  else match_line.group('type')) if match_line.groupdict().get('type') else None, 
                                                value=match.group('value') if match.group('value') else ("0" if not match.group('is_array')  else "{ 0 }"), 
                                                len=(int(match.group('size')) if match.group('size') is not None and  match.group('size') != '' else None) if match.group('is_array') else None, 
                                                scope=scope,
                                                is_declared=is_declared
                                            ) 
                            processed_line = re.sub(_PATTERN_CONSTANTS_GLOBAL_SEQ, rf"\g<initial_space>[INPUT_{i}]\g<has_next>\g<final_space>", processed_line, count=1)
                        
                        processed_file += processed_line
                        break
                    
                if not match_line:
                    processed_file += original_line
                    
        return Test(name=str(file), file_pattern=processed_file, inputs=inputs)
    
    def save_results(self, results: list[Stats], args):
        """Save the results of the interesting tests to a file."""
        
        for s in results:
            with open(s.file_path, "r") as f:
                file_c = f.read()
            diff = difflib.ndiff(s.file_content.splitlines(keepends=True), file_c.splitlines(keepends=True))

            output_dir = os.path.join("data", os.path.splitext(s.file_name)[0]) + ".txt"
            while os.path.isfile(output_dir):
                output_dir += "_"
            
            csv_line = f"{s.file_name},{args.compiler},{s.max_rateo[1]},{s.compiler_stats['last']},{s.compiler_stats[s.max_rateo[1]]},{s.max_rateo[0]}\n"
            with open(output_dir, "w") as f:
                f.writelines(csv_line)
                f.writelines(diff)