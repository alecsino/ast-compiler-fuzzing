from pathlib import Path
import re
import difflib
import os

from modules.test import Input, Test, Stats


_PATTERN_EXEC = r"int\s+main\s*\("
_VALUE_PATTERN  = r"(?P<value>(\".*\"|{.*}|[0-9]+.?[0-9]*))\s*)"
_PATTERN_CONSTANTS_LOCAL_DEF = fr"^\s+(?P<type>int|float|double|char|long|short)(?P<seq>(?:\s+(?P<is_pointer>\*)?(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*{_VALUE_PATTERN}?(?:,|;))+)"
_PATTERN_CONSTANTS_LOCAL_ASS = rf"^\s+(?P<seq>(?:\s+(?P<is_pointer>\*)?(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*{_VALUE_PATTERN}?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_DEF = rf"^(:?\w+\b(?<!\btypedef)\s+)?(?P<type>int|float|double|char|long|short)(?P<seq>(?:\s+(?P<is_pointer>\*)?(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*{_VALUE_PATTERN}?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_ASS = rf"^(?P<seq>(?:\s+(?P<is_pointer>\*)?(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*{_VALUE_PATTERN}?(?:,|;))+)"
_PATTERN_CONSTANTS_GLOBAL_SEQ = rf"(?P<initial_space>\s*)(?P<input>(?P<is_pointer>\*)?(?P<name>\w+)(?P<is_array>\[(?P<size>[0-9]*)\])?\s*(?:=\s*{_VALUE_PATTERN}?)(?P<has_next>,|;)(?P<final_space>\s*)"
_POSSIBLE_MATCHES = [(re.compile(pattern), is_global, is_declared)  for pattern, is_global, is_declared in ((_PATTERN_CONSTANTS_LOCAL_DEF, 1, 1), (_PATTERN_CONSTANTS_LOCAL_ASS, 1, 0), (_PATTERN_CONSTANTS_GLOBAL_DEF, 0, 1), (_PATTERN_CONSTANTS_GLOBAL_ASS, 0, 0))]
_FILE_EXTENSION = '**/*.[c cpp]'


class DataLoader:
    """Class for importing and preprocessing tests."""
    
    def __init__(self, args):
        # Constructor code goes here
        self.args = args
        pass
    
    def tests(self) -> list[Test]:
        """Collect the processed tests from the given directory.

        Returns:
            list[Tests]: list of processed tests.
        """        
        
        directory = self.args.data
        print(f"Analyzing tests in {directory}")
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

        if len(file_contents.splitlines()) > 200:
            return False

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
            in_union = False
            n_input = 0
            while original_line := f.readline():
                match_line = None
                
                # ------------ skip structs and unions ------------ #
                if  re.compile(r".*struct.*").match(original_line) :
                    in_struct = True
                if  re.compile(r"^}.*").match(original_line) and in_struct:
                    in_struct = False
                
                if  re.compile(r".*union.*").match(original_line) :
                    in_union = True
                if  re.compile(r"^}.*").match(original_line) and in_struct:
                    in_union = False
                

                for pattern, scope, is_declared  in _POSSIBLE_MATCHES:
                    if not in_struct and not in_union and (match_line  := pattern.match(original_line)) :
                        processed_line = original_line
                        
                        for match in r_global_seq.finditer(match_line.group('seq')):
                            
                            # ----- skip pointers ----- #
                            if match.group('is_pointer'):
                                continue
                            
                            inputs[n_input] =  Input(
                                                name=match.group('name'), 
                                                type=(match_line.group('type') if not match.group('is_array')  else match_line.group('type')) if match_line.groupdict().get('type') else None, 
                                                value=match.group('value') if match.group('value') else ("0" if not match.group('is_array')  else "{ 0 }"), 
                                                len=(int(match.group('size')) if match.group('size') is not None and  match.group('size') != '' else None) if match.group('is_array') else None, 
                                                scope=scope,
                                                is_declared=is_declared
                                            ) 
                            processed_line = re.sub(_PATTERN_CONSTANTS_GLOBAL_SEQ, rf"\g<initial_space>[INPUT_{n_input}]\g<has_next>\g<final_space>", processed_line, count=1)
                            n_input += 1
                            
                        processed_file += processed_line
                        break
                    
                if not match_line:
                    processed_file += original_line
                    
        return Test(name=str(file), file_pattern=processed_file, inputs=inputs)
    
    def save_results(self, s: Stats):
        """Save the results of the interesting tests to a file."""

        with open(s.file_path, "r") as f:
            file_c = f.read()
        diff = difflib.ndiff(s.file_content.splitlines(keepends=True), file_c.splitlines(keepends=True))

        output_dir = os.path.join("data", os.path.splitext(s.file_name)[0]) + ".txt"
        while os.path.isfile(output_dir):
            output_dir += "_"
        
        csv_line = f"{s.file_name},{self.args.compiler},{s.max_rateo[1]},{s.compiler_stats['last']},{s.compiler_stats[s.max_rateo[1]]},{s.max_rateo[0]},{'ASAN tested' if s.asan_tested else 'ASAN could not be tested'}\n"
        with open(output_dir, "w") as f:
            f.writelines(csv_line)
            f.writelines(diff)