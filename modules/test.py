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
    
    def __eq__(self, __o: object) -> bool:
        return type(__o) == Input and self.name == __o.name and self.value == __o.value and self.type == __o.type and self.len == __o.len
    
    def infer_type():
        """Infer type if not available."""
    
    def infer_len():
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
