import pytest
from config import *

def test_load_config_from_file():

    config = Config('../tests/config/test.cfg')

    assert config.config['variable_number_one'] == 'variable number one'
    assert config.config['variable_number_two'] == '2'
    assert config.config['variable_number_three'] == 'number = 3'
