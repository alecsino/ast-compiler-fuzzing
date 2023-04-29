from pathlib import Path
import dataclasses
import pytest
from modules.data_loader import DataLoader
from modules.test import Input, Test

_TEST_PATH_NON_EXECUTABLE = "tests/inputs/test_without_main.c"
_TEST_PATH_NON_GLOBAL = "tests/inputs/test_non_global_constant.c"
_TEST_PATH_GLOBAL = "tests/inputs/test_global_constant.c"

_INPUTS_GLOBAL =  {
                    0: dict(name='a', value="0", type='int', scope=0, len=None, is_declared=True),
                    1: dict(name='b', value="0", type='int', scope=0, len=None, is_declared=True), 
                    2: dict(name='d', value="0", type='int', scope=0, len=None, is_declared=True), 
                    3: dict(name='c', value="10", type='short', scope=0, len=None, is_declared=True), 
                    4: dict(name='array', value="{1, 2, 4}", type='int', len=10, scope=0, is_declared=True),
                    5: dict(name='string', value='"1023939"', type='char', len=8, scope=0, is_declared=True)
                    }
_INPUTS_NON_GLOBAL = {
                    0: dict(name='a', value="0", type='int', scope=0, len=None, is_declared=True),
                    1: dict(name='b', value="0", type='int', scope=0, len=None, is_declared=True), 
                    2: dict(name='c', value="10", type='short', scope=0, len=None, is_declared=True), 
                    3: dict(name='array', value="{1, 2, 4}", type='int', len=3, scope=0, is_declared=True),
                    4: dict(name='string', value='"1023939"', type='char', len=8, scope=0, is_declared=True),
                    5: dict(name='a', value='1', type='int', scope=1, len=None, is_declared=False)
                    }
@pytest.fixture
def data_loader():
    """The dataloader.

    Returns:
        DataLoader: the data loader
    """
    return DataLoader()

def test__is_executable(data_loader):
    """Test executability check.

    Args:
        data_loader (DataLoader): the data loader
    """
    
    assert data_loader._is_executable(Path(_TEST_PATH_NON_EXECUTABLE)) == False
    assert data_loader._is_executable(Path(_TEST_PATH_GLOBAL)) == True
    assert data_loader._is_executable(Path(_TEST_PATH_GLOBAL)) == True
    
def test__promote_constants_to_variables(data_loader):
    """Test executability check.

    Args:
        data_loader (DataLoader): the data loader
    """
    for i, input in _INPUTS_GLOBAL.items():
        assert dataclasses.asdict(data_loader._promote_constants_to_variables(Path(_TEST_PATH_GLOBAL)).inputs[i]) == input
    
    assert data_loader._promote_constants_to_variables(Path(_TEST_PATH_GLOBAL)).file_pattern =="""int [INPUT_0], [INPUT_1], [INPUT_2];\nvolatile short [INPUT_3];\nint [INPUT_4];\nchar [INPUT_5];\n\n\n\nint main() {\n    return c;\n}"""
    
    for i, input in _INPUTS_NON_GLOBAL.items():
        assert dataclasses.asdict(data_loader._promote_constants_to_variables(Path(_TEST_PATH_NON_GLOBAL)).inputs[i]) == input
    
    assert data_loader._promote_constants_to_variables(Path(_TEST_PATH_NON_GLOBAL)).file_pattern =="""volatile int [INPUT_0], [INPUT_1];\nvolatile short [INPUT_2];\nint [INPUT_3];\nchar [INPUT_4];\n\n\n\nint main() {\n    [INPUT_5];\n    return c;\n}"""
    
