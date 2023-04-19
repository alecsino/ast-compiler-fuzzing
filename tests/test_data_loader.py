from pathlib import Path
import pytest
from modules.data_loader import DataLoader
from modules.test import Input

_TEST_PATH_NON_EXECUTABLE = "tests/inputs/test_without_main.c"
_TEST_PATH_NON_GLOBAL = "tests/inputs/test_non_global_constant.c"
_TEST_PATH_GLOBAL = "tests/inputs/test_global_constant.c"

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
    assert data_loader._promote_constants_to_variables(Path(_TEST_PATH_GLOBAL)).inputs == {
                                                                                           0: Input(name='a', value="0", type='int'),
                                                                                           1: Input(name='b', value="0", type='int'), 
                                                                                           2: Input(name='d', value="0", type='int'), 
                                                                                           3: Input(name='c', value="10", type='short'), 
                                                                                           4: Input(name='array', value="{1, 2, 4}", type=list['int'], len="10"),
                                                                                           5: Input(name='string', value='"1023939"', type=list['char'], len="Infer from object")
                                                                                           }
    
    assert data_loader._promote_constants_to_variables(Path(_TEST_PATH_NON_GLOBAL)).inputs == {
                                                                                           0: Input(name='a', value="0", type='int'),
                                                                                           1: Input(name='b', value="0", type='int'), 
                                                                                           2: Input(name='c', value="10", type='short'), 
                                                                                           3: Input(name='array', value="{1, 2, 4}", type=list['int'], len="3"),
                                                                                           4: Input(name='string', value='"1023939"', type=list['char'], len="Infer from object"),
                                                                                           5: Input(name='a', value='1', type=None)
                                                                                           }

    
    