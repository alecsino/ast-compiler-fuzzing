import pytest
from modules.fuzzer import Fuzzer
from modules.test import Input, Test

@pytest.fixture
def fuzzer():
    """The fuzzer.

    Returns:
        Fuzzer: the data loader
    """
    return Fuzzer(tests=[], compiler=None, num_cores=0, n_threshold=0)

def test__mutate(fuzzer):
    """Test mutation.

    Args:
        data_loader (DataLoader): the data loader
    """

    test = Test(
        file_pattern="""int [INPUT_0], [INPUT_1], [INPUT_2];\nvolatile short [INPUT_3];\nint [INPUT_4];\nchar [INPUT_5];\n\n\n\nint main() {\n    return c;\n}""",
        name="",
        inputs={},
    )
    fuzzer.mutate(test,  {
                    0: Input(name='a', value="0", type='int', scope=0, len=None, is_declared=True),
                    1: Input(name='b', value="0", type='int', scope=0, len=None, is_declared=True), 
                    2: Input(name='d', value="0", type='int', scope=0, len=None, is_declared=True), 
                    3: Input(name='c', value="10", type='short', scope=0, len=None, is_declared=True), 
                    4: Input(name='array', value="{1, 2, 4}", type='int', len=10, scope=0, is_declared=True),
                    5: Input(name='string', value='"1023939"', type='char', len=8, scope=0, is_declared=True)
                    })
    
    