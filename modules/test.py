from dataclasses import dataclass
from pathlib import Path

@dataclass
class Test:
    """Test object."""
    
    file: Path 
    """Test file path."""
    
    inputs: dict
    """Input values for the test."""
