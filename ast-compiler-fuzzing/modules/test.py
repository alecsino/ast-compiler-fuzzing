import dataclasses
import platform
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

    interesting: bool = True
    
    
    def __post_init__(self):
        self.len = self._infer_len()
        
    def __eq__(self, __o: object) -> bool:
        return type(__o) == Input and dataclasses.asdict(self) == dataclasses.asdict(__o)
    
    def _infer_len(self):
        """Infer length if not available and is array or string."""
        if self.len != None:
            return self.len
        if is_array := re.match(r"{(?P<content>.*)}", self.value):
            return len(is_array.group('content').split(","))
        if is_string := re.match(r"\"(?P<content>.*)\"", self.value):
            return len(is_string.group('content')) + 1
        

@dataclasses.dataclass(frozen=True)
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
    
    def has_valid_inputs(self) -> bool:
        """Whether the input is valid for the test."""
        
        return len(self.inputs) > 0 and len([input for input in self.inputs.values() if not input.type]) == 0

@dataclasses.dataclass
class Stats:

    file_path: str
    """Full path of the file."""

    file_name: str
    """Name of the file."""

    file_content: str 
    """Test file content."""

    compiler_stats: dict[str, int] = None
    """Stats of the compiler.
    The key 'last' contain the stats of the current compiler.
    The other keys are expected in the form '<compiler>-<version>'.
    """

    asan_tested: bool = False
    """Whether the test has been tested with asan."""

    max_rateo: tuple[float, str] = (0, "")
    """The max rateo with respect to an older version."""
    
    strategy_mutation: str = "Not mutated"
    """The strategy used to mutate the test."""
    
    error_message: str | None = None
    """Asan error message, if any."""
    

    def add_compiler_stat(self, compiler: str, stat: int):
        """Add a stat to the compiler stats.

        Arguments:
            compiler {str} -- The compiler to add the stat to.
            stat {int} -- The stat to add.
        """
        if self.compiler_stats is None:
            self.compiler_stats = {}
            
        self.compiler_stats[compiler] = stat

    @property
    def n_tests(self):
        """Returns the number of tests."""
        return len(self.compiler_stats)

    def set_max(self):
        """Whether the ratio with respect to an older version is greater than 1.

        Args:
            stats (dict[str, Any]): the stats of the test

        Returns:
            bool: whether the test is interesting
        """

        if "last" not in self.compiler_stats:
            self.max_rateo = (0, "")
            return
        
        if len(self.compiler_stats) <= 1:
            self.max_rateo = (0, "")
            return
        
        
        min_v = min([value for key, value in self.compiler_stats.items() if not key.startswith("last")])
        
        #search for min_v key in compiler_stats
        for key, value in self.compiler_stats.items():
            if key == "last":
                continue
            if value == min_v:
                self.max_rateo = (round(self.compiler_stats["last"] / min_v, 2), key)
                break
    
    def is_interesting(self):
        """Whether the ratio with respect to an older version is greater than the interesting threshold."""
        
        return True if self.max_rateo[0] > 1.50 else False

@dataclasses.dataclass
class FuzzedTest:
    """The fuzzed test object."""
    
    test: Test
    """Test object."""
    
    stats: Stats | None
    """Stats of the fuzzed test. If None, the test has not been compiled yet."""
    
    mutated_inputs: dict[int, Input]
    """The mutated inputs of the test."""
    
    def is_asan_safe(self, compiler) -> bool:
        #if aarch64 always return true since asan is not supported
        # if platform.machine() == "aarch64" or platform.machine() == "arm64":
        #     self.stats.asan_tested = False
        #     return True
        
        return compiler.is_asan_safe(self.stats, "last") and compiler.is_asan_safe(self.stats, self.stats.max_rateo[1])
        

    def has_improved(self, old_stats: Stats) -> bool:
        """Whether the fuzzed test is improved with respect to the previous mutation.

        Returns:
            bool: whether the test has improved
        """
        
        if old_stats is None:
            return True
        
        return self.stats.max_rateo[0] >= old_stats.max_rateo[0]