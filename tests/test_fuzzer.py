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
        fuzzer (Fuzzer): the fuzzer
    """

    test = Test(
        file_pattern="""int [INPUT_0], [INPUT_1], [INPUT_2];\nvolatile short [INPUT_3];\nint [INPUT_4];\nchar [INPUT_5];\n\n\n\nint main() {\n    [INPUT_6];\n    return c;\n}""",
        name="",
        inputs={},
    )
    assert fuzzer.mutate(test,  {
                    0: Input(name='a', value="0", type='int', scope=0, len=None, is_declared=True),
                    1: Input(name='b', value="0", type='int', scope=0, len=None, is_declared=True), 
                    2: Input(name='d', value="0", type='int', scope=0, len=None, is_declared=True), 
                    3: Input(name='c', value="10", type='short', scope=0, len=None, is_declared=True), 
                    4: Input(name='array', value="{1, 2, 4}", type='int', len=10, scope=0, is_declared=True),
                    5: Input(name='string', value='"1023939"', type='char', len=8, scope=0, is_declared=True),
                    6: Input(name='array', value='3', type='int', len=2, scope=1, is_declared=False),
                    }) == """int a = 0, b = 0, d = 0;\nvolatile short c = 10;\nint array[10] = {1, 2, 4};\nchar string[8] = "1023939";\n\n\n\nint main() {\n    array[2] = 3;\n    return c;\n}"""
    
    