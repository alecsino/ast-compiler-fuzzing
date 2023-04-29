import dataclasses
from typing import Any
import re


@dataclasses.dataclass
class Input:
    """Input object."""
    
    name : str
    """Name of the variable."""
    
    value : Any
    """Original valye of the variable."""

    scope: int 
    """The scope of the variable. 1 if Local, 0 if global."""
    
    is_declared: bool 
    """Whether the variables is declared."""

    type: str | None
    """Type of the variable, if available."""
    
    len : int = None
    """Length of the variable, if array or string and available, else None."""
    
    
    def __post_init__(self):
        self.len = self._infer_len()
        
    def __eq__(self, __o: object) -> bool:
        return type(__o) == Input and dataclasses.asdict(self) == dataclasses.asdict(__o)
    
    def _infer_len(self):
        """Infer length if not available and is array or string."""
        if self.len:
            return self.len
        if is_array := re.match(r"{(?P<content>.*)}", self.value):
            return len(is_array.group('content').split(","))
        if is_string := re.match(r"\"(?P<content>.*)\"", self.value):
            return len(is_string.group('content')) + 1

@dataclasses.dataclass
class Test:
    """Test object."""
    
    name: str 
    """Test file path."""
    
    file_pattern: str
    """Test file pattern."""
    
    inputs: dict[int, Input]
    """Input values for the test."""


    def __post_init__(self):
        for i, input in self.inputs.items():
            if not input.type:
                for j in range(i-1, -1, -1):
                    input.type =  self.inputs[j].type if input.name == self.inputs[j].name and input.scope >=  self.inputs[j].scope else None
                    if input.type:
                        break
        

@dataclasses.dataclass
class Stats:

    file_path: str
    """Full path of the file."""

    file_name: str
    """Name of the file."""

    file_content: str 
    """Test file content."""

    compiler_stats: dict[str, int]
    """Stats of the compiler.
    The key 'last' contain the stats of the current compiler.
    The other keys are expected in the form '<compiler>-<version>'.
    """

    max_rateo: tuple[float, str]

    def __init__(self, file_path: str, file_name: str, file_content: str):
        """Initialize the stats.

        Arguments:
            file_path {str} -- Full path of the file.
            file_name {str} -- Name of the file.
        """
        self.file_path = file_path
        self.file_name = file_name
        self.file_content = file_content
        self.compiler_stats = {}
        self.max_rateo = (0, "")


    def add_compiler_stat(self, compiler: str, stat: int):
        """Add a stat to the compiler stats.

        Arguments:
            compiler {str} -- The compiler to add the stat to.
            stat {int} -- The stat to add.
        """
        self.compiler_stats[compiler] = stat

    def n_tests(self):
        """Returns the number of tests."""
        return len(self.compiler_stats)

    def is_interesting(self):
        """Whether the ratio with respect to an older version is greater than 1.

        Args:
            stats (dict[str, Any]): the stats of the test

        Returns:
            bool: whether the test is interesting
        """

        if "last" not in self.compiler_stats:
            return False
        
        min_v = min([value for key, value in self.compiler_stats.items() if not key.startswith("last")])
        
        #search for min_v key in compiler_stats
        for key, value in self.compiler_stats.items():
            if value == min_v:
                self.max_rateo = (round(self.compiler_stats["last"] / min_v, 2), key)
                break
        
        if self.max_rateo[0] > 1:
            return True
        return False
    

@dataclasses.dataclass
class FuzzedTest:
    """The fuzzed test object."""
    
    test: Test
    """Test object."""
    
    stats: Stats | None
    """Stats of the fuzzed test. If None, the test has not been compiled yet."""