""" Test to ensure Config works as expected
"""

from config import Config

CONFIG = Config('tests/config/test.cfg')


def test_config():
    """ Test using test.cfg to ensure key-value pairs are set correctly
    """

    assert CONFIG.value('variable_number_one') == 'variable number one'
    assert CONFIG.value('variable_number_two') == '2'
    assert CONFIG.value('variable_number_three') == 'number = 3'

    assert len(CONFIG.value('variable_with_array')) == 3
    for i in range(len(CONFIG.value('variable_with_array'))):
        assert  CONFIG.value('variable_with_array')[i] == ['value 1', 'value 2', 'Value 3'][i]


def test_set_config():
    """ Test to ensure it is possible to set key-value pair
    """

    CONFIG.set('my_key', 'my_value')
    assert CONFIG.value('my_key') == 'my_value'
