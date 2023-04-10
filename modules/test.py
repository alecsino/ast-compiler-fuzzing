from dataclasses import dataclass
from typing import Any

@dataclass
class Input:
    """Input object."""
    
    name : str
    """Name of the variable."""
    
    value : Any
    """Original valye of the variable."""
    
    type: Any
    """Type of the variable, if available."""
    
    len : int = None
    """Length of the variable, if array or string and available, else None."""
    
    def __post_init__(self):
        self.type = self._infer_type()
        self.len = self._infer_len()
        
    def __eq__(self, __o: object) -> bool:
        return type(__o) == Input and self.name == __o.name and self.value == __o.value and self.type == __o.type and self.len == __o.len
    
    def _infer_type(self):
        """Infer type if not available."""
    
    def _infer_len(self):
        """Infer length if not available and is array or string."""
        
        
@dataclass
class Test:
    """Test object."""
    
    name: str 
    """Test file path."""
    
    file: bytes 
    """Test file content."""
    
    inputs: dict[int, Input]
    """Input values for the test."""
