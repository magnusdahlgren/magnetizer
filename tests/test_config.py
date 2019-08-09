import pytest
from config import *

config = Config('../tests/config/test.cfg')


def test_basic_config():

    assert config.value('variable_number_one') == 'variable number one'
    assert config.value('variable_number_two') == '2'
    assert config.value('variable_number_three') == 'number = 3'

def test_array_in_config():

    expected = ['value 1','value 2', 'Value 3']

    assert len(config.value('variable_with_array')) == len(expected)

    for i in range(len(config.value('variable_with_array'))):
        assert  config.value('variable_with_array')[i] == expected[i]


@pytest.mark.skip(reason="Not sure how to test exceptions")
def test_exception_when_key_undefined():

    assert False

    # todo: check for key error